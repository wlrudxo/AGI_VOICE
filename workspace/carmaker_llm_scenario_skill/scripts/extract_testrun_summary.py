#!/usr/bin/env python3
"""Extract a structured summary from a CarMaker TestRun InfoFile."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


KEY_VALUE_RE = re.compile(r"^([^#:\s][^:=]*?)\s*=\s*(.*)$")
TRAFFIC_RE = re.compile(r"^Traffic\.(\d+)\.(.+)$")
DRIVMAN_STEP_RE = re.compile(r"^DrivMan\.Man\.(\d+)\.(LongStep|LatStep)\.(\d+)\.Dyn$")
TRAFFIC_STEP_RE = re.compile(
    r"^Traffic\.(\d+)\.Man\.(\d+)\.(LongStep|LatStep)\.(\d+)\.Dyn$"
)


def parse_infofile(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = KEY_VALUE_RE.match(raw.rstrip())
        if not match:
            continue
        values[match.group(1).strip()] = match.group(2).strip()
    return values


def get_int(values: dict[str, str], key: str, default: int = 0) -> int:
    try:
        return int(values.get(key, str(default)))
    except ValueError:
        return default


def collect_ego(values: dict[str, str]) -> dict[str, Any]:
    steps: list[dict[str, Any]] = []
    for key, dyn in values.items():
        match = DRIVMAN_STEP_RE.match(key)
        if not match:
            continue
        man, axis, step = match.groups()
        steps.append(
            {
                "maneuver": int(man),
                "axis": axis,
                "step": int(step),
                "dyn": dyn,
                "limit": values.get(
                    f"DrivMan.Man.{man}.{axis}.{step}.Limit",
                    values.get(f"DrivMan.Man.{man}.{axis}.{step}.TimeLimit", ""),
                ),
                "start_cond": values.get(f"DrivMan.Man.{man}.StartCond", ""),
            }
        )
    steps.sort(key=lambda item: (item["maneuver"], item["axis"], item["step"]))

    return {
        "vehicle": values.get("Vehicle", ""),
        "driver_template": values.get("Vehicle.DriverTemplate.FName", ""),
        "routing": {
            "type": values.get("Vehicle.Routing.Type", ""),
            "obj_id": values.get("Vehicle.Routing.ObjId", ""),
        },
        "start": {
            "type": values.get("Vehicle.StartPos.Type", ""),
            "obj_id": values.get("Vehicle.StartPos.ObjId", ""),
            "value": values.get("Vehicle.StartPos", ""),
            "orientation_type": values.get("Vehicle.StartPos.Orientation.Type", ""),
            "orientation": values.get("Vehicle.StartPos.Orientation", ""),
        },
        "drivman_count": get_int(values, "DrivMan.nMan"),
        "start_velocity": values.get("DrivMan.Man.Start.Velocity", ""),
        "steps": steps,
    }


def parse_template_infofile(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    return parse_infofile(path)


def resolve_template_path(testrun_path: Path, template: str) -> Path | None:
    parts = list(testrun_path.parts)
    try:
        data_index = parts.index("Data")
    except ValueError:
        return None
    project_data = Path(*parts[: data_index + 1])
    return project_data / "Traffic" / "Template" / template


def classify_template(template: str, template_values: dict[str, str] | None = None) -> str:
    template_values = template_values or {}
    structural_hint = " ".join(
        [
            template_values.get("ObjectClass", ""),
            template_values.get("RCSClass", ""),
            template_values.get("Motion.Kind", ""),
            template_values.get("Movie.Geometry", ""),
        ]
    ).lower()
    if any(token in structural_hint for token in ("people", "pedestrian", "cyclist")):
        return "pedestrian"
    if any(token in structural_hint for token in ("vehicle", "coach", "truck", "4wheel")):
        return "vehicle"

    lowered = template.lower()
    if "people" in lowered or "pedestrian" in lowered or "cyclist" in lowered:
        return "pedestrian"
    if "vehicle" in lowered or "car" in lowered or "truck" in lowered or "bus" in lowered:
        return "vehicle"
    return "unknown"


def collect_traffic(values: dict[str, str], testrun_path: Path) -> list[dict[str, Any]]:
    ids = set()
    for key in values:
        match = TRAFFIC_RE.match(key)
        if match:
            ids.add(int(match.group(1)))

    actors: list[dict[str, Any]] = []
    for idx in sorted(ids):
        prefix = f"Traffic.{idx}"
        template = values.get(f"{prefix}.Template.FName", "")
        template_path = resolve_template_path(testrun_path, template)
        template_values = parse_template_infofile(template_path) if template_path else {}
        steps: list[dict[str, Any]] = []
        for key, dyn in values.items():
            match = TRAFFIC_STEP_RE.match(key)
            if not match or int(match.group(1)) != idx:
                continue
            _, man, axis, step = match.groups()
            steps.append(
                {
                    "maneuver": int(man),
                    "axis": axis,
                    "step": int(step),
                    "dyn": dyn,
                    "limit": values.get(f"{prefix}.Man.{man}.{axis}.{step}.Limit", ""),
                    "start_cond": values.get(f"{prefix}.Man.{man}.StartCond", ""),
                }
            )
        steps.sort(key=lambda item: (item["maneuver"], item["axis"], item["step"]))
        actors.append(
            {
                "index": idx,
                "name": values.get(f"{prefix}.Name", ""),
                "template": template,
                "class": classify_template(template, template_values),
                "template_info": {
                    "object_class": template_values.get("ObjectClass", ""),
                    "rcs_class": template_values.get("RCSClass", ""),
                    "motion_kind": template_values.get("Motion.Kind", ""),
                },
                "routing": {
                    "type": values.get(f"{prefix}.Routing.Type", ""),
                    "obj_id": values.get(f"{prefix}.Routing.ObjId", ""),
                },
                "start": {
                    "type": values.get(f"{prefix}.StartPos.Type", ""),
                    "obj_id": values.get(f"{prefix}.StartPos.ObjId", ""),
                    "value": values.get(f"{prefix}.StartPos", ""),
                    "reference": values.get(f"{prefix}.StartPos.Reference", ""),
                    "orientation_type": values.get(
                        f"{prefix}.StartPos.Orientation.Type", ""
                    ),
                    "orientation": values.get(f"{prefix}.StartPos.Orientation", ""),
                },
                "maneuver_count": get_int(values, f"{prefix}.nMan"),
                "start_velocity": values.get(f"{prefix}.Man.Start.Velocity", ""),
                "steps": steps,
            }
        )
    return actors


def summarize(path: Path) -> dict[str, Any]:
    values = parse_infofile(path)
    traffic = collect_traffic(values, path)
    dyn_counter = Counter()
    start_type_counter = Counter()
    template_class_counter = Counter()

    for actor in traffic:
        start_type_counter[actor["start"]["type"]] += 1
        template_class_counter[actor["class"]] += 1
        for step in actor["steps"]:
            if step["dyn"]:
                dyn_counter[step["dyn"].split()[0]] += 1
    for step in collect_ego(values)["steps"]:
        if step["dyn"]:
            dyn_counter[step["dyn"].split()[0]] += 1

    return {
        "source": str(path),
        "file_ident": values.get("FileIdent", ""),
        "file_creator": values.get("FileCreator", ""),
        "description": values.get("Description", ""),
        "road": values.get("Road.FName", ""),
        "ego": collect_ego(values),
        "traffic_count_declared": get_int(values, "Traffic.N"),
        "traffic_count_found": len(traffic),
        "traffic": traffic,
        "feature_counts": {
            "traffic_start_types": dict(sorted(start_type_counter.items())),
            "traffic_template_classes": dict(sorted(template_class_counter.items())),
            "dyn_types": dict(sorted(dyn_counter.items())),
        },
    }


def write_markdown(summary: dict[str, Any], path: Path) -> None:
    lines = [
        f"# TestRun Summary: {Path(summary['source']).name}",
        "",
        f"- Source: `{summary['source']}`",
        f"- Road: `{summary['road']}`",
        f"- Ego vehicle: `{summary['ego']['vehicle']}`",
        f"- Ego routing: `{summary['ego']['routing']['type']} {summary['ego']['routing']['obj_id']}`",
        f"- Ego start: `{summary['ego']['start']['type']} {summary['ego']['start']['value']}`",
        f"- DrivMan.nMan: `{summary['ego']['drivman_count']}`",
        f"- Traffic.N declared/found: `{summary['traffic_count_declared']}` / `{summary['traffic_count_found']}`",
        "",
        "## Feature Counts",
        "",
        "```json",
        json.dumps(summary["feature_counts"], indent=2, ensure_ascii=False),
        "```",
        "",
        "## Traffic Actors",
        "",
        "| Index | Name | Class | Start Type | nMan | Dyn Types | Template |",
        "| ---: | --- | --- | --- | ---: | --- | --- |",
    ]
    for actor in summary["traffic"]:
        dyns = sorted({step["dyn"].split()[0] for step in actor["steps"] if step["dyn"]})
        lines.append(
            "| {index} | `{name}` | {cls} | `{start}` | {nman} | `{dyns}` | `{template}` |".format(
                index=actor["index"],
                name=actor["name"],
                cls=actor.get("class", classify_template(actor["template"])),
                start=actor["start"]["type"],
                nman=actor["maneuver_count"],
                dyns=", ".join(dyns),
                template=actor["template"],
            )
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("testrun", type=Path)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()

    summary = summarize(args.testrun)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(
            json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    if args.md_out:
        args.md_out.parent.mkdir(parents=True, exist_ok=True)
        write_markdown(summary, args.md_out)
    if not args.json_out and not args.md_out:
        print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
