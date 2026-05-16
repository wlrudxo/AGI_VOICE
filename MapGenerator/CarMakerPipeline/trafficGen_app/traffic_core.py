from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import heapq
import json
from pathlib import Path
import math
import re
import shutil
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent
DEFAULT_ROADGEN_EXPORTS = ROOT.parent / "roadGen_app" / "exports"
LANE_CHANGE_COST_M = 120.0


@dataclass(frozen=True)
class RoadFiles:
    folder: Path
    graph: Path | None
    net: Path
    xodr: Path | None
    edge_xml: Path | None
    node_xml: Path | None


@dataclass
class Lane:
    id: str
    edge_id: str
    index: int
    speed: float
    length: float
    shape: list[tuple[float, float]]
    internal: bool = False


@dataclass
class SumoEdge:
    id: str
    from_node: str | None
    to_node: str | None
    internal: bool
    lanes: list[str] = field(default_factory=list)


@dataclass
class Connection:
    from_edge: str
    to_edge: str
    from_lane: int
    to_lane: int
    via: str | None
    direction: str
    state: str

    @property
    def is_uturn(self) -> bool:
        return self.direction == "t"


@dataclass
class LaneStep:
    lane_id: str
    edge_id: str
    lane_index: int
    internal: bool
    length: float
    speed: float
    xodr_road_id: str | None = None
    xodr_lane_id: str | None = None


@dataclass
class PlannedRoute:
    name: str
    start_lane: str
    goal_lane: str
    lane_path: list[str]
    steps: list[LaneStep]

    @property
    def total_length(self) -> float:
        total = 0.0
        previous: LaneStep | None = None
        for step in self.steps:
            is_same_edge_lane_change = (
                previous is not None
                and previous.edge_id == step.edge_id
                and previous.lane_index != step.lane_index
                and previous.internal == step.internal
            )
            if not is_same_edge_lane_change:
                total += step.length
            previous = step
        return total

    def has_same_edge_lane_change(self) -> bool:
        previous: LaneStep | None = None
        for step in self.steps:
            if (
                previous is not None
                and previous.edge_id == step.edge_id
                and previous.lane_index != step.lane_index
                and previous.internal == step.internal
            ):
                return True
            previous = step
        return False

    def is_same_edge_lane_change_only(self) -> bool:
        road_steps = [step for step in self.steps if not step.internal]
        if len(road_steps) < 2 or not self.has_same_edge_lane_change():
            return False
        return len({step.edge_id for step in road_steps}) == 1


@dataclass
class VehiclePlan:
    name: str
    route_name: str
    model: str
    driver_model: str
    speed_kmh: float
    start_s: float
    lane_offset: float
    start_delay_s: float = 0.0
    control_mode: str = "ipg_driver"


class RoadPackageError(RuntimeError):
    pass


def safe_name(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())
    cleaned = cleaned.strip("._")
    return cleaned or "traffic_plan"


def find_latest_roadgen_export() -> Path | None:
    if not DEFAULT_ROADGEN_EXPORTS.exists():
        return None
    folders = [path for path in DEFAULT_ROADGEN_EXPORTS.iterdir() if path.is_dir()]
    if not folders:
        return None
    return max(folders, key=lambda path: path.stat().st_mtime)


def discover_road_files(folder: Path) -> RoadFiles:
    folder = folder.resolve()
    if not folder.exists() or not folder.is_dir():
        raise RoadPackageError(f"Folder does not exist: {folder}")

    graph = folder / "graph.json"
    graph = graph if graph.exists() else None

    nets = sorted(folder.glob("*.net.xml"))
    if not nets:
        raise RoadPackageError("No .net.xml file was found in the selected folder.")

    xodrs = sorted(folder.glob("*.xodr"))
    edge_xml = folder / "edge.xml"
    node_xml = folder / "node.xml"

    return RoadFiles(
        folder=folder,
        graph=graph,
        net=nets[0],
        xodr=xodrs[0] if xodrs else None,
        edge_xml=edge_xml if edge_xml.exists() else None,
        node_xml=node_xml if node_xml.exists() else None,
    )


def parse_shape(value: str | None) -> list[tuple[float, float]]:
    if not value:
        return []
    points: list[tuple[float, float]] = []
    for token in value.split():
        parts = token.split(",")
        if len(parts) != 2:
            continue
        try:
            points.append((float(parts[0]), float(parts[1])))
        except ValueError:
            continue
    return points


def lane_id_for(edge_id: str, lane_index: int) -> str:
    return f"{edge_id}_{lane_index}"


def edge_id_from_lane(lane_id: str) -> str:
    if lane_id.startswith(":"):
        parts = lane_id.rsplit("_", 1)
        return parts[0] if len(parts) == 2 else lane_id
    parts = lane_id.rsplit("_", 1)
    return parts[0] if len(parts) == 2 else lane_id


def parse_graph(path: Path | None) -> dict:
    if path is None:
        return {"nodes": [], "edges": []}
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return {
        "nodes": data.get("nodes", []),
        "edges": data.get("edges", []),
    }


def xodr_lane_sort_key(value: str) -> tuple[int, int]:
    try:
        lane_number = int(value)
    except ValueError:
        return (2, 999)
    if lane_number < 0:
        return (0, lane_number)
    return (1, lane_number)


