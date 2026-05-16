from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from traffic_core import PlannedRoute, RoadPackage, RoadPackageError


def junction_link_index(junction_index: int, link_index: int) -> int:
    return 1_000_000 + junction_index * 1_000 + link_index


@dataclass
class Rd5LanePath:
    index: int
    lane_path_id: str
    lane_object_id: str
    raw_values: list[str]


@dataclass
class Rd5ConPath:
    index: int
    con_path_id: str
    link_id: str
    start_path_id: str
    start_s: float
    start_lon_ref: str
    end_path_id: str
    end_s: float
    end_lon_ref: str
    vehicle_class_mask: str
    raw_values: list[str]


@dataclass
class Rd5Link:
    index: int
    link_id: str | None = None
    odr_road_id: str | None = None
    length: float | None = None
    is_junction_link: bool = False
    lanes_right: dict[int, str] = field(default_factory=dict)
    lanes_left: dict[int, str] = field(default_factory=dict)


@dataclass
class Rd5Route:
    index: int
    route_id: str | None = None
    name: str | None = None
    length: float | None = None
    drv_path_id: str | None = None
    drv_path: list[str] = field(default_factory=list)


@dataclass
class Rd5MapResult:
    lane_id: str
    edge_id: str
    xodr_road_id: str | None
    xodr_lane_id: str | None
    rd5_link_index: int | None
    rd5_link_id: str | None
    rd5_lane_object_id: str | None
    rd5_lane_path_id: str | None
    status: str
    message: str = ""

    @property
    def ok(self) -> bool:
        return self.status == "ok"


@dataclass
class Rd5RouteWriteResult:
    output_path: Path
    route_index: int
    route_id: str
    drv_path_id: str
    route_name: str
    route_length: float
    lane_path_ids: list[str]
    drv_path_ids: list[str]
    mapped_results: list[Rd5MapResult]
    skipped_results: list[Rd5MapResult]
    report: str


