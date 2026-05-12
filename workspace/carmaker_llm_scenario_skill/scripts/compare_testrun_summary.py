#!/usr/bin/env python3
"""Compare two structured CarMaker TestRun summaries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_summary(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def actor_signature(actor: dict[str, Any]) -> dict[str, Any]:
    dyn_types = sorted({step["dyn"].split()[0] for step in actor["steps"] if step["dyn"]})
    return {
        "class": actor.get("class") or classify_template(actor["template"]),
        "start_type": actor["start"]["type"],
        "routing_type": actor["routing"]["type"],
        "maneuver_count": actor["maneuver_count"],
        "dyn_types": dyn_types,
    }


def classify_template(template: str) -> str:
    lowered = template.lower()
    if "people" in lowered or "pedestrian" in lowered:
        return "pedestrian"
    if "vehicle" in lowered or "car" in lowered or "truck" in lowered or "bus" in lowered:
        return "vehicle"
    return "unknown"


def compare(reference: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def add_check(name: str, expected: Any, actual: Any) -> None:
        checks.append(
            {
                "name": name,
                "pass": expected == actual,
                "expected": expected,
                "actual": actual,
            }
        )

    add_check("road", reference["road"], candidate["road"])
    add_check(
        "ego.routing.type",
        reference["ego"]["routing"]["type"],
        candidate["ego"]["routing"]["type"],
    )
    add_check(
        "ego.start.type",
        reference["ego"]["start"]["type"],
        candidate["ego"]["start"]["type"],
    )
    add_check(
        "ego.drivman_count",
        reference["ego"]["drivman_count"],
        candidate["ego"]["drivman_count"],
    )
    add_check(
        "traffic_count_found",
        reference["traffic_count_found"],
        candidate["traffic_count_found"],
    )
    add_check(
        "traffic_start_types",
        reference["feature_counts"]["traffic_start_types"],
        candidate["feature_counts"]["traffic_start_types"],
    )
    add_check(
        "traffic_template_classes",
        reference["feature_counts"]["traffic_template_classes"],
        candidate["feature_counts"]["traffic_template_classes"],
    )
    add_check(
        "dyn_types",
        reference["feature_counts"]["dyn_types"],
        candidate["feature_counts"]["dyn_types"],
    )

    reference_actors = [actor_signature(actor) for actor in reference["traffic"]]
    candidate_actors = [actor_signature(actor) for actor in candidate["traffic"]]
    add_check("traffic_actor_signature_sequence", reference_actors, candidate_actors)

    return {
        "reference": reference["source"],
        "candidate": candidate["source"],
        "passed": all(check["pass"] for check in checks),
        "checks": checks,
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# TestRun Comparison",
        "",
        f"- Reference: `{report['reference']}`",
        f"- Candidate: `{report['candidate']}`",
        f"- Overall: `{'PASS' if report['passed'] else 'FAIL'}`",
        "",
        "| Check | Result | Expected | Actual |",
        "| --- | --- | --- | --- |",
    ]
    for check in report["checks"]:
        result = "PASS" if check["pass"] else "FAIL"
        expected = json.dumps(check["expected"], ensure_ascii=False, sort_keys=True)
        actual = json.dumps(check["actual"], ensure_ascii=False, sort_keys=True)
        lines.append(f"| `{check['name']}` | `{result}` | `{expected}` | `{actual}` |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("reference", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()

    report = compare(load_summary(args.reference), load_summary(args.candidate))
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    if args.md_out:
        args.md_out.parent.mkdir(parents=True, exist_ok=True)
        write_markdown(report, args.md_out)
    if not args.json_out and not args.md_out:
        print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