def parse_net(path: Path) -> tuple[dict[str, SumoEdge], dict[str, Lane], list[Connection]]:
    tree = ET.parse(path)
    root = tree.getroot()

    edges: dict[str, SumoEdge] = {}
    lanes: dict[str, Lane] = {}
    connections: list[Connection] = []

    for edge_el in root.findall("edge"):
        edge_id = edge_el.get("id") or ""
        internal = edge_el.get("function") == "internal" or edge_id.startswith(":")
        edge = SumoEdge(
            id=edge_id,
            from_node=edge_el.get("from"),
            to_node=edge_el.get("to"),
            internal=internal,
        )
        for lane_el in edge_el.findall("lane"):
            lane_id = lane_el.get("id") or lane_id_for(edge_id, int(lane_el.get("index") or 0))
            try:
                lane_index = int(lane_el.get("index") or 0)
            except ValueError:
                lane_index = 0
            try:
                speed = float(lane_el.get("speed") or 0.0)
            except ValueError:
                speed = 0.0
            try:
                length = float(lane_el.get("length") or 0.0)
            except ValueError:
                length = 0.0

            lanes[lane_id] = Lane(
                id=lane_id,
                edge_id=edge_id,
                index=lane_index,
                speed=speed,
                length=length,
                shape=parse_shape(lane_el.get("shape")),
                internal=internal,
            )
            edge.lanes.append(lane_id)
        edges[edge_id] = edge

    for conn_el in root.findall("connection"):
        try:
            from_lane = int(conn_el.get("fromLane") or 0)
            to_lane = int(conn_el.get("toLane") or 0)
        except ValueError:
            continue
        connections.append(
            Connection(
                from_edge=conn_el.get("from") or "",
                to_edge=conn_el.get("to") or "",
                from_lane=from_lane,
                to_lane=to_lane,
                via=conn_el.get("via") or None,
                direction=conn_el.get("dir") or "",
                state=conn_el.get("state") or "",
            )
        )

    return edges, lanes, connections


def parse_xodr_lane_map(path: Path | None, edges: dict[str, SumoEdge]) -> dict[str, tuple[str, str]]:
    if path is None or not path.exists():
        return {}

    tree = ET.parse(path)
    root = tree.getroot()

    junction_names: dict[str, str] = {}
    for junction_el in root.findall("junction"):
        junction_id = junction_el.get("id")
        name = junction_el.get("name")
        if junction_id is not None and name:
            junction_names[junction_id] = name

    road_by_name: dict[str, ET.Element] = {}
    road_by_nodes: dict[tuple[str, str], ET.Element] = {}

    for road_el in root.findall("road"):
        road_name = road_el.get("name") or ""
        road_id = road_el.get("id")
        if not road_id:
            continue
        if road_name:
            road_by_name[road_name] = road_el

        link = road_el.find("link")
        if link is None:
            continue
        predecessor = link.find("predecessor")
        successor = link.find("successor")
        if predecessor is None or successor is None:
            continue
        if predecessor.get("elementType") != "junction" or successor.get("elementType") != "junction":
            continue
        from_name = junction_names.get(predecessor.get("elementId") or "")
        to_name = junction_names.get(successor.get("elementId") or "")
        if from_name and to_name:
            road_by_nodes[(from_name, to_name)] = road_el

    mapping: dict[str, tuple[str, str]] = {}
    for edge in edges.values():
        road_el = road_by_name.get(edge.id)
        if road_el is None and edge.from_node and edge.to_node:
            road_el = road_by_nodes.get((edge.from_node, edge.to_node))
        if road_el is None:
            continue

        road_id = road_el.get("id")
        if road_id is None:
            continue
        lane_ids = [
            lane_el.get("id")
            for lane_el in road_el.findall(".//lane")
            if lane_el.get("id") and lane_el.get("id") != "0"
        ]
        lane_ids = sorted(set(lane_ids), key=xodr_lane_sort_key)
        if not lane_ids:
            continue

        for lane_id in edge.lanes:
            lane = lane_id.rsplit("_", 1)[-1]
            try:
                lane_index = int(lane)
            except ValueError:
                lane_index = 0
            xodr_lane = lane_ids[min(lane_index, len(lane_ids) - 1)]
            mapping[lane_id] = (road_id, xodr_lane)

    return mapping


