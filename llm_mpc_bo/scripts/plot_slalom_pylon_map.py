#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt


def load_pylons(path: Path) -> list[dict[str, float | bool | str]]:
    rows = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for raw in reader:
            rows.append(
                {
                    "markerIndex": raw["markerIndex"],
                    "pylonSide": raw["pylonSide"],
                    "x": float(raw["x"]),
                    "y": float(raw["y"]),
                    "gateCenterY": float(raw["gateCenterY"]),
                    "gateWidth": float(raw["gateWidth"]),
                    "isSlalomSideGate": raw["isSlalomSideGate"] == "True",
                }
            )
    return rows


def plot_pylon_map(pylons: list[dict[str, float | bool | str]], output: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 4.2))

    full_width = [p for p in pylons if not p["isSlalomSideGate"]]
    offset = [p for p in pylons if p["isSlalomSideGate"]]

    ax.scatter(
        [p["x"] for p in full_width],
        [p["y"] for p in full_width],
        s=32,
        c="#555555",
        marker="o",
        label="full-width gate pylons",
    )
    ax.scatter(
        [p["x"] for p in offset],
        [p["y"] for p in offset],
        s=46,
        c="#d62728",
        marker="^",
        label="offset gate pylons",
    )

    ax.axhline(6.0, color="#999999", linewidth=1, linestyle="--", label="road edge approx")
    ax.axhline(-6.0, color="#999999", linewidth=1, linestyle="--")
    ax.axhline(0.0, color="#c7c7c7", linewidth=0.8)
    ax.set_xlim(285, 510)
    ax.set_ylim(-6.5, 6.5)
    ax.set_xlabel("x / sRoad [m]")
    ax.set_ylabel("y [m]")
    ax.set_title("Slalom18m Pylon Map")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="upper center", ncol=3, bbox_to_anchor=(0.5, -0.16), frameon=False)
    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description="Plot actual pylon positions for the Slalom18m TestRun.")
    parser.add_argument("--pylons-csv", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    pylons = load_pylons(args.pylons_csv)
    plot_pylon_map(pylons, args.output)
    print(json.dumps({"output": str(args.output)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