class Rd5Road:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        self.n_objects = 0
        self.n_routes = 0
        self.max_used_obj_id = 0
        self.original_file: str | None = None
        self.links: dict[int, Rd5Link] = {}
        self.links_by_odr: dict[str, list[Rd5Link]] = {}
        self.lane_paths: dict[str, Rd5LanePath] = {}
        self.lane_paths_by_lane_object: dict[str, list[Rd5LanePath]] = {}
        self.con_paths: dict[str, Rd5ConPath] = {}
        self.con_paths_by_pair: dict[tuple[str, str], list[Rd5ConPath]] = {}
        self.routes: dict[int, Rd5Route] = {}
        self._parse()

    @classmethod
    def load(cls, path: str | Path) -> "Rd5Road":
        path = Path(path)
        if not path.exists():
            raise RoadPackageError(f"RD5 file does not exist: {path}")
        return cls(path)

    def _parse(self) -> None:
        route_path_index: int | None = None

        for line in self.lines:
            stripped = line.strip()
            if not stripped:
                continue

            if route_path_index is not None:
                if line.startswith("\t") or line.startswith(" "):
                    value = stripped.split()[0] if stripped.split() else ""
                    if value:
                        self.routes.setdefault(route_path_index, Rd5Route(route_path_index)).drv_path.append(value)
                    continue
                route_path_index = None

            if stripped.startswith("Original File:"):
                self.original_file = stripped.split(":", 1)[1].strip()
                continue

            match = re.match(r"nObjects\s*=\s*(\d+)", stripped)
            if match:
                self.n_objects = int(match.group(1))
                continue

            match = re.match(r"nRoutes\s*=\s*(\d+)", stripped)
            if match:
                self.n_routes = int(match.group(1))
                continue

            match = re.match(r"MaxUsedObjId\s*=\s*(\d+)", stripped)
            if match:
                self.max_used_obj_id = int(match.group(1))
                continue

            match = re.match(r"Route\.(\d+)\.Length\s*=\s*(\S+)", stripped)
            if match:
                route = self.routes.setdefault(int(match.group(1)), Rd5Route(int(match.group(1))))
                try:
                    route.length = float(match.group(2))
                except ValueError:
                    route.length = None
                continue

            match = re.match(r"Route\.(\d+)\.ID\s*=\s*(\S+)", stripped)
            if match:
                route = self.routes.setdefault(int(match.group(1)), Rd5Route(int(match.group(1))))
                route.route_id = match.group(2)
                continue

            match = re.match(r"Route\.(\d+)\.Name\s*=\s*(.*)", stripped)
            if match:
                route = self.routes.setdefault(int(match.group(1)), Rd5Route(int(match.group(1))))
                route.name = match.group(2).strip()
                continue

            match = re.match(r"Route\.(\d+)\.DrvPath\.ID\s*=\s*(\S+)", stripped)
            if match:
                route = self.routes.setdefault(int(match.group(1)), Rd5Route(int(match.group(1))))
                route.drv_path_id = match.group(2)
                continue

            match = re.match(r"Route\.(\d+)\.DrvPath:\s*$", stripped)
            if match:
                route_path_index = int(match.group(1))
                self.routes.setdefault(route_path_index, Rd5Route(route_path_index))
                continue

            match = re.match(r"Link\.(\d+)\.ID\s*=\s*(\S+)", stripped)
            if match:
                link = self.links.setdefault(int(match.group(1)), Rd5Link(int(match.group(1))))
                link.link_id = match.group(2)
                continue

            match = re.match(r"Junction\.(\d+)\.Link\.(\d+)\.ID\s*=\s*(\S+)(?:\s+(\S+))?", stripped)
            if match:
                index = junction_link_index(int(match.group(1)), int(match.group(2)))
                link = self.links.setdefault(index, Rd5Link(index))
                link.is_junction_link = True
                link.link_id = "/".join(value for value in [match.group(3), match.group(4)] if value)
                continue

            match = re.match(r"Link\.(\d+)\.Tag\s*=\s*odrRoadId:(\S+)", stripped)
            if match:
                link = self.links.setdefault(int(match.group(1)), Rd5Link(int(match.group(1))))
                link.odr_road_id = match.group(2)
                continue

            match = re.match(r"Junction\.(\d+)\.Link\.(\d+)\.Tag\s*=\s*odrRoadId:(\S+)", stripped)
            if match:
                index = junction_link_index(int(match.group(1)), int(match.group(2)))
                link = self.links.setdefault(index, Rd5Link(index))
                link.is_junction_link = True
                link.odr_road_id = match.group(3)
                continue

            match = re.match(r"Link\.(\d+)\.Seg\.0\.Param\s*=\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+))", stripped)
            if match:
                link = self.links.setdefault(int(match.group(1)), Rd5Link(int(match.group(1))))
                link.length = float(match.group(2))
                continue

            match = re.match(r"Link\.(\d+)\.LaneSection\.\d+\.Lane([RL])\.(\d+)\.ID\s*=\s*(\S+)", stripped)
            if match:
                link = self.links.setdefault(int(match.group(1)), Rd5Link(int(match.group(1))))
                side = match.group(2)
                lane_index = int(match.group(3))
                lane_object_id = match.group(4)
                if side == "R":
                    link.lanes_right[lane_index] = lane_object_id
                else:
                    link.lanes_left[lane_index] = lane_object_id
                continue

            match = re.match(
                r"Junction\.(\d+)\.Link\.(\d+)\.LaneSection\.\d+\.Lane([RL])\.(\d+)\.ID\s*=\s*(\S+)",
                stripped,
            )
            if match:
                index = junction_link_index(int(match.group(1)), int(match.group(2)))
                link = self.links.setdefault(index, Rd5Link(index))
                link.is_junction_link = True
                side = match.group(3)
                lane_index = int(match.group(4))
                lane_object_id = match.group(5)
                if side == "R":
                    link.lanes_right[lane_index] = lane_object_id
                else:
                    link.lanes_left[lane_index] = lane_object_id
                continue

            match = re.match(r"LanePath\.(\d+)\s*=\s*(.+)", stripped)
            if match:
                index = int(match.group(1))
                values = match.group(2).split()
                if len(values) >= 2:
                    lane_path = Rd5LanePath(
                        index=index,
                        lane_path_id=values[0],
                        lane_object_id=values[1],
                        raw_values=values,
                    )
                    self.lane_paths[lane_path.lane_path_id] = lane_path
                    self.lane_paths_by_lane_object.setdefault(lane_path.lane_object_id, []).append(lane_path)
                continue

            match = re.match(r"ConPath\.(\d+)\s*=\s*(.+)", stripped)
            if match:
                index = int(match.group(1))
                values = match.group(2).split()
                if len(values) >= 14:
                    try:
                        start_s = float(values[3])
                        end_s = float(values[6])
                    except ValueError:
                        continue
                    con_path = Rd5ConPath(
                        index=index,
                        con_path_id=values[0],
                        link_id=values[1],
                        start_path_id=values[2],
                        start_s=start_s,
                        start_lon_ref=values[4],
                        end_path_id=values[5],
                        end_s=end_s,
                        end_lon_ref=values[7],
                        vehicle_class_mask=values[8],
                        raw_values=values,
                    )
                    self.con_paths[con_path.con_path_id] = con_path
                    self.con_paths_by_pair.setdefault((con_path.start_path_id, con_path.end_path_id), []).append(con_path)
                continue

        self.links_by_odr.clear()
        for link in self.links.values():
            if link.odr_road_id:
                self.links_by_odr.setdefault(link.odr_road_id, []).append(link)

    def summary(self) -> str:
        lane_object_count = sum(len(link.lanes_right) + len(link.lanes_left) for link in self.links.values())
        return (
            f"RD5: {self.path}\n"
            f"Original File: {self.original_file or 'unknown'}\n"
            f"Links: {len(self.links)}\n"
            f"Links with odrRoadId: {len(self.links_by_odr)}\n"
            f"Lane objects: {lane_object_count}\n"
            f"LanePaths: {len(self.lane_paths)}\n"
            f"ConPaths: {len(self.con_paths)}\n"
            f"Routes: {self.n_routes} declared, {len(self.routes)} parsed\n"
            f"MaxUsedObjId: {self.max_used_obj_id or 'unknown'}"
        )

    def find_con_path(self, start_lane_path_id: str, end_lane_path_id: str, link_id: str | None = None) -> Rd5ConPath | None:
        candidates = self.con_paths_by_pair.get((start_lane_path_id, end_lane_path_id), [])
        if link_id is not None:
            candidates = [item for item in candidates if item.link_id == link_id]
        return candidates[0] if candidates else None

    def map_xodr_lane(
        self,
        xodr_road_id: str | None,
        xodr_lane_id: str | None,
        prefer_junction_link: bool | None = None,
    ) -> Rd5MapResult:
        if not xodr_road_id or not xodr_lane_id:
            return Rd5MapResult("", "", xodr_road_id, xodr_lane_id, None, None, None, None, "missing_xodr", "No XODR mapping.")

        links = self.links_by_odr.get(str(xodr_road_id), [])
        if not links:
            return Rd5MapResult(
                "",
                "",
                str(xodr_road_id),
                str(xodr_lane_id),
                None,
                None,
                None,
                None,
                "missing_road",
                f"No RD5 Link.Tag = odrRoadId:{xodr_road_id}",
            )
        if prefer_junction_link is not None:
            preferred_links = [link for link in links if link.is_junction_link == prefer_junction_link]
            if preferred_links:
                links = preferred_links

        try:
            lane_number = int(xodr_lane_id)
        except ValueError:
            return Rd5MapResult(
                "",
                "",
                str(xodr_road_id),
                str(xodr_lane_id),
                None,
                None,
                None,
                None,
                "bad_lane",
                f"Unsupported XODR lane id: {xodr_lane_id}",
            )

        if lane_number == 0:
            return Rd5MapResult(
                "",
                "",
                str(xodr_road_id),
                str(xodr_lane_id),
                None,
                None,
                None,
                None,
                "bad_lane",
                "Lane 0 is the road center and cannot map to a LanePath.",
            )

        lane_index = abs(lane_number) - 1
        side = "R" if lane_number < 0 else "L"

        candidates: list[tuple[Rd5Link, str, Rd5LanePath]] = []
        for link in links:
            lane_object_id = (link.lanes_right if side == "R" else link.lanes_left).get(lane_index)
            if not lane_object_id:
                continue
            lane_paths = self.lane_paths_by_lane_object.get(lane_object_id, [])
            for lane_path in lane_paths:
                candidates.append((link, lane_object_id, lane_path))

        if not candidates:
            lane_objects = []
            for link in links:
                lane_objects.extend((link.lanes_right if side == "R" else link.lanes_left).values())
            return Rd5MapResult(
                "",
                "",
                str(xodr_road_id),
                str(xodr_lane_id),
                links[0].index if links else None,
                links[0].link_id if links else None,
                None,
                None,
                "missing_lanepath",
                f"No LanePath for road {xodr_road_id} lane {xodr_lane_id}; lane objects on side {side}: {lane_objects}",
            )

        link, lane_object_id, lane_path = candidates[0]
        status = "ok" if len(candidates) == 1 else "ok_ambiguous"
        message = "" if len(candidates) == 1 else f"{len(candidates)} candidates; selected first."
        return Rd5MapResult(
            "",
            "",
            str(xodr_road_id),
            str(xodr_lane_id),
            link.index,
            link.link_id,
            lane_object_id,
            lane_path.lane_path_id,
            status,
            message,
        )