class RoadPackage:
    def __init__(self, files: RoadFiles) -> None:
        self.files = files
        self.graph = parse_graph(files.graph)
        self.edges, self.lanes, self.connections = parse_net(files.net)
        self.xodr_lane_map = parse_xodr_lane_map(files.xodr, self.edges)

    @classmethod
    def load(cls, folder: Path) -> "RoadPackage":
        return cls(discover_road_files(folder))

    @property
    def external_lanes(self) -> list[str]:
        return sorted(lane_id for lane_id, lane in self.lanes.items() if not lane.internal)

    @property
    def internal_lanes(self) -> list[str]:
        return sorted(lane_id for lane_id, lane in self.lanes.items() if lane.internal)

    def build_lane_graph(self, include_uturns: bool = False, allow_lane_changes: bool = False) -> dict[str, list[str]]:
        graph: dict[str, list[str]] = {lane_id: [] for lane_id in self.lanes}
        internal_continuations = {
            (connection.from_edge, connection.to_edge)
            for connection in self.connections
            if self.edges.get(connection.from_edge, SumoEdge("", None, None, False)).internal
        }

        def add_edge(source: str, target: str) -> None:
            if source not in self.lanes or target not in self.lanes:
                return
            if target not in graph[source]:
                graph[source].append(target)

        for connection in self.connections:
            if connection.is_uturn and not include_uturns:
                continue
            source = lane_id_for(connection.from_edge, connection.from_lane)
            target = lane_id_for(connection.to_edge, connection.to_lane)
            if connection.via:
                add_edge(source, connection.via)
                via_edge = edge_id_from_lane(connection.via)
                if (via_edge, connection.to_edge) not in internal_continuations:
                    add_edge(connection.via, target)
            else:
                add_edge(source, target)

        if allow_lane_changes:
            for edge in self.edges.values():
                if edge.internal:
                    continue
                lanes = sorted(
                    (self.lanes[lane_id] for lane_id in edge.lanes if lane_id in self.lanes),
                    key=lambda lane: lane.index,
                )
                for left, right in zip(lanes, lanes[1:]):
                    add_edge(left.id, right.id)
                    add_edge(right.id, left.id)

        for targets in graph.values():
            targets.sort()
        return graph

    def transition_cost(self, source: str, target: str) -> float:
        source_lane = self.lanes[source]
        target_lane = self.lanes[target]
        if source_lane.edge_id == target_lane.edge_id and source_lane.index != target_lane.index:
            return LANE_CHANGE_COST_M + abs(source_lane.index - target_lane.index)
        return max(target_lane.length, 1.0)

    def shortest_lane_path(self, start_lane: str, goal_lane: str, graph: dict[str, list[str]]) -> list[str]:
        return self.shortest_lane_path_between([start_lane], [goal_lane], graph)

    def shortest_lane_path_between(self, start_lanes: list[str], goal_lanes: list[str], graph: dict[str, list[str]]) -> list[str]:
        goal_set = set(goal_lanes)
        distances: dict[str, float] = {}
        parents: dict[str, str | None] = {}
        queue: list[tuple[float, str]] = []
        for lane_id in start_lanes:
            distances[lane_id] = 0.0
            parents[lane_id] = None
            heapq.heappush(queue, (0.0, lane_id))

        reached_goal: str | None = None

        while queue:
            distance, current = heapq.heappop(queue)
            if distance > distances.get(current, math.inf):
                continue
            if current in goal_set:
                reached_goal = current
                break
            for target in graph.get(current, []):
                new_distance = distance + self.transition_cost(current, target)
                if new_distance >= distances.get(target, math.inf):
                    continue
                distances[target] = new_distance
                parents[target] = current
                heapq.heappush(queue, (new_distance, target))

        if reached_goal is None:
            raise RoadPackageError(f"No lane-level route from {', '.join(start_lanes)} to {', '.join(goal_lanes)}.")

        lane_path: list[str] = []
        current: str | None = reached_goal
        while current is not None:
            lane_path.append(current)
            current = parents[current]
        lane_path.reverse()
        return lane_path

    def checkpoint_candidates(self, token: str) -> list[str]:
        token = token.strip()
        if token in self.lanes:
            return [token]

        node_ids = {
            node_id
            for edge in self.edges.values()
            for node_id in [edge.from_node, edge.to_node]
            if node_id
        }
        if token not in node_ids:
            raise RoadPackageError(f"Unknown lane or node checkpoint: {token}")

        outgoing = [
            lane_id
            for edge in self.edges.values()
            if not edge.internal and edge.from_node == token
            for lane_id in edge.lanes
            if lane_id in self.lanes
        ]
        if outgoing:
            return sorted(outgoing)

        incoming = [
            lane_id
            for edge in self.edges.values()
            if not edge.internal and edge.to_node == token
            for lane_id in edge.lanes
            if lane_id in self.lanes
        ]
        if incoming:
            return sorted(incoming)
        raise RoadPackageError(f"Node checkpoint has no usable lanes: {token}")

    def plan_route(
        self,
        start_lane: str,
        goal_lane: str,
        include_uturns: bool = False,
        allow_lane_changes: bool = False,
    ) -> PlannedRoute:
        return self.plan_route_via(
            [start_lane, goal_lane],
            include_uturns=include_uturns,
            allow_lane_changes=allow_lane_changes,
        )

    def plan_route_via(
        self,
        lane_ids: list[str],
        include_uturns: bool = False,
        allow_lane_changes: bool = False,
    ) -> PlannedRoute:
        clean_lanes = [lane_id.strip() for lane_id in lane_ids if lane_id.strip()]
        if len(clean_lanes) < 2:
            raise RoadPackageError("At least start and goal lanes are required.")

        base_graph = self.build_lane_graph(include_uturns=include_uturns, allow_lane_changes=False)
        lane_change_graph = (
            self.build_lane_graph(include_uturns=include_uturns, allow_lane_changes=True)
            if allow_lane_changes
            else base_graph
        )
        lane_path: list[str] = []
        current_candidates = self.checkpoint_candidates(clean_lanes[0])
        for index, target_token in enumerate(clean_lanes[1:]):
            target_candidates = self.checkpoint_candidates(target_token)
            try:
                segment = self.shortest_lane_path_between(current_candidates, target_candidates, base_graph)
            except RoadPackageError:
                if not allow_lane_changes:
                    raise
                segment = self.shortest_lane_path_between(current_candidates, target_candidates, lane_change_graph)
            if index > 0:
                segment = segment[1:]
            lane_path.extend(segment)
            current_candidates = [segment[-1]]

        name_parts = [edge_id_from_lane(lane_id) for lane_id in clean_lanes]
        name = "_via_".join(name_parts) if len(name_parts) > 2 else f"{name_parts[0]}_to_{name_parts[-1]}"
        return PlannedRoute(
            name=safe_name(name),
            start_lane=clean_lanes[0],
            goal_lane=clean_lanes[-1],
            lane_path=lane_path,
            steps=[self.lane_step(lane_id) for lane_id in lane_path],
        )

    def lane_step(self, lane_id: str) -> LaneStep:
        lane = self.lanes[lane_id]
        xodr = self.xodr_lane_map.get(lane_id)
        return LaneStep(
            lane_id=lane.id,
            edge_id=lane.edge_id,
            lane_index=lane.index,
            internal=lane.internal,
            length=lane.length,
            speed=lane.speed,
            xodr_road_id=xodr[0] if xodr else None,
            xodr_lane_id=xodr[1] if xodr else None,
        )

    def connection_rows(self, include_internal: bool = False) -> list[dict]:
        rows: list[dict] = []
        for connection in self.connections:
            source = lane_id_for(connection.from_edge, connection.from_lane)
            target = lane_id_for(connection.to_edge, connection.to_lane)
            source_internal = self.edges.get(connection.from_edge, SumoEdge("", None, None, True)).internal
            if source_internal and not include_internal:
                continue
            rows.append(
                {
                    "from": source,
                    "via": connection.via or "",
                    "to": target,
                    "dir": connection.direction,
                    "state": connection.state,
                }
            )
        return rows

    def summary(self) -> str:
        mapped = sum(1 for lane_id in self.external_lanes if lane_id in self.xodr_lane_map)
        return (
            f"Folder: {self.files.folder}\n"
            f"Graph: {self.files.graph.name if self.files.graph else 'missing'}\n"
            f"SUMO net: {self.files.net.name}\n"
            f"OpenDRIVE: {self.files.xodr.name if self.files.xodr else 'missing'}\n"
            f"Edges: {len(self.edges)} total, {sum(1 for edge in self.edges.values() if not edge.internal)} external\n"
            f"Lanes: {len(self.lanes)} total, {len(self.external_lanes)} external, {len(self.internal_lanes)} internal\n"
            f"Connections: {len(self.connections)}\n"
            f"External lanes mapped to XODR: {mapped}/{len(self.external_lanes)}"
        )


