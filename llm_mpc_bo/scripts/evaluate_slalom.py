#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any


def load_rows(path: Path) -> list[dict[str, float]]:
    rows = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for raw in reader:
            rows.append({key: float(value) for key, value in raw.items() if value != ""})
    return rows


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def values(rows: list[dict[str, float]], name: str) -> list[float]:
    return [row[name] for row in rows if name in row and math.isfinite(row[name])]


def rmse(items: list[float]) -> float | None:
    if not items:
        return None
    return math.sqrt(sum(value * value for value in items) / len(items))


def max_abs(items: list[float]) -> float | None:
    if not items:
        return None
    return max(abs(value) for value in items)


def finite(value: float | None) -> float:
    return value if value is not None and math.isfinite(value) else 0.0


def evaluate(summary: dict[str, Any], rows: list[dict[str, float]]) -> dict[str, Any]:
    e_y = values(rows, "Car.Road.Path.DevDist") or values(rows, "Vhcl.tRoad") or values(rows, "Car.ty")
    e_psi = values(rows, "Car.Road.Path.DevAng")
    steer = values(rows, "DM.Steer.Ang")
    steer_rate = values(rows, "DM.Steer.AngVel")
    yaw_rate = values(rows, "Car.YawRate")
    side_slip = values(rows, "Car.SideSlipAngle")

    pylon_hits = int(summary.get("pylonHitCount") or 0)
    session = summary.get("sessionLog") or {}
    status = session.get("status")
    crash_or_sim_fail = status == "SIM_ABORT" or bool(session.get("roadDeparture"))

    metrics = {
        "RMSE_y": rmse(e_y),
        "MAX_y": max_abs(e_y),
        "RMSE_e_psi": rmse(e_psi),
        "MAX_e_psi": max_abs(e_psi),
        "RMSE_delta": rmse(steer),
        "RMSE_d_delta": rmse(steer_rate),
        "MAX_yaw_rate": max_abs(yaw_rate),
        "MAX_side_slip": max_abs(side_slip),
        "N_violation": pylon_hits,
        "crash_or_sim_fail": crash_or_sim_fail,
        "status": status,
        "durationS": session.get("durationS") or summary.get("durationS"),
        "distanceM": session.get("distanceM") or summary.get("finalSRoadM"),
    }

    continuous_j = (
        1.00 * finite(metrics["RMSE_y"]) / 0.50
        + 0.60 * finite(metrics["MAX_y"]) / 1.50
        + 0.20 * finite(metrics["RMSE_delta"]) / 0.20
        + 0.30 * finite(metrics["RMSE_d_delta"]) / 0.80
        + 0.30 * finite(metrics["MAX_yaw_rate"]) / 0.80
        + 5.00 * pylon_hits
        + 20.0 * (1.0 if crash_or_sim_fail else 0.0)
    )
    hard_fail_j = 50.0 + 10.0 * pylon_hits if crash_or_sim_fail else None

    return {
        "testrun": summary.get("testrun"),
        "ergPath": summary.get("ergPath"),
        "metrics": metrics,
        "objective": {
            "J_continuous": continuous_j,
            "J_failClosed": hard_fail_j if hard_fail_j is not None else continuous_j,
            "objectiveUsed": "hard_fail" if hard_fail_j is not None else "continuous",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate slalom run metrics and scalar objective J.")
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = evaluate(load_json(args.summary), load_rows(args.csv))
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