def map_route_to_rd5(rd5: Rd5Road, route: PlannedRoute, skip_internal: bool = False) -> list[Rd5MapResult]:
    results: list[Rd5MapResult] = []
    for step in route.steps:
        if skip_internal and step.internal:
            continue
        result = rd5.map_xodr_lane(step.xodr_road_id, step.xodr_lane_id, prefer_junction_link=step.internal)
        result.lane_id = step.lane_id
        result.edge_id = step.edge_id
        results.append(result)
    return results


def lane_path_sequence(results: list[Rd5MapResult], dedupe: bool = True) -> list[str]:
    sequence: list[str] = []
    for result in results:
        if not result.rd5_lane_path_id:
            continue
        if dedupe and sequence and sequence[-1] == result.rd5_lane_path_id:
            continue
        sequence.append(result.rd5_lane_path_id)
    return sequence


def rd5_safe_name(value: str | None, fallback: str = "Route") -> str:
    value = (value or "").strip()
    cleaned = re.sub(r"[^A-Za-z0-9_]+", "_", value).strip("_")
    return cleaned or fallback


def _format_float(value: float) -> str:
    return f"{value:.12g}"


def _next_route_index(rd5: Rd5Road) -> int:
    highest_declared_index = rd5.n_routes - 1
    highest_parsed_index = max(rd5.routes, default=-1)
    return max(highest_declared_index, highest_parsed_index) + 1


