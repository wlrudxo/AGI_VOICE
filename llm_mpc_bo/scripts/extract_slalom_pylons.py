#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any


def parse_pylons(testrun_path: Path) -> list[dict[str, Any]]:
    text = testrun_path.read_text(encoding="utf-8", errors="replace")
    pylons = []
    pattern = re.compile(
        r"Road\.RL\.(\d+)\.Marker\.(\d+)\.Type = (.+?)\s*\n"
        r"Road\.RL\.\1\.Marker\.\2\.Param = ([^\n]+)",
        flags=re.MULTILINE,
    )
    for match in pattern.finditer(text):
        marker_type = match.group(3).strip()
        if marker_type != "DrvPylon":
            continue
        raw_params = match.group(4).split()
        params = [to_number(item) for item in raw_params]
        if len(params) < 6 or not all(isinstance(item, float) for item in (params[0], params[2], params[5])):
            raise ValueError(f"Unsupported DrvPylon Param format: {' '.join(raw_params)}")

        s_road = float(params[0])
        gate_center_y = float(params[2])
        gate_width = float(params[5])
        half_width = gate_width / 2.0
        for pylon_side, lateral_y in (("lower", gate_center_y - half_width), ("upper", gate_center_y + half_width)):
            pylons.append(
                {
                    "roadLayer": int(match.group(1)),
                    "markerIndex": int(match.group(2)),
                    "pylonSide": pylon_side,
                    "type": marker_type,
                    "sRoad": s_road,
                    "x": s_road,
                    "y": lateral_y,
                    "gateCenterY": gate_center_y,
                    "gateWidth": gate_width,
                    "isGateCenter": False,
                    "isSlalomSideGate": abs(gate_center_y) > 1.0,
                    "rawParam": " ".join(raw_params),
                }
            )
    return pylons


def to_number(value: str) -> float | str:
    try:
        return float(value)
    except ValueError:
        return value


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract DrvPylon marker positions from a CarMaker TestRun.")
    parser.add_argument("testrun", type=Path)
    parser.add_argument("--csv", type=Path)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()

    pylons = parse_pylons(args.testrun)
    if args.csv:
        write_csv(args.csv, pylons)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(pylons, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(pylons, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
