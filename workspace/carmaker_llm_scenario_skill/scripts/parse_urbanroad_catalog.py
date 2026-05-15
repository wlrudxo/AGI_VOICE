#!/usr/bin/env python3
"""Build a generation catalog for UrbanRoad_RuralRoad_Expressway.rd5.

The catalog is intentionally practical: it combines rd5 topology, IPG example
TestRun actor placements, and our manual CarMaker feedback into one allow-list
that the generator can consume.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path("workspace/carmaker_llm_scenario_skill")
DEFAULT_ROAD = Path(
    "/mnt/c/IPG/carmaker/win64-15.0.1/Data/Road/Examples/Synthetic/Scenario/UrbanRoad_RuralRoad_Expressway.rd5"
)
DEFAULT_TESTRUNS = (
    Path(
        "/mnt/c/IPG/carmaker/win64-15.0.1/Data/TestRun/Examples/DriverAssistance/BrakingAssist/AEB_CrossingCarIntersection"
    ),
    Path(
        "/mnt/c/IPG/carmaker/win64-15.0.1/Data/TestRun/Examples/DriverAssistance/BrakingAssist/AEB_CrossingPedestrianCity"
    ),
    Path(
        "/mnt/c/IPG/carmaker/win64-15.0.1/Data/TestRun/Examples/BasicFunctions/Traffic/Man_AutonomousJunctions"
    ),
)
DEFAULT_OUT = ROOT / "reports" / "urbanroad_catalog"

KEY_VALUE_RE = re.compile(r"^([^#:\s][^:=]*?)\s*=\s*(.*)$")
ROUTE_KEY_RE = re.compile(r"^Route\.(\d+)\.(ID|Name|Length|DrvPath\.ID)$")
JUNCTION_KEY_RE = re.compile(r"^Junction\.(\d+)\.(.+)$")
TOP_RL_KEY_RE = re.compile(r"^RL\.(\d+)\.(.+)$")
TRAFFIC_KEY_RE = re.compile(r"^Traffic\.(\d+)\.(.+)$")
LANEPATH_KEY_RE = re.compile(r"^LanePath\.(\d+)$")


MANUAL_FEEDBACK: list[dict[str, Any]] = [
    {
        "id": "CMASM_004_crossing_with_oncoming",
        "status": "intentional_conflict",
        "routes": [4235, 4236, 4232],
        "tags": ["validated", "visible", "conflict", "collision_observed"],
        "note": "Ego route 4235 and crossing target route 4236 are the IPG AEB conflict pair. Collision can be intentional, but scenario naming must say collision-risk.",
    },
    {
        "id": "CMASM_005_bus_occluded_pedestrian",
        "status": "failed_visibility",
        "routes": [4235, 4229, 4228],
        "tags": ["not_visible", "stops_at_18s", "needs_segment_context"],
        "note": "User reported bus and pedestrian not visible; ego stopped around 18 s. Treat copied bus/ped blocks as local to another viewpoint until revalidated.",
    },
    {
        "id": "CMASM_006_multi_pedestrian_crosswalk",
        "status": "failed_visibility",
        "routes": [4235, 4228, 4225, 4229],
        "tags": ["not_visible", "wrong_speed_context", "needs_segment_context"],
        "note": "User reported pedestrians not visible and ego around 30 kph; do not compose these pedestrian routes with ego route 4235 start 200 without a validated viewpoint.",
    },
    {
        "id": "CMASM_007_cyclist_and_crossing_car",
        "status": "partial_visibility",
        "routes": [4235, 4236, 4233],
        "tags": ["crossing_car_visible", "cyclist_not_visible"],
        "note": "Crossing car is visible, cyclist on route 4233 at s=1311.25 is not visible from the chosen ego segment.",
    },
    {
        "id": "CMASM_008_dense_urban_background",
        "status": "syntax_abort",
        "routes": [4235, 4236, 4226, 4227, 4234],
        "tags": ["name_length_error", "not_validated"],
        "note": "CarMaker traffic names are effectively limited to 8 characters. Long names were truncated and duplicate truncations caused Too many warnings abort.",
    },
    {
        "id": "CMASM_009_late_near_miss_crossing",
        "status": "no_conflict",
        "routes": [4235, 4236],
        "tags": ["visible", "validated", "no_conflict"],
        "note": "Scenario ran but had no collision risk; route pair is usable, timing is not a conflict recipe.",
    },
    {
        "id": "CMASM_010_static_clutter_pedestrian",
        "status": "syntax_abort",
        "routes": [4235, 4229, 269],
        "tags": ["name_length_error", "not_validated"],
        "note": "Same >8-character traffic-name failure as CMASM_008. Static clutter positions also need visible-segment validation.",
    },
]


GENERATION_LIBRARY: list[dict[str, Any]] = [
    {
        "key": "aeb_crossing_vehicle_cross_ob",
        "source": "AEB_CrossingCarIntersection",
        "source_index": 0,
        "actor_name": "cross_ob",
        "short_name": "cross01",
        "actor_type": "vehicle",
        "ego_route_id": 4235,
        "ego_start": "200.00 0",
        "route_id": 4236,
        "start_pos": "55.00 0",
        "speed_kmh": 30,
        "tags": ["visible", "validated", "conflict"],
        "note": "Primary verified AEB crossing target. Conflict timing is controlled by ego speed and target start around route 4236 s=55.",
    },
    {
        "key": "aeb_crossing_vehicle_fast",
        "source": "AEB_CrossingCarIntersection",
        "source_index": 0,
        "actor_name": "cross_ob",
        "short_name": "cross02",
        "actor_type": "vehicle",
        "ego_route_id": 4235,
        "ego_start": "200.00 0",
        "route_id": 4236,
        "start_pos": "42.00 0",
        "speed_kmh": 45,
        "tags": ["visible", "validated", "conflict", "derived_timing"],
        "note": "Derived from the same verified route pair; user validation showed route pair works, but exact severity depends on timing.",
    },
    {
        "key": "aeb_crossing_vehicle_late_no_conflict",
        "source": "CMASM_009_late_near_miss_crossing",
        "source_index": 0,
        "actor_name": "late_crossing_beetle",
        "short_name": "cross09",
        "actor_type": "vehicle",
        "ego_route_id": 4235,
        "ego_start": "200.00 0",
        "route_id": 4236,
        "start_pos": "75.00 0",
        "speed_kmh": 25,
        "tags": ["visible", "validated", "no_conflict"],
        "note": "Usable as non-conflict control only.",
    },
    {
        "key": "aeb_oncoming_background",
        "source": "AEB_CrossingCarIntersection",
        "source_index": 1,
        "actor_name": "Oncoming",
        "short_name": "oncom01",
        "actor_type": "vehicle",
        "ego_route_id": 4235,
        "ego_start": "200.00 0",
        "route_id": 4232,
        "start_pos": "0.00 0",
        "speed_kmh": 50,
        "tags": ["visible", "validated", "background"],
        "note": "Background vehicle from IPG example; not a primary conflict actor.",
    },
    {
        "key": "aeb_pedestrian_same_route_cross_ob",
        "source": "AEB_CrossingPedestrianCity",
        "source_index": 0,
        "actor_name": "cross_ob",
        "short_name": "pedx01",
        "actor_type": "pedestrian",
        "ego_route_id": 4235,
        "ego_start": "200.00 0",
        "route_id": 4235,
        "start_pos": "400.00 -2.5",
        "speed_kmh": 0,
        "tags": ["visible", "validated", "conflict", "needs_source_block"],
        "note": "IPG pedestrian AEB target. Current native generator template is car-intersection based, so this requires importing the PedestrianCity actor block before generation.",
    },
]


def parse_values(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = KEY_VALUE_RE.match(raw.rstrip())
        if match:
            values[match.group(1).strip()] = match.group(2).strip()
    return values


def collect_block_list(lines: list[str], prefix: str) -> list[int]:
    items: list[int] = []
    in_block = False
    for raw in lines:
        stripped = raw.strip()
        if stripped == f"{prefix}:":
            in_block = True
            continue
        if in_block:
            if not raw.startswith("\t") or not stripped:
                break
            try:
                items.append(int(stripped.split()[0]))
            except ValueError:
                continue
    return items


def parse_float_pair(value: str) -> list[float] | None:
    parts = value.split()
    if len(parts) < 2:
        return None
    try:
        return [float(parts[0]), float(parts[1])]
    except ValueError:
        return None


def classify_template(template: str) -> str:
    lowered = template.lower()
    if "pedestrian" in lowered:
        return "pedestrian"
    if "cyclist" in lowered or "biker" in lowered:
        return "cyclist"
    if "vehicle" in lowered or "truck" in lowered or "bus" in lowered:
        return "vehicle"
    return "unknown"


def parse_road(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    values = parse_values(path)

    lane_paths: dict[int, dict[str, Any]] = {}
    for key, value in values.items():
        match = LANEPATH_KEY_RE.match(key)
        if not match:
            continue
        parts = value.split()
        if len(parts) < 3:
            continue
        try:
            lane_path_id = int(parts[0])
            road_link_index = int(parts[1])
            lane_id = int(parts[2])
        except ValueError:
            continue
        lane_paths[lane_path_id] = {
            "index": int(match.group(1)),
            "id": lane_path_id,
            "road_link_index": road_link_index,
            "lane_id": lane_id,
            "raw": value,
        }

    route_indices = sorted(
        {int(match.group(1)) for key in values for match in [ROUTE_KEY_RE.match(key)] if match}
    )
    routes: list[dict[str, Any]] = []
    for idx in route_indices:
        drv_path = collect_block_list(lines, f"Route.{idx}.DrvPath")
        lane_path_details = [lane_paths[path_id] for path_id in drv_path if path_id in lane_paths]
        route = {
            "index": idx,
            "id": int(values.get(f"Route.{idx}.ID", "-1")),
            "name": values.get(f"Route.{idx}.Name", ""),
            "length_m": float(values.get(f"Route.{idx}.Length", "0")),
            "drv_path_id": values.get(f"Route.{idx}.DrvPath.ID", ""),
            "drv_path": drv_path,
            "lane_path_details": lane_path_details,
            "road_link_indices": [item["road_link_index"] for item in lane_path_details],
            "example_usage": [],
            "feedback_tags": [],
        }
        routes.append(route)

    junction_indices = sorted(
        {int(match.group(1)) for key in values for match in [JUNCTION_KEY_RE.match(key)] if match}
    )
    junctions: list[dict[str, Any]] = []
    link_to_junction: dict[int, dict[str, Any]] = {}
    rl_to_junction: dict[int, dict[str, Any]] = {}
    for idx in junction_indices:
        prefix = f"Junction.{idx}"
        links: list[dict[str, Any]] = []
        rls: list[dict[str, Any]] = []
        arms: list[dict[str, Any]] = []
        link_numbers = sorted(
            {
                int(m.group(1))
                for key in values
                for m in [re.match(rf"^{re.escape(prefix)}\.Link\.(\d+)\.ID$", key)]
                if m
            }
        )
        for link_no in link_numbers:
            ids = [int(x) for x in values.get(f"{prefix}.Link.{link_no}.ID", "").split() if x.lstrip("-").isdigit()]
            link_value = values.get(f"{prefix}.Link.{link_no}", "")
            link = {"index": link_no, "ids": ids, "value": link_value}
            links.append(link)
            for link_id in ids:
                link_to_junction[link_id] = {"junction_index": idx, "junction_id": values.get(f"{prefix}.ID", ""), "link_index": link_no}
        rl_numbers = sorted(
            {
                int(m.group(1))
                for key in values
                for m in [re.match(rf"^{re.escape(prefix)}\.RL\.(\d+)\.ID$", key)]
                if m
            }
        )
        for rl_no in rl_numbers:
            ids = [int(x) for x in values.get(f"{prefix}.RL.{rl_no}.ID", "").split() if x.lstrip("-").isdigit()]
            rl_value = values.get(f"{prefix}.RL.{rl_no}", "")
            rl = {
                "index": rl_no,
                "ids": ids,
                "value": rl_value,
                "ref_object": values.get(f"{prefix}.RL.{rl_no}.RefObject", ""),
                "segment_type": values.get(f"{prefix}.RL.{rl_no}.Seg.0.Type", ""),
            }
            rls.append(rl)
            for rl_id in ids:
                rl_to_junction[rl_id] = {"junction_index": idx, "junction_id": values.get(f"{prefix}.ID", ""), "rl_index": rl_no}
        arm_numbers = sorted(
            {
                int(m.group(1))
                for key in values
                for m in [re.match(rf"^{re.escape(prefix)}\.Arm\.(\d+)\.ID$", key)]
                if m
            }
        )
        for arm_no in arm_numbers:
            arm_ids = [int(x) for x in values.get(f"{prefix}.Arm.{arm_no}.ID", "").split() if x.lstrip("-").isdigit()]
            arms.append({"index": arm_no, "ids": arm_ids, "value": values.get(f"{prefix}.Arm.{arm_no}", "")})
        junctions.append(
            {
                "index": idx,
                "id": int(values.get(f"{prefix}.ID", "-1")),
                "type": values.get(f"{prefix}.Type", ""),
                "knot_xy": parse_float_pair(values.get(f"{prefix}.Knot", "")),
                "rst": values.get(f"{prefix}.RST", ""),
                "main_arms": values.get(f"{prefix}.MainArms", ""),
                "arms": arms,
                "rls": rls,
                "links": links,
            }
        )

    controls = []
    for key, value in sorted(values.items()):
        if key.startswith("Control.TrfLight."):
            parts = value.split()
            controls.append({"kind": "traffic_light", "key": key, "raw": value, "object_id": parts[0] if parts else "", "name": parts[1] if len(parts) > 1 else ""})
        elif key.startswith("Control.RightOfWay."):
            controls.append({"kind": "right_of_way", "key": key, "raw": value, "object_id": "", "name": "RightOfWay"})

    mounts = []
    mount_keywords = ("PedestrianCrossing", "TrfLight", "Stop", "SpeedLimit", "GiveWay", "RightOfWay")
    for key, value in sorted(values.items()):
        if ".Mount." not in key:
            continue
        if any(token in value for token in mount_keywords):
            rl_match = TOP_RL_KEY_RE.match(key)
            mounts.append({"key": key, "rl_index": int(rl_match.group(1)) if rl_match else None, "raw": value})

    for route in routes:
        related = []
        for obj_id in route["drv_path"]:
            if obj_id in link_to_junction:
                related.append({"object_id": obj_id, "type": "link", **link_to_junction[obj_id]})
            elif obj_id in rl_to_junction:
                related.append({"object_id": obj_id, "type": "rl", **rl_to_junction[obj_id]})
        route["junction_path"] = related
        route_rls = set(route["road_link_indices"])
        route["mounted_assets"] = [mount for mount in mounts if mount["rl_index"] in route_rls]
        route["control_path_refs"] = [
            control
            for control in controls
            if any(f" {path_id}" in f" {control['raw']} " for path_id in route["drv_path"])
        ]

    return {
        "source": str(path),
        "counts": {
            "routes": len(routes),
            "junctions": len(junctions),
            "traffic_lights": sum(1 for control in controls if control["kind"] == "traffic_light"),
            "right_of_way_entries": sum(1 for control in controls if control["kind"] == "right_of_way"),
            "mounted_control_assets": len(mounts),
            "lane_paths": len(lane_paths),
        },
        "lane_paths": sorted(lane_paths.values(), key=lambda item: item["id"]),
        "routes": routes,
        "junctions": junctions,
        "controls": controls,
        "mounted_assets": mounts,
    }


def parse_testrun(path: Path) -> dict[str, Any]:
    values = parse_values(path)
    traffic_indices = sorted(
        {int(match.group(1)) for key in values for match in [TRAFFIC_KEY_RE.match(key)] if match}
    )
    actors = []
    for idx in traffic_indices:
        prefix = f"Traffic.{idx}"
        template = values.get(f"{prefix}.Template.FName", "")
        actors.append(
            {
                "index": idx,
                "name": values.get(f"{prefix}.Name", ""),
                "template": template,
                "actor_type": classify_template(template),
                "route_id": values.get(f"{prefix}.Routing.ObjId", ""),
                "start_pos": values.get(f"{prefix}.StartPos", ""),
                "orientation": values.get(f"{prefix}.StartPos.Orientation", ""),
                "speed_kmh": values.get(f"{prefix}.Man.Start.Velocity", ""),
                "maneuver_count": values.get(f"{prefix}.nMan", ""),
            }
        )
    return {
        "name": path.name,
        "path": str(path),
        "road": values.get("Road.FName", ""),
        "ego": {
            "route_id": values.get("Vehicle.Routing.ObjId", ""),
            "start_pos": values.get("Vehicle.StartPos", ""),
            "speed_kmh": values.get("DrivMan.Man.Start.Velocity", ""),
        },
        "traffic_count": len(actors),
        "actors": actors,
    }


def overlay_usage(road: dict[str, Any], examples: list[dict[str, Any]]) -> None:
    route_by_id = {route["id"]: route for route in road["routes"]}
    for example in examples:
        ego_route = example["ego"]["route_id"]
        if ego_route.isdigit() and int(ego_route) in route_by_id:
            route_by_id[int(ego_route)]["example_usage"].append({"source": example["name"], "role": "ego", "start_pos": example["ego"]["start_pos"]})
        for actor in example["actors"]:
            route_id = actor["route_id"]
            if route_id.isdigit() and int(route_id) in route_by_id:
                route_by_id[int(route_id)]["example_usage"].append(
                    {
                        "source": example["name"],
                        "role": actor["actor_type"],
                        "actor": actor["name"],
                        "start_pos": actor["start_pos"],
                        "speed_kmh": actor["speed_kmh"],
                    }
                )
    for feedback in MANUAL_FEEDBACK:
        for route_id in feedback["routes"]:
            if route_id in route_by_id:
                route_by_id[route_id]["feedback_tags"].extend(feedback["tags"])
    for route in road["routes"]:
        route["feedback_tags"] = sorted(set(route["feedback_tags"]))


def build_markdown(catalog: dict[str, Any]) -> str:
    road = catalog["road"]
    lines = [
        "# UrbanRoad Catalog",
        "",
        "Source map: `Examples/Synthetic/Scenario/UrbanRoad_RuralRoad_Expressway.rd5`.",
        "",
        "This catalog is the current allow-list for native CarMaker scenario generation. Use `generation_library` entries tagged `visible` and `validated`; require `conflict` when the scenario target is a crash/near-crash.",
        "",
        "## Counts",
        "",
        f"- Routes: {road['counts']['routes']}",
        f"- Junctions: {road['counts']['junctions']}",
        f"- Lane paths: {road['counts']['lane_paths']}",
        f"- Traffic lights: {road['counts']['traffic_lights']}",
        f"- Right-of-way control entries: {road['counts']['right_of_way_entries']}",
        f"- Mounted control assets: {road['counts']['mounted_control_assets']}",
        "",
        "## Generation Allow-List",
        "",
        "| Key | Actor | Ego route/start | Actor route/start | Speed | Tags | Note |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in catalog["generation_library"]:
        tags = ", ".join(item["tags"])
        lines.append(
            f"| `{item['key']}` | {item['actor_type']} `{item['short_name']}` | {item['ego_route_id']} / `{item['ego_start']}` | {item['route_id']} / `{item['start_pos']}` | {item['speed_kmh']} | {tags} | {item['note']} |"
        )

    lines.extend(
        [
            "",
            "## Route Catalog",
            "",
            "| Route ID | Index | Length m | LanePath IDs | RL Indices | Route Assets | Example Usage | Feedback Tags |",
            "| --- | ---: | ---: | --- | --- | --- | --- | --- |",
        ]
    )
    for route in road["routes"]:
        usage = "; ".join(
            f"{entry['source']}:{entry['role']}:{entry.get('actor', 'ego')}@{entry['start_pos']}"
            for entry in route["example_usage"][:8]
        )
        feedback = ", ".join(route["feedback_tags"])
        rl_indices = " ".join(str(x) for x in route["road_link_indices"])
        assets = "; ".join(
            f"RL{asset['rl_index']}:{asset['raw'].split()[10] if len(asset['raw'].split()) > 10 else asset['raw']}"
            for asset in route.get("mounted_assets", [])[:6]
        )
        path_ids = " ".join(str(x) for x in route["drv_path"])
        lines.append(
            f"| {route['id']} | {route['index']} | {route['length_m']:.1f} | `{path_ids}` | `{rl_indices}` | {assets} | {usage} | {feedback} |"
        )

    lines.extend(
        [
            "",
            "## Junction Catalog",
            "",
            "| Index | ID | Type | RST | Knot XY | Arms | Links | RLs |",
            "| ---: | ---: | --- | --- | --- | ---: | ---: | ---: |",
        ]
    )
    for junction in road["junctions"]:
        knot = "" if junction["knot_xy"] is None else f"{junction['knot_xy'][0]:.2f}, {junction['knot_xy'][1]:.2f}"
        lines.append(
            f"| {junction['index']} | {junction['id']} | {junction['type']} | {junction['rst']} | {knot} | {len(junction['arms'])} | {len(junction['links'])} | {len(junction['rls'])} |"
        )

    lines.extend(["", "## Traffic Lights", "", "| Key | Object | Name | Raw |", "| --- | --- | --- | --- |"])
    for control in road["controls"]:
        if control["kind"] != "traffic_light":
            continue
        lines.append(f"| `{control['key']}` | {control['object_id']} | {control['name']} | `{control['raw']}` |")

    lines.extend(
        [
            "",
            "## Example TestRun Overlay",
            "",
            "| TestRun | Ego | Actors | Notes |",
            "| --- | --- | ---: | --- |",
        ]
    )
    for example in catalog["examples"]:
        actor_preview = ", ".join(f"{a['name']}:{a['actor_type']}@R{a['route_id']} {a['start_pos']}" for a in example["actors"][:10])
        lines.append(
            f"| `{example['name']}` | R{example['ego']['route_id']} `{example['ego']['start_pos']}`, {example['ego']['speed_kmh']} km/h | {example['traffic_count']} | {actor_preview} |"
        )

    lines.extend(
        [
            "",
            "## Manual Feedback Overlay",
            "",
            "| Scenario | Status | Routes | Tags | Interpretation |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for feedback in catalog["manual_feedback"]:
        lines.append(
            f"| `{feedback['id']}` | {feedback['status']} | {', '.join(str(x) for x in feedback['routes'])} | {', '.join(feedback['tags'])} | {feedback['note']} |"
        )

    lines.extend(
        [
            "",
            "## Current Generation Rules",
            "",
            "- Traffic actor `Name` must be unique and 8 characters or shorter.",
            "- Default generator inputs must come from `generation_library` entries containing both `visible` and `validated`.",
            "- Collision-risk scenarios must include at least one actor placement tagged `conflict`.",
            "- Pedestrian/cyclist placements copied from unrelated example viewpoints are not allowed until they get a visible validation tag for the same ego route/start.",
            "- The IPG pedestrian `cross_ob` from `AEB_CrossingPedestrianCity` is valid but requires importing that TestRun actor block; the current car-intersection template cannot synthesize it from the vehicle block alone.",
            "",
        ]
    )
    return "\n".join(lines)


def build_catalog(road_path: Path, testruns: tuple[Path, ...]) -> dict[str, Any]:
    road = parse_road(road_path)
    examples = [parse_testrun(path) for path in testruns if path.is_file()]
    overlay_usage(road, examples)
    return {
        "schema_version": 1,
        "road": road,
        "examples": examples,
        "manual_feedback": MANUAL_FEEDBACK,
        "generation_library": GENERATION_LIBRARY,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--road", type=Path, default=DEFAULT_ROAD)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    catalog = build_catalog(args.road, DEFAULT_TESTRUNS)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.out_dir / "urbanroad_catalog.json"
    md_path = args.out_dir / "urbanroad_catalog.md"
    json_path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(build_markdown(catalog), encoding="utf-8")
    print(json_path)
    print(md_path)


if __name__ == "__main__":
    main()
