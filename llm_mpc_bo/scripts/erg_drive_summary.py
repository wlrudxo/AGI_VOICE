#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TYPE_FORMATS = {
    "Double": "d",
    "Float": "f",
    "Int": "i",
    "4 Bytes": "4s",
}

DEFAULT_QUANTITIES = [
    "Time",
    "Vhcl.sRoad",
    "Vhcl.tRoad",
    "Vhcl.YawRate",
    "Car.Road.Path.DevAng",
    "Car.Road.Path.DevDist",
    "Car.Road.Route.DevAng",
    "Car.Road.Route.DevDist",
    "Car.tx",
    "Car.ty",
    "Car.v",
    "Car.YawRate",
    "Car.SideSlipAngle",
    "Car.ax",
    "Car.ay",
    "DM.Steer.Ang",
    "DM.Steer.AngVel",
    "DM.Steer.AngAcc",
    "Steer.WhlAng",
    "Driver.Lat.dy",
    "DM.Brake",
    "DM.Gas",
    "Car.muRoadFL",
    "Car.muRoadFR",
    "Car.muRoadRL",
    "Car.muRoadRR",
]


@dataclass(frozen=True)
class Quantity:
    index: int
    name: str
    typ: str
    unit: str | None = None


def parse_info(info_path: Path) -> tuple[list[Quantity], dict[str, Any]]:
    text = info_path.read_text(encoding="utf-8", errors="replace")
    by_index: dict[int, dict[str, str]] = {}
    units: dict[str, str] = {}

    for match in re.finditer(r"File\.At\.(\d+)\.(Name|Type) = (.+)", text):
        index = int(match.group(1))
        by_index.setdefault(index, {})[match.group(2)] = match.group(3).strip()

    for match in re.finditer(r"Quantity\.([^\n]+?)\.Unit = (.+)", text):
        units[match.group(1).strip()] = match.group(2).strip()

    quantities = []
    for index in sorted(by_index):
        item = by_index[index]
        if "Name" not in item or "Type" not in item:
            raise ValueError(f"Incomplete File.At.{index} entry in {info_path}")
        if item["Type"] not in TYPE_FORMATS:
            raise ValueError(f"Unsupported ERG type {item['Type']!r} at File.At.{index}")
        quantities.append(
            Quantity(
                index=index,
                name=item["Name"],
                typ=item["Type"],
                unit=units.get(item["Name"]),
            )
        )

    metadata = {
        "testrun": extract_first(r"^Testrun = (.+)$", text),
        "date_local": extract_first(r"^File\.DateLocal = (.+)$", text),
        "delta_t": parse_float(extract_first(r"^SimParam\.DeltaT = (.+)$", text)),
        "pylon_hits": parse_pylon_hits(text),
    }
    return quantities, metadata


def extract_first(pattern: str, text: str) -> str | None:
    match = re.search(pattern, text, flags=re.MULTILINE)
    return match.group(1).strip() if match else None


