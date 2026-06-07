#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from bisect import bisect_left
from pathlib import Path


def load_rows(path: Path) -> list[dict[str, float]]:
    rows = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for raw in reader:
            rows.append({key: float(value) for key, value in raw.items() if value != ""})
    return rows


def interp(xs: list[float], ys: list[float], x: float) -> float:
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    idx = bisect_left(xs, x)
    x0, x1 = xs[idx - 1], xs[idx]
    y0, y1 = ys[idx - 1], ys[idx]
    alpha = (x - x0) / (x1 - x0)
    return y0 + alpha * (y1 - y0)


def make_grid(start: float, stop: float, step: float) -> list[float]:
    values = []
    x = start
    while x <= stop + 1e-9:
        values.append(round(x, 6))
        x += step
    return values


def write_reference(rows: list[dict[str, float]], output: Path, start: float, stop: float, step: float) -> None:
    rows = sorted(rows, key=lambda row: row["Vhcl.sRoad"])
    unique = []
    last_s = None
    for row in rows:
        s = row["Vhcl.sRoad"]
        if last_s is None or s > last_s:
            unique.append(row)
            last_s = s

    s_raw = [row["Vhcl.sRoad"] for row in unique]
    t_raw = [row["Car.Road.Path.DevDist"] for row in unique]
    psi_raw = [row["Car.Road.Path.DevAng"] for row in unique]
    delta_raw = [row["DM.Steer.Ang"] for row in unique]

    grid = make_grid(start, stop, step)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["s_ref", "t_ref", "psi_ref", "delta_ff"],
        )
        writer.writeheader()
        for s in grid:
            writer.writerow(
                {
                    "s_ref": f"{s:.6f}",
                    "t_ref": f"{interp(s_raw, t_raw, s):.9f}",
                    "psi_ref": f"{interp(s_raw, psi_raw, s):.9f}",
                    "delta_ff": f"{interp(s_raw, delta_raw, s):.9f}",
                }
            )


def write_matlab_init(reference_csv: Path, output: Path) -> None:
    csv_path = reference_csv.resolve().as_posix()
    if csv_path.startswith("/mnt/") and len(csv_path) > 6 and csv_path[6] == "/":
        drive = csv_path[5].upper()
        csv_path = drive + ":\\" + csv_path[7:].replace("/", "\\")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "\n".join(
            [
                "% Auto-generated slalom reference loader.",
                "% Source: Base mu=1.0 successful Slalom18m trajectory.",
                f"T = readtable('{csv_path}');",
                "slalom_s_ref = T.s_ref;",
                "slalom_t_ref = T.t_ref;",
                "slalom_psi_ref = T.psi_ref;",
                "slalom_delta_ff = T.delta_ff;",
                "clear T;",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Simulink lookup reference from a successful slalom run.")
    parser.add_argument("--input-csv", type=Path, required=True)
    parser.add_argument("--reference-csv", type=Path, required=True)
    parser.add_argument("--matlab-init", type=Path, required=True)
    parser.add_argument("--start", type=float, default=280.0)
    parser.add_argument("--stop", type=float, default=505.0)
    parser.add_argument("--step", type=float, default=0.5)
    args = parser.parse_args()

    rows = load_rows(args.input_csv)
    write_reference(rows, args.reference_csv, args.start, args.stop, args.step)
    write_matlab_init(args.reference_csv, args.matlab_init)
    print(args.reference_csv)
    print(args.matlab_init)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