def _next_object_ids(rd5: Rd5Road) -> tuple[str, str, int]:
    base = rd5.max_used_obj_id
    if not base:
        numeric_ids: list[int] = []
        for link in rd5.links.values():
            for value in [link.link_id, *link.lanes_left.values(), *link.lanes_right.values()]:
                if value and value.isdigit():
                    numeric_ids.append(int(value))
        for lane_path in rd5.lane_paths.values():
            if lane_path.lane_path_id.isdigit():
                numeric_ids.append(int(lane_path.lane_path_id))
            if lane_path.lane_object_id.isdigit():
                numeric_ids.append(int(lane_path.lane_object_id))
        for con_path in rd5.con_paths.values():
            for value in [con_path.con_path_id, con_path.link_id, con_path.start_path_id, con_path.end_path_id]:
                if value and value.isdigit():
                    numeric_ids.append(int(value))
        for route in rd5.routes.values():
            for value in [route.route_id, route.drv_path_id, *route.drv_path]:
                if value and value.isdigit():
                    numeric_ids.append(int(value))
        base = max(numeric_ids, default=0)
    route_id = base + 1
    drv_path_id = base + 2
    return str(route_id), str(drv_path_id), drv_path_id


def _next_object_ids_with_conpaths(rd5: Rd5Road, n_conpaths: int) -> tuple[list[str], str, str, int]:
    route_id, drv_path_id, max_used_obj_id = _next_object_ids(rd5)
    base = int(route_id) - 1
    con_path_ids = [str(base + offset) for offset in range(1, n_conpaths + 1)]
    route_id = str(base + n_conpaths + 1)
    drv_path_id = str(base + n_conpaths + 2)
    return con_path_ids, route_id, drv_path_id, base + n_conpaths + 2


def _insert_route_length(lines: list[str], route_index: int, route_length: float) -> None:
    route_length_line = f"Route.{route_index}.Length = {_format_float(route_length)}"
    last_route_length = None
    fallback = None
    for index, line in enumerate(lines):
        stripped = line.strip()
        if re.match(r"Route\.\d+\.Length\s*=", stripped):
            last_route_length = index
        elif stripped.startswith("BBox ="):
            fallback = index
        elif stripped.startswith("RoadNetworkLength =") and fallback is None:
            fallback = index

    insert_at = last_route_length + 1 if last_route_length is not None else (fallback + 1 if fallback is not None else len(lines))
    lines.insert(insert_at, route_length_line)


