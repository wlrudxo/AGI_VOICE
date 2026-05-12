#!/usr/bin/env python3
"""Parse osc2cm console logs into a structured warning/error summary."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


LOG_RE = re.compile(r"^\[(?P<section>[^\]]+)\](?: \[(?P<context>[^\]]+)\])?(?: \[(?P<level>[^\]]+)\])? (?P<message>.*)$")


def classify(message: str) -> str:
    lowered = message.lower()
    if "failed to validate" in lowered:
        return "validation_failed"
    if "validation finished with" in lowered:
        return "validation_summary"
    if "failed to evaluate the init speed" in lowered:
        return "missing_init_speed"
    if "followingmode = position" in lowered:
        return "following_mode_position"
    if "no declaration found for element 'pedestrian'" in lowered:
        return "unsupported_pedestrian_validation"
    if "attribute" in lowered and "pedestrian" in lowered:
        return "unsupported_pedestrian_validation"
    if "value '" in lowered and "does not match any member types" in lowered:
        return "unsupported_enum_value"
    if "failed to evaluate" in lowered:
        return "position_evaluation_failed"
    if "invalid maneuver definition" in lowered:
        return "invalid_maneuver_definition"
    return "other"


def severity(record: dict[str, str]) -> str:
    level = record.get("level", "").lower()
    message = record["message"].lower()
    if level in {"fatal", "error"}:
        return "error"
    if "failed to validate the openscenario file with osc2cm supported features" in message:
        return "warning"
    if "failed to evaluate" in message or "invalid maneuver definition" in message:
        return "warning"
    if "does not match" in message or "not supported" in message:
        return "warning"
    if "no declaration found" in message or "is not declared" in message or "is not allowed" in message:
        return "warning"
    if "warning" in level:
        return "warning"
    return "info"


def parse_log(path: Path) -> dict[str, Any]:
    records: list[dict[str, str]] = []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        match = LOG_RE.match(raw)
        if not match:
            continue
        record = {
            "line": line_no,
            "section": match.group("section") or "",
            "context": match.group("context") or "",
            "level": match.group("level") or "",
            "message": match.group("message") or "",
        }
        record["class"] = classify(record["message"])
        record["severity"] = severity(record)
        records.append(record)

    warning_records = [record for record in records if record["severity"] == "warning"]
    error_records = [record for record in records if record["severity"] == "error"]
    return {
        "source": str(path),
        "status": "error" if error_records else ("warning" if warning_records else "clean"),
        "counts": {
            "records": len(records),
            "warnings": len(warning_records),
            "errors": len(error_records),
            "by_class": dict(sorted(Counter(record["class"] for record in warning_records + error_records).items())),
        },
        "issues": warning_records + error_records,
    }


def write_markdown(summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# osc2cm Log Summary",
        "",
        f"- Source: `{summary['source']}`",
        f"- Status: `{summary['status']}`",
        f"- Warnings: `{summary['counts']['warnings']}`",
        f"- Errors: `{summary['counts']['errors']}`",
        "",
        "## Issue Counts",
        "",
        "```json",
        json.dumps(summary["counts"]["by_class"], indent=2, ensure_ascii=False),
        "```",
        "",
        "## Issues",
        "",
        "| Line | Severity | Class | Section | Context | Message |",
        "| ---: | --- | --- | --- | --- | --- |",
    ]
    for issue in summary["issues"]:
        message = issue["message"].replace("|", "\\|")
        lines.append(
            f"| {issue['line']} | `{issue['severity']}` | `{issue['class']}` | `{issue['section']}` | `{issue['context']}` | {message} |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("log", type=Path)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()

    summary = parse_log(args.log)
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