def route_to_dict(route: PlannedRoute) -> dict:
    return {
        "name": route.name,
        "start_lane": route.start_lane,
        "goal_lane": route.goal_lane,
        "total_length_m": round(route.total_length, 3),
        "lane_path": route.lane_path,
        "steps": [
            {
                "lane_id": step.lane_id,
                "edge_id": step.edge_id,
                "lane_index": step.lane_index,
                "internal": step.internal,
                "length_m": round(step.length, 3),
                "speed_mps": round(step.speed, 3),
                "xodr_road_id": step.xodr_road_id,
                "xodr_lane_id": step.xodr_lane_id,
            }
            for step in route.steps
        ],
    }


def vehicle_to_dict(vehicle: VehiclePlan) -> dict:
    category = vehicle_category(vehicle.model)
    return {
        "name": vehicle.name,
        "category": category,
        "route_name": vehicle.route_name,
        "model": vehicle.model,
        "driver_model": vehicle.driver_model,
        "control_mode": vehicle.control_mode,
        "speed_kmh": vehicle.speed_kmh,
        "speed_abs_kmh": abs(vehicle.speed_kmh),
        "direction": "reverse" if category == "pedestrian" and vehicle.speed_kmh < 0 else "forward",
        "start_s": vehicle.start_s,
        "lane_offset": vehicle.lane_offset,
        "start_delay_s": vehicle.start_delay_s,
    }


def write_plan(
    package: RoadPackage,
    routes: list[PlannedRoute],
    vehicles: list[VehiclePlan],
    output_dir: Path,
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source_folder": str(package.files.folder),
        "graph_file": str(package.files.graph) if package.files.graph else None,
        "net_file": str(package.files.net),
        "xodr_file": str(package.files.xodr) if package.files.xodr else None,
        "routes": [route_to_dict(route) for route in routes],
        "vehicles": [vehicle_to_dict(vehicle) for vehicle in vehicles],
        "notes": [
            "Routes are SUMO lane-level plans based on .net.xml connections.",
            "OpenDRIVE road/lane IDs are best-effort helper mappings, not validated CarMaker route objects.",
        ],
    }
    json_path = output_dir / "traffic_plan.json"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    report_path = output_dir / "route_report.md"
    report_path.write_text(build_report(package, routes, vehicles), encoding="utf-8")
    return json_path, report_path


