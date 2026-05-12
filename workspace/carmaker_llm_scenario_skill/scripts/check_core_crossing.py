#!/usr/bin/env python3
"""Check a focused ego/pedestrian crossing acceptance slice."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_summary(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def actor_dyns(actor: dict[str, Any]) -> set[str]:
    return {step["dyn"].split()[0] for step in actor["steps"] if step["dyn"]}


def check(summary: dict[str, Any]) -> dict[str, Any]:
    traffic = summary["traffic"]
    pedestrians = [actor for actor in traffic if actor.get("class") == "pedestrian"]
    moving_pedestrians = [
        actor for actor in pedestrians if actor["maneuver_count"] > 0 and "FollowTraj" in actor_dyns(actor)
    ]
    static_or_slow_vehicles = [
        actor for actor in traffic if actor.get("class") == "vehicle" and actor["start_velocity"] in {"", "0", "0.000"}
    ]

    ped_trigger_conditions = []
    for actor in moving_pedestrians:
        ped_trigger_conditions.extend(
            step["start_cond"] for step in actor["steps"] if step.get("start_cond")
        )

    checks = [
        {
            "name": "ego_has_maneuver",
            "pass": summary["ego"]["drivman_count"] >= 1,
            "actual": summary["ego"]["drivman_count"],
        },
        {
            "name": "has_pedestrian",
            "pass": len(pedestrians) >= 1,
            "actual": len(pedestrians),
        },
        {
            "name": "has_moving_pedestrian_followtraj",
            "pass": len(moving_pedestrians) >= 1,
            "actual": len(moving_pedestrians),
        },
        {
            "name": "has_static_or_slow_vehicle_occluder",
            "pass": len(static_or_slow_vehicles) >= 1,
            "actual": len(static_or_slow_vehicles),
        },
        {
            "name": "moving_pedestrian_has_trigger",
            "pass": any("DistToObj" in cond or "sRoad" in cond for cond in ped_trigger_conditions),
            "actual": ped_trigger_conditions,
        },
    ]

    return {
        "source": summary["source"],
        "passed": all(item["pass"] for item in checks),
        "checks": checks,
        "moving_pedestrians": [
            {
                "index": actor["index"],
                "name": actor["name"],
                "template": actor["template"],
                "start_type": actor["start"]["type"],
                "routing_type": actor["routing"]["type"],
                "dyn_types": sorted(actor_dyns(actor)),
            }
            for actor in moving_pedestrians
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Core Crossing Check",
        "",
        f"- Source: `{report['source']}`",
        f"- Overall: `{'PASS' if report['passed'] else 'FAIL'}`",
        "",
        "| Check | Result | Actual |",
        "| --- | --- | --- |",
    ]
    for item in report["checks"]:
        result = "PASS" if item["pass"] else "FAIL"
        actual = json.dumps(item["actual"], ensure_ascii=False, sort_keys=True)
        lines.append(f"| `{item['name']}` | `{result}` | `{actual}` |")
    lines.extend(["", "## Moving Pedestrians", "", "```json"])
    lines.append(json.dumps(report["moving_pedestrians"], indent=2, ensure_ascii=False))
    lines.extend(["```", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("summary", type=Path)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()

    report = check(load_summary(args.summary))
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.md_out:
        args.md_out.parent.mkdir(parents=True, exist_ok=True)
        write_markdown(report, args.md_out)
    if not args.json_out and not args.md_out:
        print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
