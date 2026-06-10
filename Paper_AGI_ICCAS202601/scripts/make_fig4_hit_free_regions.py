#!/usr/bin/env python
"""Create 4D hit-free region projection figure for the paper."""

from __future__ import print_function

import json
import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Ellipse


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PAPER_DIR = os.path.dirname(SCRIPT_DIR)
ROOT = os.path.dirname(PAPER_DIR)
EXPERIMENTS = os.path.join(ROOT, "llm_mpc_bo", "results", "experiments")
OUT_DIR = os.path.join(PAPER_DIR, "figures")


METHODS = [
    {
        "label": "LHC",
        "color": "#4c78a8",
        "marker": "s",
        "dirs": [
            "standard_slalom_v61_4d_lhc_entryignored_budget50_seed1",
            "standard_slalom_v61_4d_lhc_entryignored_budget50_seed2",
            "standard_slalom_v61_4d_lhc_entryignored_budget50_seed3",
            "standard_slalom_v61_4d_lhc_entryignored_budget50_seed4",
            "standard_slalom_v61_4d_lhc_entryignored_budget50_seed5",
        ],
    },
    {
        "label": "BO",
        "color": "#f58518",
        "marker": "o",
        "dirs": [
            "standard_slalom_v61_4d_bo_entryignored_init15_seed1",
            "standard_slalom_v61_4d_bo_entryignored_budget50_seed2",
            "standard_slalom_v61_4d_bo_entryignored_budget50_seed3",
            "standard_slalom_v61_4d_bo_entryignored_budget50_seed4",
            "standard_slalom_v61_4d_bo_entryignored_budget50_seed5",
        ],
    },
    {
        "label": "LLM-based",
        "color": "#54a24b",
        "marker": ".",
        "dirs": [
            "standard_slalom_v61_4d_llm_only_seed1",
            "standard_slalom_v61_4d_llm_only_seed2",
            "standard_slalom_v61_4d_llm_only_seed3",
            "standard_slalom_v61_4d_llm_only_seed4",
            "standard_slalom_v61_4d_llm_only_seed5",
        ],
    },
]


REPRESENTATIVES = [
    {
        "label": "R1",
        "params": {
            "q_y": 13.321,
            "q_psi": 89.758,
            "r_delta": 0.0114,
            "r_d_delta": 0.0126,
        },
    },
    {
        "label": "R2",
        "params": {
            "q_y": 80.000,
            "q_psi": 45.765,
            "r_delta": 0.1000,
            "r_d_delta": 0.8000,
        },
    },
    {
        "label": "R3",
        "params": {
            "q_y": 62.960,
            "q_psi": 4.710,
            "r_delta": 0.1900,
            "r_d_delta": 1.1300,
        },
    },
    {
        "label": "R4",
        "params": {
            "q_y": 56.001,
            "q_psi": 0.0459,
            "r_delta": 0.3501,
            "r_d_delta": 0.9510,
        },
    },
    {
        "label": "R5",
        "params": {
            "q_y": 29.110,
            "q_psi": 0.2300,
            "r_delta": 0.1500,
            "r_d_delta": 0.5300,
        },
    },
    {
        "label": "R6",
        "params": {
            "q_y": 86.585,
            "q_psi": 0.0406,
            "r_delta": 0.0209,
            "r_d_delta": 1.7583,
        },
    },
]


PANELS = [
    ("q_y", "q_psi", "(a) $q_y$ vs. $q_\\psi$"),
    ("q_psi", "r_delta", "(b) $q_\\psi$ vs. $r_\\delta$"),
    ("q_psi", "r_d_delta", "(c) $q_\\psi$ vs. $r_{\\Delta\\delta}$"),
    ("r_delta", "r_d_delta", "(d) $r_\\delta$ vs. $r_{\\Delta\\delta}$"),
]


AXIS_LABELS = {
    "q_y": "$\\log_{10} q_y$",
    "q_psi": "$\\log_{10} q_\\psi$",
    "r_delta": "$\\log_{10} r_\\delta$",
    "r_d_delta": "$\\log_{10} r_{\\Delta\\delta}$",
}