def write_xml(path: Path, root: ET.Element) -> None:
    tree = ET.ElementTree(root)
    ET.indent(tree, space="    ")
    tree.write(path, encoding="utf-8", xml_declaration=True)


def find_osc2cm() -> str | None:
    candidates = []
    base = Path(r"C:\IPG\carmaker")
    if base.exists():
        candidates.extend(base.glob(r"win64-*\bin\osc2cm.exe"))

    def version_key(path: Path) -> tuple[int, int, int, str]:
        match = re.search(r"win64-(\d+)\.(\d+)\.(\d+)", str(path))
        if not match:
            return (0, 0, 0, str(path))
        return (int(match.group(1)), int(match.group(2)), int(match.group(3)), str(path))

    if candidates:
        return str(sorted(candidates, key=version_key)[-1])
    return shutil.which("osc2cm")


def vehicle_category(model: str) -> str:
    lowered = model.lower()
    if "pedestrian" in lowered or "people" in lowered:
        return "pedestrian"
    if "cyclist" in lowered or "bicycle" in lowered:
        return "bicycle"
    if "truck" in lowered:
        return "truck"
    if "bus" in lowered:
        return "bus"
    return "car"


def add_inline_vehicle(parent: ET.Element, vehicle: VehiclePlan) -> None:
    category = vehicle_category(vehicle.model)
    if category == "pedestrian":
        pedestrian = ET.SubElement(parent, "Pedestrian", {"name": f"{vehicle.name}_model", "pedestrianCategory": "pedestrian"})
        ET.SubElement(pedestrian, "Properties")
        ET.SubElement(pedestrian, "Mass", {"value": "80"})
        return

    attrs = {"name": f"{vehicle.name}_model", "vehicleCategory": category}
    vehicle_el = ET.SubElement(parent, "Vehicle", attrs)
    properties = ET.SubElement(vehicle_el, "Properties")
    ET.SubElement(properties, "Property", {"name": "carmakerTemplate", "value": vehicle.model})
    ET.SubElement(properties, "Property", {"name": "carmakerDriverModel", "value": vehicle.driver_model})
    ET.SubElement(properties, "Property", {"name": "carmakerControlMode", "value": vehicle.control_mode})
    bbox = ET.SubElement(vehicle_el, "BoundingBox")
    ET.SubElement(bbox, "Center", {"x": "1.4", "y": "0.0", "z": "0.9"})
    ET.SubElement(bbox, "Dimensions", {"width": "1.9", "length": "4.6", "height": "1.6"})
    ET.SubElement(vehicle_el, "Performance", {"maxSpeed": "90", "maxDeceleration": "10", "maxAcceleration": "10"})
    axles = ET.SubElement(vehicle_el, "Axles")
    ET.SubElement(
        axles,
        "FrontAxle",
        {"maxSteering": "0.5", "wheelDiameter": "0.7", "trackWidth": "1.68", "positionX": "2.8", "positionZ": "0.35"},
    )
    ET.SubElement(
        axles,
        "RearAxle",
        {"maxSteering": "0", "wheelDiameter": "0.7", "trackWidth": "1.68", "positionX": "0.0", "positionZ": "0.35"},
    )


def add_controller(parent: ET.Element, vehicle: VehiclePlan) -> None:
    controller = ET.SubElement(parent, "ObjectController")
    controller_el = ET.SubElement(controller, "Controller", {"name": vehicle.driver_model or "DefaultDriver"})
    properties = ET.SubElement(controller_el, "Properties")
    ET.SubElement(properties, "Property", {"name": "driverModel", "value": vehicle.driver_model or "DefaultDriver"})
    ET.SubElement(properties, "Property", {"name": "controlMode", "value": vehicle.control_mode})


def position_attrs(step: LaneStep, s_value: float, offset: float) -> dict[str, str]:
    if step.xodr_road_id is None or step.xodr_lane_id is None:
        raise RoadPackageError(f"Lane {step.lane_id} has no OpenDRIVE road/lane mapping.")
    s_value = max(0.0, min(float(s_value), max(step.length - 0.05, 0.0)))
    return {
        "roadId": str(step.xodr_road_id),
        "laneId": str(step.xodr_lane_id),
        "s": f"{s_value:.3f}",
        "offset": f"{float(offset):.3f}",
    }


def route_by_name(routes: list[PlannedRoute]) -> dict[str, PlannedRoute]:
    return {route.name: route for route in routes}


def add_position(parent: ET.Element, step: LaneStep, s_value: float, offset: float) -> None:
    position = ET.SubElement(parent, "Position")
    ET.SubElement(position, "LanePosition", position_attrs(step, s_value, offset))


