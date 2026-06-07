#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt


@dataclass(frozen=True)
class Run:
    label: str
    rows: list[dict[str, float]]


def load_csv(path: Path) -> list[dict[str, float]]:
    rows = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for raw in reader:
            rows.append({key: float(value) for key, value in raw.items() if value != ""})
    return rows


def load_pylons(path: Path) -> list[dict[str, float | bool]]:
    rows = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for raw in reader:
            rows.append(
                {
                    "x": float(raw["x"]),
                    "y": float(raw["y"]),
                    "isSlalomSideGate": raw["isSlalomSideGate"] == "True",
                }
            )
    return rows


def col(rows: list[dict[str, float]], name: str) -> list[float]:
    return [row[name] for row in rows if name in row]


def parse_run(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("--run must be formatted as label=csv_path")
    label, path = value.rsplit("=", 1)
    if not label.strip():
        raise argparse.ArgumentTypeError("--run label must not be empty")
    return label.strip(), Path(path)


def plot_xy(runs: list[Run], pylons: list[dict[str, float | bool]], output: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 4.8))
    for run in runs:
        ax.plot(col(run.rows, "Car.tx"), col(run.rows, "Car.ty"), label=run.label, linewidth=2)

    center_gate = [p for p in pylons if not p["isSlalomSideGate"]]
    side_gate = [p for p in pylons if p["isSlalomSideGate"]]
    ax.scatter(
        [p["x"] for p in center_gate],
        [p["y"] for p in center_gate],
        s=20,
        c="#777777",
        marker="o",
        label="full-width gate pylons",
    )
    ax.scatter(
        [p["x"] for p in side_gate],
        [p["y"] for p in side_gate],
        s=38,
        c="#d62728",
        marker="^",
        label="offset gate pylons",
    )

    ax.axhline(6.0, color="#999999", linewidth=1, linestyle="--", label="road edge approx")
    ax.axhline(-6.0, color="#999999", linewidth=1, linestyle="--")
    ax.axhline(0.0, color="#c7c7c7", linewidth=0.8)
    ax.set_xlim(280, 505)
    ax.set_ylim(-6.5, 6.5)
    ax.set_xlabel("x / sRoad [m]")
    ax.set_ylabel("y [m]")
    ax.set_title("Slalom18m UserSteer Mu Sweep: Trajectory and Pylons")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper center", ncol=3, bbox_to_anchor=(0.5, -0.14), frameon=False)
    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180)
    plt.close(fig)


def plot_time(runs: list[Run], output: Path) -> None:
    fig, axes = plt.subplots(4, 1, figsize=(10, 9), sharex=True)
    series = [
        ("Car.Road.Path.DevDist", "path dev dist [m]"),
        ("Car.YawRate", "yaw rate [rad/s]"),
        ("DM.Steer.Ang", "steer wheel angle [rad]"),
        ("DM.Steer.AngVel", "steer wheel rate [rad/s]"),
    ]

    for ax, (name, ylabel) in zip(axes, series):
        for run in runs:
            ax.plot(col(run.rows, "Time"), col(run.rows, name), label=run.label, linewidth=1.8)
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.3)
    axes[-1].set_xlabel("time [s]")
    axes[0].set_title("Slalom18m UserSteer Mu Sweep: Time-Series Metrics")
    axes[0].legend(loc="best")
    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description="Plot multiple slalom runs with pylon geometry.")
    parser.add_argument("--run", type=parse_run, action="append", required=True)
    parser.add_argument("--pylons-csv", type=Path, required=True)
    parser.add_argument("--xy-output", type=Path, required=True)
    parser.add_argument("--time-output", type=Path, required=True)
    args = parser.parse_args()

    runs = [Run(label, load_csv(path)) for label, path in args.run]
    pylons = load_pylons(args.pylons_csv)
    plot_xy(runs, pylons, args.xy_output)
    plot_time(runs, args.time_output)
    print(json.dumps({"xy": str(args.xy_output), "time": str(args.time_output)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
