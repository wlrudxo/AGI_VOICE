#!/usr/bin/env python
"""Create paper Fig. 3: best-J trajectories from the four compared methods.

This script intentionally uses hard-coded result paths from the current
ICCAS2026 nominal slalom experiment set. It is written with conservative Python
syntax because the matplotlib-enabled environment on this machine is currently
the Amesim Python executable exposed as `python`.
"""

from __future__ import print_function

import csv
import json
import os

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PAPER_DIR = os.path.dirname(SCRIPT_DIR)
ROOT = os.path.dirname(PAPER_DIR)
EXPERIMENTS = os.path.join(ROOT, "llm_mpc_bo", "results", "experiments")
PYLONS_CSV = os.path.join(ROOT, "llm_mpc_bo", "results", "processed", "slalom18m_pylons.csv")
OUT_DIR = os.path.join(PAPER_DIR, "figures")


METHOD_TRIALS = [
    {
        "label": "LHC",
        "color": "#4c78a8",
        "linestyle": "-",
        "trial_dir": os.path.join(
            EXPERIMENTS,
            "standard_slalom_v61_4d_lhc_entryignored_budget50_seed3",
            "trials",
            "lhc_0050",
        ),
    },
    {
        "label": "Random",
        "color": "#b279a2",
        "linestyle": (0, (1.0, 1.4)),
        "trial_dir": os.path.join(
            EXPERIMENTS,
            "standard_slalom_v61_4d_random_entryignored_budget50_seed3",
            "trials",
            "random_0044",
        ),
    },
    {
        "label": "BO",
        "color": "#f58518",
        "linestyle": "--",
        "trial_dir": os.path.join(
            EXPERIMENTS,
            "standard_slalom_v61_4d_bo_entryignored_budget50_seed3",
            "trials",
            "bo_0049",
        ),
    },
    {
        "label": "LLM-based",
        "color": "#54a24b",
        "linestyle": "-.",
        "trial_dir": os.path.join(
            EXPERIMENTS,
            "standard_slalom_v61_4d_llm_only_seed5",
            "trials",
            "llm_only_0047",
        ),
    },
]


def main():
    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)

    pylons = load_pylons(PYLONS_CSV)
    fig, ax = plt.subplots(figsize=(3.45, 2.35))
    plotted_ref = False

    for item in METHOD_TRIALS:
        trial_dir = item["trial_dir"]
        rows = load_float_csv(os.path.join(trial_dir, "aligned_signals.csv"), downsample=8)

        if not plotted_ref:
            ax.plot(
                col(rows, "s"),
                col(rows, "t_ref"),
                color="#111111",
                linewidth=1.1,
                linestyle="--",
                label="Reference",
                zorder=2,
            )
            plotted_ref = True

        ax.plot(
            col(rows, "s"),
            col(rows, "t"),
            color=item["color"],
            linewidth=0.9,
            linestyle=item["linestyle"],
            label=item["label"],
            zorder=3,
        )

    plot_pylons(ax, pylons)
    ax.add_patch(
        Rectangle(
            (365.5, -1.32),
            13.0,
            1.20,
            fill=False,
            edgecolor="#d62728",
            linewidth=0.9,
            linestyle=(0, (3.0, 2.0)),
            zorder=5,
        )
    )
    ax.axhline(0.0, color="#dddddd", linewidth=0.7, zorder=1)

    ax.set_xlim(280, 505)
    ax.set_ylim(-2.0, 2.0)
    ax.set_xlabel("Road coordinate [m]", fontsize=8.5)
    ax.set_ylabel("Lateral position [m]", fontsize=8.5)
    ax.tick_params(axis="both", labelsize=7.5)
    ax.grid(True, alpha=0.22, linewidth=0.55)
    ax.legend(loc="upper right", ncol=1, frameon=True, framealpha=0.78, fontsize=5.4)
    fig.subplots_adjust(left=0.13, right=0.995, top=0.995, bottom=0.18)

    png = os.path.join(OUT_DIR, "fig3_best_trajectories.png")
    pdf = os.path.join(OUT_DIR, "fig3_best_trajectories.pdf")
    fig.savefig(png, dpi=300, bbox_inches="tight", pad_inches=0.015)
    try:
        fig.savefig(pdf, bbox_inches="tight", pad_inches=0.015)
    except IOError:
        pdf = os.path.join(OUT_DIR, "fig3_best_trajectories_new.pdf")
        fig.savefig(pdf, bbox_inches="tight", pad_inches=0.015)
    plt.close(fig)

    print(json.dumps({"png": png, "pdf": pdf}, indent=2))
    return 0


def load_float_csv(path, downsample):
    if not os.path.exists(path):
        raise IOError(path)
    rows = []
    with open(path, "r") as handle:
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


def load_pylons(path):
    if not os.path.exists(path):
        raise IOError(path)
    rows = []
    with open(path, "r") as handle:
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


def load_json(path):
    if not os.path.exists(path):
        raise IOError(path)
    with open(path, "r") as handle:
        return json.load(handle)


def col(rows, name):
    return [row[name] for row in rows if name in row]


def plot_pylons(ax, pylons):
    visible = [p for p in pylons if abs(p["y"]) < 2.0]
    ax.scatter(
        [p["x"] for p in visible],
        [p["y"] for p in visible],
        s=16,
        c="#d62728",
        marker="^",
        alpha=0.85,
        zorder=4,
    )


if __name__ == "__main__":
    raise SystemExit(main())