def add_private_init(parent: ET.Element, vehicle: VehiclePlan, route: PlannedRoute) -> None:
    mapped_steps = [step for step in route.steps if step.xodr_road_id and step.xodr_lane_id]
    if not mapped_steps:
        raise RoadPackageError(f"Route {route.name} has no OpenDRIVE-mapped steps.")

    private = ET.SubElement(parent, "Private", {"entityRef": vehicle.name})

    teleport_action = ET.SubElement(private, "PrivateAction")
    teleport = ET.SubElement(teleport_action, "TeleportAction")
    add_position(teleport, mapped_steps[0], vehicle.start_s, vehicle.lane_offset)

    speed_action = ET.SubElement(private, "PrivateAction")
    longitudinal = ET.SubElement(speed_action, "LongitudinalAction")
    speed = ET.SubElement(longitudinal, "SpeedAction")
    ET.SubElement(speed, "SpeedActionDynamics", {"dynamicsShape": "step", "value": "0", "dynamicsDimension": "time"})
    target = ET.SubElement(speed, "SpeedActionTarget")
    ET.SubElement(target, "AbsoluteTargetSpeed", {"value": f"{abs(vehicle.speed_kmh) / 3.6:.3f}"})

    route_action = ET.SubElement(private, "PrivateAction")
    routing = ET.SubElement(route_action, "RoutingAction")
    assign = ET.SubElement(routing, "AssignRouteAction")
    route_el = ET.SubElement(assign, "Route", {"name": route.name, "closed": "false"})

    for index, step in enumerate(mapped_steps):
        s_value = vehicle.start_s if index == 0 else 0.0
        waypoint = ET.SubElement(route_el, "Waypoint", {"routeStrategy": "shortest"})
        add_position(waypoint, step, s_value, vehicle.lane_offset)

    final_step = mapped_steps[-1]
    waypoint = ET.SubElement(route_el, "Waypoint", {"routeStrategy": "shortest"})
    add_position(waypoint, final_step, final_step.length, vehicle.lane_offset)


def route_world_points(package: RoadPackage, route: PlannedRoute) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    for lane_id in route.lane_path:
        lane = package.lanes.get(lane_id)
        if lane is None:
            continue
        for point in lane.shape:
            if points and math.hypot(points[-1][0] - point[0], points[-1][1] - point[1]) < 0.05:
                continue
            points.append(point)
    return points


def point_heading(points: list[tuple[float, float]], index: int) -> float:
    if len(points) < 2:
        return 0.0
    if index < len(points) - 1:
        x1, y1 = points[index]
        x2, y2 = points[index + 1]
    else:
        x1, y1 = points[index - 1]
        x2, y2 = points[index]
    return math.atan2(y2 - y1, x2 - x1)


def build_trajectory_catalog(
    package: RoadPackage,
    routes: list[PlannedRoute],
    vehicles: list[VehiclePlan],
    output_dir: Path,
) -> tuple[Path, dict[str, str]]:
    route_map = route_by_name(routes)
    catalog_dir = output_dir / "Catalogs" / "Trajectory"
    catalog_dir.mkdir(parents=True, exist_ok=True)
    catalog_path = catalog_dir / "TrajectoryCatalog.xosc"
    trajectory_names: dict[str, str] = {}

    root = ET.Element("OpenSCENARIO")
    ET.SubElement(
        root,
        "FileHeader",
        {
            "revMajor": "1",
            "revMinor": "2",
            "date": datetime.now().isoformat(timespec="seconds"),
            "description": "trafficGen_app generated trajectory catalog",
            "author": "trafficGen_app",
        },
    )
    catalog = ET.SubElement(root, "Catalog", {"name": "TrajectoryCatalog"})

    for vehicle in vehicles:
        route = route_map[vehicle.route_name]
        points = route_world_points(package, route)
        if len(points) < 2:
            raise RoadPackageError(f"Route {route.name} does not have enough lane shape points for trajectory output.")
        trajectory_name = safe_name(f"{vehicle.name}_{route.name}")
        trajectory_names[vehicle.name] = trajectory_name

        if vehicle_category(vehicle.model) == "pedestrian" and vehicle.speed_kmh < 0:
            points = list(reversed(points))
        speed_mps = max(abs(vehicle.speed_kmh) / 3.6, 0.1)
        trajectory = ET.SubElement(catalog, "Trajectory", {"closed": "false", "name": trajectory_name})
        ET.SubElement(trajectory, "ParameterDeclarations")
        shape = ET.SubElement(trajectory, "Shape")
        polyline = ET.SubElement(shape, "Polyline")

        elapsed = 0.0
        last = points[0]
        for index, point in enumerate(points):
            if index > 0:
                elapsed += math.hypot(point[0] - last[0], point[1] - last[1]) / speed_mps
                last = point
            vertex = ET.SubElement(polyline, "Vertex", {"time": f"{elapsed:.3f}"})
            position = ET.SubElement(vertex, "Position")
            ET.SubElement(
                position,
                "WorldPosition",
                {
                    "x": f"{point[0]:.6f}",
                    "y": f"{point[1]:.6f}",
                    "z": "0.0",
                    "h": f"{point_heading(points, index):.6f}",
                    "p": "0.0",
                    "r": "0.0",
                },
            )

    write_xml(catalog_path, root)
    return catalog_path, trajectory_names


