#!/usr/bin/env python3
"""Plot objective value by experiment episode from trials.jsonl."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt


def main() -> int:
    parser = argparse.ArgumentParser(description="Plot objective J over trial episodes.")
    parser.add_argument("--experiment-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--title", default=None)
    parser.add_argument("--ymax", type=float, default=None)
    args = parser.parse_args()

    experiment_dir = args.experiment_dir.resolve()
    rows = load_trials(experiment_dir / "trials.jsonl")
    output = args.output or (experiment_dir / "objective_by_episode.png")
    title = args.title or experiment_dir.name
    plot_objective(rows, output, title, args.ymax)
    print(json.dumps({"output": str(output), "episodes": len(rows)}, indent=2, ensure_ascii=False))
    return 0


def load_trials(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(path)
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    rows.sort(key=lambda row: int(row.get("iter") or 0))
    return rows


def plot_objective(rows: list[dict[str, Any]], output: Path, title: str, ymax: float | None) -> None:
    episodes = [int(row["iter"]) for row in rows if row.get("J") is not None]
    values = [float(row["J"]) for row in rows if row.get("J") is not None]
    best = best_so_far(values)

    sim_end_x = [int(row["iter"]) for row in rows if row.get("J") is not None and row.get("status") == "SIM_END"]
    sim_end_y = [float(row["J"]) for row in rows if row.get("J") is not None and row.get("status") == "SIM_END"]
    abort_x = [int(row["iter"]) for row in rows if row.get("J") is not None and row.get("status") != "SIM_END"]
    abort_y = [float(row["J"]) for row in rows if row.get("J") is not None and row.get("status") != "SIM_END"]

    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    ax.plot(episodes, values, color="#9aa0a6", linewidth=1.0, alpha=0.65, label="J")
    ax.scatter(sim_end_x, sim_end_y, s=28, color="#1f77b4", label="SIM_END", zorder=3)
    if abort_x:
        ax.scatter(abort_x, abort_y, s=38, color="#d62728", marker="x", label="non-SIM_END", zorder=4)
    ax.plot(episodes, best, color="#111111", linewidth=2.3, label="best so far")

    best_idx = min(range(len(values)), key=values.__getitem__)
    best_ep = episodes[best_idx]
    best_j = values[best_idx]
    ax.scatter([best_ep], [best_j], s=90, color="#2ca02c", marker="*", label=f"best ep {best_ep}", zorder=5)
    ax.annotate(
        f"best J={best_j:.4g}\nep={best_ep}",
        xy=(best_ep, best_j),
        xytext=(8, 18),
        textcoords="offset points",
        fontsize=9,
        arrowprops={"arrowstyle": "->", "color": "#2ca02c", "lw": 1.0},
    )

    if ymax is not None:
        ax.set_ylim(0, ymax)
    else:
        ax.set_ylim(bottom=0)
    ax.set_xlabel("episode / trial iteration")
    ax.set_ylabel("objective J")
    ax.set_title(f"Objective by Episode | {title}", loc="left")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", frameon=False)
    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180)
    plt.close(fig)


def best_so_far(values: list[float]) -> list[float]:
    best = []
    current = float("inf")
    for value in values:
        current = min(current, value)
        best.append(current)
    return best


if __name__ == "__main__":
    raise SystemExit(main())