def _insert_route_block(
    lines: list[str],
    route_index: int,
    route_id: str,
    drv_path_id: str,
    route_name: str,
    lane_path_ids: list[str],
) -> None:
    block = [
        f"Route.{route_index}.ID = {route_id}",
        f"Route.{route_index}.Name = {route_name}",
        f"Route.{route_index}.DrvPath.ID = {drv_path_id}",
        f"Route.{route_index}.DrvPath:",
    ]
    block.extend(f"\t{lane_path_id}" for lane_path_id in lane_path_ids)

    insert_at = len(lines)
    for index, line in enumerate(lines):
        if line.strip().startswith("MaxUsedObjId ="):
            insert_at = index
            break
    lines[insert_at:insert_at] = block


def _insert_con_path_blocks(lines: list[str], blocks: list[str]) -> None:
    if not blocks:
        return
    insert_at = len(lines)
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("Route.") and ".ID" in stripped:
            insert_at = index
            break
        if stripped.startswith("MaxUsedObjId ="):
            insert_at = index
            break
    lines[insert_at:insert_at] = blocks


def _patch_scalar(lines: list[str], key: str, value: int) -> bool:
    pattern = re.compile(rf"{re.escape(key)}\s*=")
    for index, line in enumerate(lines):
        if pattern.match(line.strip()):
            lines[index] = f"{key} = {value}"
            return True
    return False


def build_rd5_write_report(result: Rd5RouteWriteResult) -> str:
    skipped = [entry for entry in result.skipped_results if entry.status != "missing_xodr"]
    lines = [
        "# RD5 Route Write Report",
        "",
        f"- Output RD5: `{result.output_path}`",
        f"- Route index: `{result.route_index}`",
        f"- Route name: `{result.route_name}`",
        f"- Route object ID: `{result.route_id}`",
        f"- DrvPath object ID: `{result.drv_path_id}`",
        f"- Route length: `{_format_float(result.route_length)}`",
        f"- DrvPath IDs: `{' '.join(result.drv_path_ids)}`",
        f"- LanePath IDs: `{' '.join(result.lane_path_ids)}`",
        "",
        "## Vehicle Usage Note",
        "",
        "This RD5 contains the road-level Route/DrvPath. Use the TrafficGen TestRun generator to place the ego vehicle and traffic vehicles on this route ObjId.",
        "",
        "## Mapped LanePaths",
        "",
        "| # | SUMO lane | XODR road/lane | RD5 Link | Lane Object | LanePath |",
        "|---:|---|---|---|---|---|",
    ]
    for index, item in enumerate(result.mapped_results, start=1):
        lines.append(
            f"| {index} | `{item.lane_id}` | `{item.xodr_road_id or ''}/{item.xodr_lane_id or ''}` | "
            f"`{item.rd5_link_id or ''}` | `{item.rd5_lane_object_id or ''}` | `{item.rd5_lane_path_id or ''}` |"
        )
    if skipped:
        lines.extend(["", "## Skipped Steps", ""])
        for item in skipped:
            lines.append(f"- `{item.lane_id}` {item.xodr_road_id}/{item.xodr_lane_id}: {item.status} - {item.message}")
        lines.append("")
        lines.append("Skipped steps are usually SUMO/OpenDRIVE internal junction connector lanes that are not exposed as RD5 Link.Tag entries.")
    return "\n".join(lines) + "\n"


def _lane_change_window(link_length: float | None, ordinal: int, total: int) -> tuple[float, float]:
    length = link_length if link_length and link_length > 0 else 30.0
    margin = min(max(length * 0.08, 0.5), max(length / 4.0, 0.5))
    usable = max(length - 2.0 * margin, 1.0)
    total = max(total, 1)
    slot = usable / total
    start = margin + slot * ordinal + slot * 0.15
    end = margin + slot * (ordinal + 1) - slot * 0.15
    if end <= start:
        midpoint = margin + slot * (ordinal + 0.5)
        start = max(margin, midpoint - 0.5)
        end = min(length - margin, midpoint + 0.5)
    return max(0.1, start), min(max(end, start + 0.5), max(length - 0.1, start + 0.5))


def _link_by_id(rd5: Rd5Road, link_id: str | None) -> Rd5Link | None:
    if not link_id:
        return None
    for link in rd5.links.values():
        if link.link_id == link_id:
            return link
    return None