def add_follow_trajectory_story(parent: ET.Element, vehicles: list[VehiclePlan], trajectory_names: dict[str, str]) -> None:
    story = ET.SubElement(parent, "Story", {"name": "TrafficGenStory"})
    act = ET.SubElement(story, "Act", {"name": "FollowGeneratedTrajectories"})

    for vehicle in vehicles:
        maneuver_group = ET.SubElement(
            act,
            "ManeuverGroup",
            {"maximumExecutionCount": "1", "name": f"ManeuverGroup_{vehicle.name}"},
        )
        actors = ET.SubElement(maneuver_group, "Actors", {"selectTriggeringEntities": "false"})
        ET.SubElement(actors, "EntityRef", {"entityRef": vehicle.name})
        maneuver = ET.SubElement(maneuver_group, "Maneuver", {"name": f"Maneuver_{vehicle.name}_FollowTrajectory"})
        event = ET.SubElement(
            maneuver,
            "Event",
            {"maximumExecutionCount": "1", "name": f"Event_{vehicle.name}_FollowTrajectory", "priority": "overwrite"},
        )
        action = ET.SubElement(event, "Action", {"name": f"Action_{vehicle.name}_FollowTrajectory"})
        private_action = ET.SubElement(action, "PrivateAction")
        routing = ET.SubElement(private_action, "RoutingAction")
        follow = ET.SubElement(routing, "FollowTrajectoryAction")
        time_ref = ET.SubElement(follow, "TimeReference")
        ET.SubElement(time_ref, "Timing", {"domainAbsoluteRelative": "absolute", "offset": "0.0", "scale": "1.0"})
        ET.SubElement(follow, "TrajectoryFollowingMode", {"followingMode": "follow"})
        ET.SubElement(follow, "CatalogReference", {"catalogName": "TrajectoryCatalog", "entryName": trajectory_names[vehicle.name]})

        start = ET.SubElement(event, "StartTrigger")
        group = ET.SubElement(start, "ConditionGroup")
        condition = ET.SubElement(group, "Condition", {"name": f"Start_{vehicle.name}_Trajectory", "delay": "0", "conditionEdge": "rising"})
        by_value = ET.SubElement(condition, "ByValueCondition")
        ET.SubElement(by_value, "SimulationTimeCondition", {"value": "0", "rule": "greaterThan"})

    start_trigger = ET.SubElement(act, "StartTrigger")
    group = ET.SubElement(start_trigger, "ConditionGroup")
    condition = ET.SubElement(group, "Condition", {"name": "StartAct", "delay": "0", "conditionEdge": "rising"})
    by_value = ET.SubElement(condition, "ByValueCondition")
    ET.SubElement(by_value, "SimulationTimeCondition", {"value": "0", "rule": "greaterThan"})


def build_openscenario(
    package: RoadPackage,
    routes: list[PlannedRoute],
    vehicles: list[VehiclePlan],
    output_dir: Path,
    scenario_name: str = "traffic_scenario",
) -> tuple[Path, Path, Path]:
    if not package.files.xodr:
        raise RoadPackageError("Cannot generate OpenSCENARIO without an .xodr file.")
    if not routes:
        raise RoadPackageError("Plan at least one route before generating OpenSCENARIO.")
    if not vehicles:
        raise RoadPackageError("Add at least one vehicle before generating OpenSCENARIO.")

    route_map = route_by_name(routes)
    for vehicle in vehicles:
        if vehicle.route_name not in route_map:
            raise RoadPackageError(f"Vehicle {vehicle.name} references missing route {vehicle.route_name}.")

    output_dir.mkdir(parents=True, exist_ok=True)
    xodr_copy = output_dir / package.files.xodr.name
    if package.files.xodr.resolve() != xodr_copy.resolve():
        shutil.copy2(package.files.xodr, xodr_copy)

    xosc_path = output_dir / f"{safe_name(scenario_name)}.xosc"
    script_path = output_dir / "run_osc2cm.ps1"
    readme_path = output_dir / "OSC2CM_README.md"
    trajectory_catalog, trajectory_names = build_trajectory_catalog(package, routes, vehicles, output_dir)

    root = ET.Element("OpenSCENARIO")
    ET.SubElement(
        root,
        "FileHeader",
        {
            "revMajor": "1",
            "revMinor": "2",
            "date": datetime.now().isoformat(timespec="seconds"),
            "description": "trafficGen_app lane-level route scenario",
            "author": "trafficGen_app",
        },
    )
    ET.SubElement(root, "ParameterDeclarations")
    catalogs = ET.SubElement(root, "CatalogLocations")
    trajectory_catalog_el = ET.SubElement(catalogs, "TrajectoryCatalog")
    ET.SubElement(trajectory_catalog_el, "Directory", {"path": "./Catalogs/Trajectory"})
    road_network = ET.SubElement(root, "RoadNetwork")
    ET.SubElement(road_network, "LogicFile", {"filepath": f"./{xodr_copy.name}"})

    entities = ET.SubElement(root, "Entities")
    for vehicle in vehicles:
        scenario_object = ET.SubElement(entities, "ScenarioObject", {"name": vehicle.name})
        add_inline_vehicle(scenario_object, vehicle)
        add_controller(scenario_object, vehicle)

    storyboard = ET.SubElement(root, "Storyboard")
    init = ET.SubElement(storyboard, "Init")
    actions = ET.SubElement(init, "Actions")
    for vehicle in vehicles:
        add_private_init(actions, vehicle, route_map[vehicle.route_name])

    add_follow_trajectory_story(storyboard, vehicles, trajectory_names)

    stop_trigger = ET.SubElement(storyboard, "StopTrigger")
    group = ET.SubElement(stop_trigger, "ConditionGroup")
    condition = ET.SubElement(group, "Condition", {"name": "StopAfter60s", "delay": "0", "conditionEdge": "rising"})
    by_value = ET.SubElement(condition, "ByValueCondition")
    ET.SubElement(by_value, "SimulationTimeCondition", {"value": "60", "rule": "greaterThan"})

    write_xml(xosc_path, root)
    write_osc2cm_helper(xosc_path, xodr_copy, trajectory_catalog, script_path, readme_path)
    return xosc_path, script_path, readme_path


