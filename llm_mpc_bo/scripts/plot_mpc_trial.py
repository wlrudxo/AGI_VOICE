#!/usr/bin/env python3
"""Plot one analyzed MPC trial from aligned_signals.csv."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt


def main() -> int:
    parser = argparse.ArgumentParser(description="Plot one MPC trial trajectory and time signals.")
    parser.add_argument("--trial-dir", type=Path, required=True)
    parser.add_argument(
        "--pylons-csv",
        type=Path,
        default=Path("llm_mpc_bo/results/processed/slalom18m_pylons.csv"),
    )
    parser.add_argument("--label", default=None)
    parser.add_argument("--trajectory-output", type=Path, default=None)
    parser.add_argument("--time-output", type=Path, default=None)
    parser.add_argument("--downsample", type=int, default=5)
    args = parser.parse_args()

    trial_dir = args.trial_dir.resolve()
    rows = load_float_csv(trial_dir / "aligned_signals.csv", downsample=max(args.downsample, 1))
    pylons = load_pylons(args.pylons_csv.resolve())
    summary = load_json_if_exists(trial_dir / "trial_summary.json")
    label = args.label or str(summary.get("runId") or trial_dir.name)

    trajectory_output = args.trajectory_output or (trial_dir / "trajectory_pylons.png")
    time_output = args.time_output or (trial_dir / "trial_time_signals.png")

    plot_trajectory(rows, pylons, trajectory_output, label, summary)
    plot_time(rows, time_output, label, summary)

    print(
        json.dumps(
            {
                "trialDir": str(trial_dir),
                "trajectory": str(trajectory_output),
                "time": str(time_output),
                "label": label,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


def load_float_csv(path: Path, downsample: int = 1) -> list[dict[str, float]]:
    if not path.exists():
        raise FileNotFoundError(path)
    rows: list[dict[str, float]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw in enumerate(reader):
            if idx % downsample != 0:
                continue
            row = {}
            for key, value in raw.items():
                if value != "":
                    row[key] = float(value)
            rows.append(row)
    return rows


def load_pylons(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(path)
    rows: list[dict[str, Any]] = []
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


def load_json_if_exists(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def col(rows: list[dict[str, float]], name: str) -> list[float]:
    return [row[name] for row in rows if name in row]


def plot_trajectory(
    rows: list[dict[str, float]],
    pylons: list[dict[str, Any]],
    output: Path,
    label: str,
    summary: dict[str, Any],
) -> None:
    fig, ax = plt.subplots(figsize=(11, 4.8))
    ax.plot(col(rows, "s"), col(rows, "t"), color="#1f77b4", linewidth=2.2, label=label)
    if rows and "t_ref" in rows[0]:
        ax.plot(col(rows, "s"), col(rows, "t_ref"), color="#2ca02c", linewidth=1.5, linestyle="--", label="reference")

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
    ax.set_xlabel("sRoad [m]")
    ax.set_ylabel("lateral position t [m]")
    ax.set_title(title_text("Slalom18m MPC Trial Trajectory", summary), loc="left")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper center", ncol=4, bbox_to_anchor=(0.5, -0.14), frameon=False)
    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180)
    plt.close(fig)


def plot_time(rows: list[dict[str, float]], output: Path, label: str, summary: dict[str, Any]) -> None:
    fig, axes = plt.subplots(4, 1, figsize=(10, 9), sharex=True)
    series = [
        ("e_t", "lateral error [m]"),
        ("e_psi", "heading error [rad]"),
        ("applied_delta_cmd", "steer command [rad]"),
        ("yawrate", "yaw rate [rad/s]"),
    ]
    for ax, (name, ylabel) in zip(axes, series):
        if rows and name in rows[0]:
            ax.plot(col(rows, "Time"), col(rows, name), label=label, linewidth=1.8)
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.3)
    axes[-1].set_xlabel("time [s]")
    axes[0].set_title(title_text("Slalom18m MPC Trial Time Signals", summary), loc="left")
    axes[0].legend(loc="best")
    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180)
    plt.close(fig)


def title_text(prefix: str, summary: dict[str, Any]) -> str:
    if not summary:
        return prefix
    parts = [prefix]
    run_id = summary.get("runId")
    if run_id:
        parts.append(str(run_id))
    metrics = []
    for key, label in (("J", "J"), ("pylonHits", "pylons"), ("rmseET", "rmseET"), ("maxAbsET", "maxET")):
        if key in summary:
            value = summary[key]
            if isinstance(value, float):
                metrics.append(f"{label}={value:.4g}")
            else:
                metrics.append(f"{label}={value}")
    if metrics:
        parts.append(", ".join(metrics))
    return " | ".join(parts)


if __name__ == "__main__":
    raise SystemExit(main())