def _build_drv_path_with_conpaths(
    rd5: Rd5Road,
    mapped_results: list[Rd5MapResult],
    con_path_ids: list[str],
) -> tuple[list[str], list[str]]:
    drv_path_ids: list[str] = []
    con_path_blocks: list[str] = []
    con_path_index = max((item.index for item in rd5.con_paths.values()), default=-1) + 1
    next_con_path = 0
    lane_change_totals: dict[str, int] = {}
    previous_for_count: Rd5MapResult | None = None
    for item in mapped_results:
        if (
            previous_for_count
            and previous_for_count.rd5_lane_path_id
            and item.rd5_lane_path_id
            and previous_for_count.rd5_lane_path_id != item.rd5_lane_path_id
            and previous_for_count.rd5_link_id
            and previous_for_count.rd5_link_id == item.rd5_link_id
        ):
            lane_change_totals[item.rd5_link_id] = lane_change_totals.get(item.rd5_link_id, 0) + 1
        if item.rd5_lane_path_id:
            previous_for_count = item
    lane_change_ordinals: dict[str, int] = {}

    previous: Rd5MapResult | None = None
    for item in mapped_results:
        lane_path_id = item.rd5_lane_path_id
        if not lane_path_id:
            continue
        if previous and previous.rd5_lane_path_id and previous.rd5_lane_path_id != lane_path_id:
            same_link = previous.rd5_link_id and previous.rd5_link_id == item.rd5_link_id
            if same_link:
                con_path = rd5.find_con_path(previous.rd5_lane_path_id, lane_path_id, link_id=item.rd5_link_id)
                if con_path:
                    if not drv_path_ids or drv_path_ids[-1] != con_path.con_path_id:
                        drv_path_ids.append(con_path.con_path_id)
                else:
                    if next_con_path >= len(con_path_ids):
                        raise RoadPackageError("Internal error: not enough generated ConPath IDs.")
                    con_path_id = con_path_ids[next_con_path]
                    next_con_path += 1
                    link = _link_by_id(rd5, item.rd5_link_id)
                    link_key = item.rd5_link_id or ""
                    ordinal = lane_change_ordinals.get(link_key, 0)
                    lane_change_ordinals[link_key] = ordinal + 1
                    start_s, end_s = _lane_change_window(
                        link.length if link else None,
                        ordinal,
                        lane_change_totals.get(link_key, 1),
                    )
                    values = [
                        con_path_id,
                        item.rd5_link_id or "",
                        previous.rd5_lane_path_id,
                        _format_float(start_s),
                        "0",
                        lane_path_id,
                        _format_float(end_s),
                        "0",
                        "31",
                        "1",
                        "-1",
                        "-1",
                        "-1",
                        "-1",
                    ]
                    con_path_blocks.append(f"ConPath.{con_path_index} = {' '.join(values)}")
                    con_path_index += 1
                    drv_path_ids.append(con_path_id)
        if not drv_path_ids or drv_path_ids[-1] != lane_path_id:
            drv_path_ids.append(lane_path_id)
        previous = item
    return drv_path_ids, con_path_blocks


def _count_needed_conpaths(rd5: Rd5Road, mapped_results: list[Rd5MapResult]) -> int:
    count = 0
    previous: Rd5MapResult | None = None
    for item in mapped_results:
        if previous and previous.rd5_lane_path_id and item.rd5_lane_path_id and previous.rd5_lane_path_id != item.rd5_lane_path_id:
            same_link = previous.rd5_link_id and previous.rd5_link_id == item.rd5_link_id
            if same_link and not rd5.find_con_path(previous.rd5_lane_path_id, item.rd5_lane_path_id, link_id=item.rd5_link_id):
                count += 1
        previous = item
    return count