def write_osc2cm_helper(xosc_path: Path, xodr_path: Path, trajectory_catalog: Path, script_path: Path, readme_path: Path) -> None:
    osc2cm = find_osc2cm() or r"C:\IPG\carmaker\win64-15.0.1\bin\osc2cm.exe"
    project_hint = r"C:\CM_Projects\MapGen_TEST"
    rel_hint = f"Data/OpenSCENARIO/TrafficGen/{xosc_path.name}"
    rd5_name = xodr_path.with_suffix(".rd5").name
    tr_name = xosc_path.stem

    script = f"""$cmProject = "{project_hint}"
$target = Join-Path $cmProject "Data\\OpenSCENARIO\\TrafficGen"
New-Item -ItemType Directory -Force -Path $target | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $target "Catalogs\\Trajectory") | Out-Null
Copy-Item -Force "{xosc_path}" (Join-Path $target "{xosc_path.name}")
Copy-Item -Force "{xodr_path}" (Join-Path $target "{xodr_path.name}")
Copy-Item -Force "{trajectory_catalog}" (Join-Path $target "Catalogs\\Trajectory\\TrajectoryCatalog.xosc")
& "{osc2cm}" --cmprojpath $cmProject --oscfname "{rel_hint}" --rdfname "{rd5_name}" --trfname "{tr_name}" --logtoconsole
"""
    script_path.write_text(script, encoding="utf-8")

    readme = f"""# OpenSCENARIO To CarMaker

Generated files:

- `{xosc_path.name}`
- `{xodr_path.name}`
- `Catalogs/Trajectory/TrajectoryCatalog.xosc`
- `run_osc2cm.ps1`

The XOSC references the XODR with a relative path:

```xml
<LogicFile filepath="./{xodr_path.name}" />
```

Recommended test flow:

1. Open PowerShell.
2. Run `run_osc2cm.ps1`.
3. Open CarMaker project `{project_hint}`.
4. Check the generated TestRun `{tr_name}` and road `{rd5_name}`.

The script copies the XOSC/XODR pair to:

```text
{project_hint}\\Data\\OpenSCENARIO\\TrafficGen
```

Then it runs:

```powershell
& "{osc2cm}" --cmprojpath "{project_hint}" --oscfname "{rel_hint}" --rdfname "{rd5_name}" --trfname "{tr_name}" --logtoconsole
```

This is the A-method experiment. It does not require manually creating CarMaker
routes first. If CarMaker rejects the scenario, the next thing to adjust is the
OpenSCENARIO route representation, not the lane graph parser.
"""
    readme_path.write_text(readme, encoding="utf-8")


def build_report(package: RoadPackage, routes: list[PlannedRoute], vehicles: list[VehiclePlan]) -> str:
    lines = [
        "# Traffic Route Report",
        "",
        "## Package",
        "",
        "```text",
        package.summary(),
        "```",
        "",
        "## Routes",
        "",
    ]
    if not routes:
        lines.append("No routes were saved.")
    for route in routes:
        lines.extend(
            [
                f"### {route.name}",
                "",
                f"- Start: `{route.start_lane}`",
                f"- Goal: `{route.goal_lane}`",
                f"- Length: `{route.total_length:.2f} m`",
                "",
                "| # | Lane | Edge | Internal | XODR road | XODR lane |",
                "|---:|---|---|---|---|---|",
            ]
        )
        for index, step in enumerate(route.steps, start=1):
            lines.append(
                f"| {index} | `{step.lane_id}` | `{step.edge_id}` | {step.internal} | "
                f"`{step.xodr_road_id or ''}` | `{step.xodr_lane_id or ''}` |"
            )
        lines.append("")

    lines.extend(["## Actors", ""])
    if not vehicles:
        lines.append("No traffic actors were saved.")
    for vehicle in vehicles:
        category = vehicle_category(vehicle.model)
        direction = " reverse" if category == "pedestrian" and vehicle.speed_kmh < 0 else ""
        lines.append(
            f"- `{vehicle.name}` ({category}{direction}) on `{vehicle.route_name}` at `{abs(vehicle.speed_kmh):g} km/h`, "
            f"route s={vehicle.start_s:g} m, lateral offset={vehicle.lane_offset:g} m, delay={vehicle.start_delay_s:g} s, "
            f"model `{vehicle.model}`, driver `{vehicle.driver_model}`, control `{vehicle.control_mode}`"
        )
    lines.extend(
        [
            "",
            "## CarMaker Note",
            "",
            "For CarMaker use, write the route into an `.rd5` first, then generate a TestRun that references the route ObjId.",
        ]
    )
    return "\n".join(lines) + "\n"