def parse_float(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def parse_pylon_hits(text: str) -> list[dict[str, Any]]:
    hits = []
    pattern = re.compile(
        r"Scratchpad\.PylonHit\.(\d+):\n"
        r"\t([0-9.+\-eE]+)\s+([0-9.+\-eE]+)\s+([0-9.+\-eE]+)\n"
        r"\t([0-9.+\-eE]+)\n"
        r"\t([0-9.+\-eE]+)\n"
        r"\t([0-9.+\-eE]+)\n"
        r"\t([0-9.+\-eE]+)\n"
        r"\t([0-9.+\-eE]+)",
        flags=re.MULTILINE,
    )
    for match in pattern.finditer(text):
        hits.append(
            {
                "record": int(match.group(1)),
                "time": float(match.group(2)),
                "sRoad": float(match.group(3)),
                "id": int(float(match.group(4))),
                "side": int(float(match.group(5))),
                "pos_0_x": float(match.group(7)),
                "pos_0_y": float(match.group(9)),
            }
        )
    return hits


def build_struct(quantities: list[Quantity]) -> struct.Struct:
    return struct.Struct("<" + "".join(TYPE_FORMATS[q.typ] for q in quantities))


def choose_data_offset(data: bytes, record_struct: struct.Struct, time_pos: int) -> int:
    candidates = []
    for offset in range(0, 256):
        remaining = len(data) - offset
        if remaining <= 0 or remaining % record_struct.size:
            continue
        rows = remaining // record_struct.size
        if rows < 2:
            continue
        try:
            first = record_struct.unpack_from(data, offset)
            second = record_struct.unpack_from(data, offset + record_struct.size)
        except struct.error:
            continue
        t0 = first[time_pos]
        t1 = second[time_pos]
        if isinstance(t0, float) and isinstance(t1, float) and math.isfinite(t0) and math.isfinite(t1):
            if -1e-9 <= t0 <= 1.0 and t1 > t0:
                candidates.append((offset, rows, t0, t1))
    if not candidates:
        raise ValueError("Could not infer ERG data offset")
    candidates.sort(key=lambda item: (abs(item[2]), item[0]))
    return candidates[0][0]


def iter_records(
    erg_path: Path,
    quantities: list[Quantity],
    selected_names: list[str],
) -> tuple[list[dict[str, Any]], int]:
    name_to_pos = {q.name: pos for pos, q in enumerate(quantities)}
    if "Time" not in name_to_pos:
        raise ValueError("ERG file does not contain Time")
    record_struct = build_struct(quantities)
    data = erg_path.read_bytes()
    offset = choose_data_offset(data, record_struct, name_to_pos["Time"])
    rows = (len(data) - offset) // record_struct.size

    selected = [name for name in selected_names if name in name_to_pos]
    records = []
    for row_idx in range(rows):
        values = record_struct.unpack_from(data, offset + row_idx * record_struct.size)
        row = {}
        for name in selected:
            value = values[name_to_pos[name]]
            if isinstance(value, bytes):
                value = value.hex()
            row[name] = value
        records.append(row)
    return records, offset


def summarize(records: list[dict[str, Any]], metadata: dict[str, Any], available: set[str]) -> dict[str, Any]:
    if not records:
        raise ValueError("No records to summarize")

    def values(name: str) -> list[float]:
        return [float(row[name]) for row in records if name in row and is_number(row[name])]

    time = values("Time")
    speed = values("Car.v")
    y = values("Car.ty")
    t_road = values("Vhcl.tRoad")
    sroad = values("Vhcl.sRoad")
    yaw_rate = values("Car.YawRate")
    vhcl_yaw_rate = values("Vhcl.YawRate")
    path_dev_dist = values("Car.Road.Path.DevDist")
    route_dev_dist = values("Car.Road.Route.DevDist")
    path_dev_ang = values("Car.Road.Path.DevAng")
    route_dev_ang = values("Car.Road.Route.DevAng")
    side_slip = values("Car.SideSlipAngle")
    steer = values("DM.Steer.Ang")
    steer_vel = values("DM.Steer.AngVel")
    steer_acc = values("DM.Steer.AngAcc")
    whl = values("Steer.WhlAng")
    driver_lat_dy = values("Driver.Lat.dy")
    ay = values("Car.ay")
    mu = values("Car.muRoadFL")

    summary = {
        "testrun": metadata.get("testrun"),
        "dateLocal": metadata.get("date_local"),
        "samples": len(records),
        "durationS": span(time),
        "finalTimeS": time[-1] if time else None,
        "finalSRoadM": sroad[-1] if sroad else None,
        "finalX": last_value(records, "Car.tx"),
        "finalY": last_value(records, "Car.ty"),
        "speedKph": min_mean_max([v * 3.6 for v in speed]),
        "sRoadM": min_mean_max(sroad),
        "carTyM": min_mean_max(y),
        "absCarTyMaxM": max_abs(y),
        "vhclTRoadM": min_mean_max(t_road),
        "absVhclTRoadMaxM": max_abs(t_road),
        "pathDevDistM": min_mean_max(path_dev_dist),
        "absPathDevDistMaxM": max_abs(path_dev_dist),
        "routeDevDistM": min_mean_max(route_dev_dist),
        "absRouteDevDistMaxM": max_abs(route_dev_dist),
        "pathDevAngRad": min_mean_max(path_dev_ang),
        "absPathDevAngMaxRad": max_abs(path_dev_ang),
        "routeDevAngRad": min_mean_max(route_dev_ang),
        "absRouteDevAngMaxRad": max_abs(route_dev_ang),
        "driverLatDyM": min_mean_max(driver_lat_dy),
        "absDriverLatDyMaxM": max_abs(driver_lat_dy),
        "yawRateRadps": min_mean_max(yaw_rate),
        "absYawRateMaxRadps": max_abs(yaw_rate),
        "vhclYawRateRadps": min_mean_max(vhcl_yaw_rate),
        "absVhclYawRateMaxRadps": max_abs(vhcl_yaw_rate),
        "sideSlipRad": min_mean_max(side_slip),
        "absSideSlipMaxRad": max_abs(side_slip),
        "latAccelMps2": min_mean_max(ay),
        "absLatAccelMaxMps2": max_abs(ay),
        "dmSteerAngRad": min_mean_max(steer),
        "absDmSteerAngMaxRad": max_abs(steer),
        "dmSteerAngVelRadps": min_mean_max(steer_vel),
        "absDmSteerAngVelMaxRadps": max_abs(steer_vel),
        "dmSteerAngAccRadps2": min_mean_max(steer_acc),
        "absDmSteerAngAccMaxRadps2": max_abs(steer_acc),
        "steerWhlAngRad": min_mean_max(whl),
        "absSteerWhlAngMaxRad": max_abs(whl),
        "muRoadFL": min_mean_max(mu),
        "pylonHitCount": len(metadata.get("pylon_hits") or []),
        "pylonHits": metadata.get("pylon_hits") or [],
        "availableDefaultQuantities": sorted(name for name in DEFAULT_QUANTITIES if name in available),
    }
    summary["roadDepartureLikely"] = bool(summary["absCarTyMaxM"] and summary["absCarTyMaxM"] >= 5.9)
    return summary


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def span(items: list[float]) -> float | None:
    if not items:
        return None
    return items[-1] - items[0]


def min_mean_max(items: list[float]) -> dict[str, float] | None:
    if not items:
        return None
    return {
        "min": min(items),
        "mean": sum(items) / len(items),
        "max": max(items),
    }


def max_abs(items: list[float]) -> float | None:
    if not items:
        return None
    return max(abs(value) for value in items)


def last_value(records: list[dict[str, Any]], name: str) -> Any:
    for row in reversed(records):
        if name in row:
            return row[name]
    return None


def write_csv(path: Path, records: list[dict[str, Any]]) -> None:
    if not records:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(records[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def downsample(records: list[dict[str, Any]], step: int) -> list[dict[str, Any]]:
    if step <= 1:
        return records
    result = records[::step]
    if records and result[-1] is not records[-1]:
        result.append(records[-1])
    return result


def parse_quantities(value: str | None) -> list[str]:
    if not value:
        return DEFAULT_QUANTITIES
    return [item.strip() for item in value.split(",") if item.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize an IPG CarMaker .erg driving log.")
    parser.add_argument("erg", type=Path, help="Path to .erg file")
    parser.add_argument("--info", type=Path, help="Path to .erg.info file; defaults to <erg>.info")
    parser.add_argument("--quantities", help="Comma-separated quantity names to export")
    parser.add_argument("--csv", type=Path, help="Optional CSV output path")
    parser.add_argument("--json", type=Path, help="Optional JSON summary output path")
    parser.add_argument("--session-log", type=Path, help="Optional CarMaker session log path")
    parser.add_argument("--downsample", type=int, default=10, help="CSV downsample step; default 10")
    args = parser.parse_args()

    erg_path = args.erg
    info_path = args.info or Path(str(erg_path) + ".info")
    quantities, metadata = parse_info(info_path)
    available = {q.name for q in quantities}
    selected = parse_quantities(args.quantities)
    missing = [name for name in selected if name not in available]
    records, offset = iter_records(erg_path, quantities, selected)
    summary = summarize(records, metadata, available)
    summary["ergPath"] = str(erg_path)
    summary["infoPath"] = str(info_path)
    summary["dataOffsetBytes"] = offset
    summary["recordQuantityCount"] = len(quantities)
    summary["missingRequestedQuantities"] = missing
    if args.session_log:
        session_summary = parse_session_log(args.session_log, summary.get("testrun"))
        summary["sessionLogPath"] = str(args.session_log)
        summary["sessionLog"] = session_summary
        if session_summary.get("roadDeparture"):
            summary["roadDepartureLikely"] = True

    if args.csv:
        write_csv(args.csv, downsample(records, args.downsample))
        summary["csvPath"] = str(args.csv)
        summary["csvDownsample"] = args.downsample
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def parse_session_log(log_path: Path, testrun: str | None) -> dict[str, Any]:
    text = log_path.read_text(encoding="utf-8", errors="replace")
    starts = []
    ends = []
    road_departures = []
    slalom_time = None
    average_speed = None

    current_testrun = None
    for line in text.splitlines():
        start_match = re.search(r"SIM_START\s+(\S+)\s+(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", line)
        if start_match:
            current_testrun = start_match.group(1)
            starts.append({"testrun": current_testrun, "startedAt": start_match.group(2)})
            continue

        if testrun and current_testrun != testrun:
            continue

        slalom_match = re.search(r"Slalom time:\s+([0-9.]+)\s+s", line)
        if slalom_match:
            slalom_time = float(slalom_match.group(1))
            continue

        average_match = re.search(r"Average Speed:\s+([0-9.]+)\s+km/h", line)
        if average_match:
            average_speed = float(average_match.group(1))
            continue

        departure_match = re.search(
            r"ERROR\s+Vehicle leaves road at about x=([0-9.+\-eE]+), y=([0-9.+\-eE]+) TireNo=([0-9]+)",
            line,
        )
        if departure_match:
            road_departures.append(
                {
                    "x": float(departure_match.group(1)),
                    "y": float(departure_match.group(2)),
                    "tireNo": int(departure_match.group(3)),
                }
            )
            continue

        end_match = re.search(r"(SIM_END|SIM_ABORT)\s+(\S+)\s+([0-9.]+)s\s+([0-9.]+)m", line)
        if end_match:
            ends.append(
                {
                    "status": end_match.group(1),
                    "testrun": end_match.group(2),
                    "durationS": float(end_match.group(3)),
                    "distanceM": float(end_match.group(4)),
                }
            )
            current_testrun = None

    selected_ends = [item for item in ends if not testrun or item["testrun"] == testrun]
    return {
        "status": selected_ends[-1]["status"] if selected_ends else None,
        "durationS": selected_ends[-1]["durationS"] if selected_ends else None,
        "distanceM": selected_ends[-1]["distanceM"] if selected_ends else None,
        "slalomTimeS": slalom_time,
        "averageSpeedKph": average_speed,
        "roadDeparture": road_departures[-1] if road_departures else None,
        "starts": [item for item in starts if not testrun or item["testrun"] == testrun],
    }


if __name__ == "__main__":
    raise SystemExit(main())