def main():
    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)

    data = collect_hit_free()
    fig, axes = plt.subplots(1, 4, figsize=(6.95, 1.85))
    handles = []
    labels = []

    for ax, panel in zip(axes, PANELS):
        x_key, y_key, title = panel
        draw_llm_region(ax, data["LLM-based"], x_key, y_key)
        for method in METHODS:
            points = data[method["label"]]
            xs = [log_param(point, x_key) for point in points]
            ys = [log_param(point, y_key) for point in points]
            size = 17 if method["label"] != "LLM-based" else 14
            alpha = 0.86 if method["label"] != "LLM-based" else 0.58
            sc = ax.scatter(
                xs,
                ys,
                s=size,
                c=method["color"],
                marker=method["marker"],
                alpha=alpha,
                edgecolors="none",
                label=method["label"],
                zorder=2,
            )
            if panel == PANELS[0]:
                handles.append(sc)
                labels.append(method["label"])

        for rep in REPRESENTATIVES:
            x = log_param(rep["params"], x_key)
            y = log_param(rep["params"], y_key)
            ax.scatter(
                [x],
                [y],
                s=5,
                c="#111111",
                edgecolors="none",
                linewidths=0.0,
                marker="o",
                zorder=5,
            )
            dx, dy = label_offset(rep["label"], x_key, y_key)
            ax.text(x + dx, y + dy, rep["label"], fontsize=5.2, zorder=5)

        ax.set_title(title, fontsize=7.0)
        ax.set_xlabel(AXIS_LABELS[x_key], fontsize=6.6)
        ax.set_ylabel(AXIS_LABELS[y_key], fontsize=6.6)
        ax.set_xlim(-2.15, 2.15)
        ax.set_ylim(-2.15, 2.15)
        ax.tick_params(axis="both", labelsize=5.8, pad=1.0)
        ax.grid(True, alpha=0.23, linewidth=0.45)

    fig.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.53, 1.035),
        ncol=3,
        frameon=True,
        framealpha=0.82,
        fontsize=6.5,
        handlelength=1.1,
        columnspacing=0.55,
        borderpad=0.25,
    )
    fig.subplots_adjust(left=0.055, right=0.995, top=0.76, bottom=0.21, wspace=0.42)

    png = os.path.join(OUT_DIR, "fig4_hit_free_regions.png")
    pdf = os.path.join(OUT_DIR, "fig4_hit_free_regions.pdf")
    fig.savefig(png, dpi=300, bbox_inches="tight", pad_inches=0.02)
    try:
        fig.savefig(pdf, bbox_inches="tight", pad_inches=0.02)
    except IOError:
        pdf = os.path.join(OUT_DIR, "fig4_hit_free_regions_new.pdf")
        fig.savefig(pdf, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)

    counts = dict((method["label"], len(data[method["label"]])) for method in METHODS)
    print(json.dumps({"png": png, "pdf": pdf, "counts": counts}, indent=2))
    return 0


def collect_hit_free():
    data = dict((method["label"], []) for method in METHODS)
    for method in METHODS:
        for exp_name in method["dirs"]:
            path = os.path.join(EXPERIMENTS, exp_name, "trials.jsonl")
            for row in load_trials(path):
                if is_hit_free(row):
                    data[method["label"]].append(row["params"])
    return data


def draw_llm_region(ax, points, x_key, y_key):
    if len(points) < 3:
        return
    xy = np.array([[log_param(point, x_key), log_param(point, y_key)] for point in points])
    center = xy.mean(axis=0)
    cov = np.cov(xy, rowvar=False)
    values, vectors = np.linalg.eigh(cov)
    order = values.argsort()[::-1]
    values = values[order]
    vectors = vectors[:, order]
    values = np.maximum(values, 1.0e-6)
    angle = math.degrees(math.atan2(vectors[1, 0], vectors[0, 0]))
    scale = 2.1
    ellipse = Ellipse(
        xy=center,
        width=2.0 * scale * math.sqrt(values[0]),
        height=2.0 * scale * math.sqrt(values[1]),
        angle=angle,
        facecolor="#54a24b",
        edgecolor="#2f7d32",
        alpha=0.12,
        linewidth=1.1,
        zorder=1,
    )
    ax.add_patch(ellipse)


def label_offset(label, x_key, y_key):
    offsets = {
        ("q_y", "q_psi", "R1"): (-0.25, -0.28),
        ("q_y", "q_psi", "R2"): (-0.28, 0.00),
        ("q_y", "q_psi", "R4"): (-0.18, 0.10),
        ("q_y", "q_psi", "R6"): (-0.10, -0.30),
        ("q_psi", "r_delta", "R1"): (-0.18, 0.16),
        ("q_psi", "r_delta", "R4"): (0.05, 0.12),
        ("q_psi", "r_delta", "R6"): (0.05, -0.18),
        ("q_psi", "r_d_delta", "R1"): (-0.18, 0.16),
        ("q_psi", "r_d_delta", "R4"): (0.05, 0.10),
        ("q_psi", "r_d_delta", "R6"): (0.05, 0.16),
        ("r_delta", "r_d_delta", "R3"): (-0.23, 0.20),
        ("r_delta", "r_d_delta", "R4"): (0.10, 0.16),
        ("r_delta", "r_d_delta", "R2"): (-0.34, 0.02),
        ("r_delta", "r_d_delta", "R5"): (-0.22, -0.42),
        ("r_delta", "r_d_delta", "R6"): (0.06, 0.20),
    }
    return offsets.get((x_key, y_key, label), (0.05, 0.05))


def is_hit_free(row):
    return row.get("status") == "SIM_END" and int(row.get("pylonHits") or 0) == 0


def load_trials(path):
    if not os.path.exists(path):
        raise IOError(path)
    rows = []
    with open(path, "r") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def log_param(params, key):
    value = float(params[key])
    return math.log10(value)


if __name__ == "__main__":
    raise SystemExit(main())
