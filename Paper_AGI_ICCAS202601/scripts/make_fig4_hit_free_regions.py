#!/usr/bin/env python
"""Create 4D hit-free region projection figure for the paper."""

from __future__ import print_function

import json
import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


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
    {
        "label": "Sobol",
        "color": "#d62728",
        "marker": "^",
        "dirs": [
            "standard_slalom_v61_4d_sobol_entryignored_budget1024_seed1",
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
            "q_y": 56.001,
            "q_psi": 0.0459,
            "r_delta": 0.3501,
            "r_d_delta": 0.9510,
        },
    },
    {
        "label": "R4",
        "params": {
            "q_y": 7.915,
            "q_psi": 0.0414,
            "r_delta": 0.0685,
            "r_d_delta": 0.1134,
        },
    },
    {
        "label": "R5",
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
    ("q_y", "r_delta", "(b) $q_y$ vs. $r_\\delta$"),
    ("q_y", "r_d_delta", "(c) $q_y$ vs. $r_{\\Delta\\delta}$"),
    ("q_psi", "r_delta", "(d) $q_\\psi$ vs. $r_\\delta$"),
    ("q_psi", "r_d_delta", "(e) $q_\\psi$ vs. $r_{\\Delta\\delta}$"),
    ("r_delta", "r_d_delta", "(f) $r_\\delta$ vs. $r_{\\Delta\\delta}$"),
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
    fig, axes = plt.subplots(2, 3, figsize=(6.95, 3.15))
    axes = [axes[0][0], axes[0][1], axes[0][2], axes[1][0], axes[1][1], axes[1][2]]
    handles = []
    labels = []

    for ax, panel in zip(axes, PANELS):
        x_key, y_key, title = panel
        for method in METHODS:
            points = data[method["label"]]
            xs = [log_param(point, x_key) for point in points]
            ys = [log_param(point, y_key) for point in points]
            size = 12 if method["label"] != "LLM-based" else 9
            alpha = 0.78 if method["label"] != "LLM-based" else 0.35
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
            ax.scatter([x], [y], s=42, c="#111111", marker="*", zorder=4)
            ax.text(x + 0.05, y + 0.05, rep["label"], fontsize=5.5, zorder=5)

        ax.set_title(title, fontsize=7.2)
        ax.set_xlabel(AXIS_LABELS[x_key], fontsize=6.8)
        ax.set_ylabel(AXIS_LABELS[y_key], fontsize=6.8)
        ax.set_xlim(-2.15, 2.15)
        ax.set_ylim(-2.15, 2.15)
        ax.tick_params(axis="both", labelsize=5.9, pad=1.0)
        ax.grid(True, alpha=0.23, linewidth=0.45)

    fig.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.53, 1.005),
        ncol=4,
        frameon=True,
        framealpha=0.82,
        fontsize=6.2,
        handlelength=1.1,
        columnspacing=0.55,
        borderpad=0.25,
    )
    fig.subplots_adjust(left=0.07, right=0.995, top=0.87, bottom=0.10, wspace=0.35, hspace=0.58)

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