def write_rd5_with_route(
    rd5: Rd5Road,
    route: PlannedRoute,
    output_path: str | Path,
    route_name: str | None = None,
    allow_partial: bool = True,
) -> Rd5RouteWriteResult:
    if route.is_same_edge_lane_change_only():
        raise RoadPackageError(
            "CarMaker RD5 route export is disabled for same-edge-only lane changes "
            f"such as `{route.start_lane}` -> `{route.goal_lane}`. "
            "CarMaker can misplace the vehicle when a Route consists only of an in-link lane-change ConPath. "
            "Use start/goal lanes on different edges, or include a downstream checkpoint/goal edge."
        )

    all_results = map_route_to_rd5(rd5, route)
    mapped_results = [item for item in all_results if item.ok or item.status == "ok_ambiguous"]
    skipped_results = [item for item in all_results if not (item.ok or item.status == "ok_ambiguous")]
    lane_path_ids = lane_path_sequence(mapped_results)

    if not lane_path_ids:
        examples = []
        for item in all_results[:6]:
            examples.append(
                f"{item.lane_id or '?'} xodr={item.xodr_road_id or ''}/{item.xodr_lane_id or ''} "
                f"status={item.status}"
            )
        detail = "; ".join(examples) if examples else "route has no lane steps"
        raise RoadPackageError(
            "RD5 route writing needs at least one mapped LanePath ID. "
            "This usually means the selected RD5 was not converted from the currently loaded RoadGen export, "
            f"or the selected lane has no RD5 LanePath. Route `{route.name}` mapping sample: {detail}"
        )
    if skipped_results and not allow_partial:
        raise RoadPackageError("Some route steps could not be mapped to RD5 LanePath IDs.")

    route_index = _next_route_index(rd5)
    n_needed_conpaths = _count_needed_conpaths(rd5, mapped_results)
    con_path_ids, route_id, drv_path_id, max_used_obj_id = _next_object_ids_with_conpaths(rd5, n_needed_conpaths)
    drv_path_ids, con_path_blocks = _build_drv_path_with_conpaths(rd5, mapped_results, con_path_ids)
    safe_route_name = rd5_safe_name(route_name or route.name, fallback=f"Route_{route_index}")
    route_length = route.total_length

    lines = list(rd5.lines)
    _patch_scalar(lines, "nObjects", rd5.n_objects + 2 + len(con_path_blocks) if rd5.n_objects else 2 + len(con_path_blocks))
    _patch_scalar(lines, "nRoutes", max(rd5.n_routes, route_index) + 1)
    _insert_route_length(lines, route_index, route_length)
    _insert_con_path_blocks(lines, con_path_blocks)
    _insert_route_block(lines, route_index, route_id, drv_path_id, safe_route_name, drv_path_ids)
    if not _patch_scalar(lines, "MaxUsedObjId", max_used_obj_id):
        lines.append(f"MaxUsedObjId = {max_used_obj_id}")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    result = Rd5RouteWriteResult(
        output_path=output_path,
        route_index=route_index,
        route_id=route_id,
        drv_path_id=drv_path_id,
        route_name=safe_route_name,
        route_length=route_length,
        lane_path_ids=lane_path_ids,
        drv_path_ids=drv_path_ids,
        mapped_results=mapped_results,
        skipped_results=skipped_results,
        report="",
    )
    result.report = build_rd5_write_report(result)
    return result


def build_mapping_report(rd5: Rd5Road, route: PlannedRoute, results: list[Rd5MapResult]) -> str:
    ok_count = sum(1 for result in results if result.ok or result.status == "ok_ambiguous")
    lines = [
        "# RD5 Mapping Report",
        "",
        "## RD5",
        "",
        "```text",
        rd5.summary(),
        "```",
        "",
        "## Route",
        "",
        f"- Name: `{route.name}`",
        f"- SUMO lane steps: `{len(route.steps)}`",
        f"- Mapped steps: `{ok_count}/{len(results)}`",
        f"- Proposed DrvPath: `{' '.join(lane_path_sequence(results))}`",
        "",
        "| # | SUMO lane | XODR road/lane | RD5 Link | Lane Object | LanePath | Status |",
        "|---:|---|---|---|---|---|---|",
    ]
    for index, result in enumerate(results, start=1):
        lines.append(
            f"| {index} | `{result.lane_id}` | `{result.xodr_road_id or ''}/{result.xodr_lane_id or ''}` | "
            f"`{result.rd5_link_id or ''}` | `{result.rd5_lane_object_id or ''}` | "
            f"`{result.rd5_lane_path_id or ''}` | `{result.status}` |"
        )
    missing = [result for result in results if not (result.ok or result.status == "ok_ambiguous")]
    if missing:
        lines.extend(["", "## Missing / Warnings", ""])
        for result in missing:
            lines.append(f"- `{result.lane_id}` {result.xodr_road_id}/{result.xodr_lane_id}: {result.message}")
    return "\n".join(lines) + "\n"
