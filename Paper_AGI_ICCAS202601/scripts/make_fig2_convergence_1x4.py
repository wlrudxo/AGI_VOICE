#!/usr/bin/env python
"""Create a 1x4 convergence preview figure with all repetitions."""

from __future__ import print_function

import json
import os

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
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
        "dirs": [
            "standard_slalom_v61_4d_lhc_entryignored_budget50_seed1",
            "standard_slalom_v61_4d_lhc_entryignored_budget50_seed2",
            "standard_slalom_v61_4d_lhc_entryignored_budget50_seed3",
            "standard_slalom_v61_4d_lhc_entryignored_budget50_seed4",
            "standard_slalom_v61_4d_lhc_entryignored_budget50_seed5",
        ],
    },
    {
        "label": "Random",
        "color": "#b279a2",
        "dirs": [
            "standard_slalom_v61_4d_random_entryignored_budget50_seed1",
            "standard_slalom_v61_4d_random_entryignored_budget50_seed2",
            "standard_slalom_v61_4d_random_entryignored_budget50_seed3",
            "standard_slalom_v61_4d_random_entryignored_budget50_seed4",
            "standard_slalom_v61_4d_random_entryignored_budget50_seed5",
        ],
    },
    {
        "label": "BO",
        "color": "#f58518",
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
        "dirs": [
            "standard_slalom_v61_4d_llm_only_seed1",
            "standard_slalom_v61_4d_llm_only_seed2",
            "standard_slalom_v61_4d_llm_only_seed3",
            "standard_slalom_v61_4d_llm_only_seed4",
            "standard_slalom_v61_4d_llm_only_seed5",
        ],
    },
]


def main():
    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)

    fig, axes = plt.subplots(1, 4, figsize=(6.95, 1.55), sharex=True, sharey=True)
    report = []

    for ax, method in zip(axes, METHODS):
        curves = []
        for seed_idx, exp_name in enumerate(method["dirs"], start=1):
            rows = load_trials(os.path.join(EXPERIMENTS, exp_name, "trials.jsonl"))
            xs, ys = best_so_far_curve(rows)
            final = ys[-1]
            curves.append(
                {
                    "seed": seed_idx,
                    "experiment": exp_name,
                    "xs": xs,
                    "ys": ys,
                    "final": final,
                }
            )

        best_final = min(curve["final"] for curve in curves)
        for curve in curves:
            is_best = curve["final"] == best_final
            ax.plot(
                curve["xs"],
                curve["ys"],
                color=method["color"],
                alpha=0.9 if is_best else 0.38,
                linewidth=1.25 if is_best else 0.75,
            )
            report.append(
                {
                    "method": method["label"],
                    "seed": curve["seed"],
                    "experiment": curve["experiment"],
                    "finalBestJ": curve["final"],
                    "highlighted": is_best,
                }
            )

        ax.set_title(method["label"], fontsize=7.0, pad=2.0)
        ax.set_yscale("log")
        ax.set_xlim(1, 50)
        ax.set_ylim(0.55, 180)
        ax.grid(True, which="major", alpha=0.24, linewidth=0.45)
        ax.grid(True, which="minor", axis="y", alpha=0.11, linewidth=0.30)
        ax.tick_params(axis="both", labelsize=6.2, pad=1.3)

    axes[0].set_ylabel(r"$J_{\mathrm{best}}$", fontsize=7.2)
    fig.text(0.52, 0.06, "Trial", ha="center", va="center", fontsize=7.2)
    fig.subplots_adjust(left=0.065, right=0.995, top=0.84, bottom=0.26, wspace=0.13)

    png = os.path.join(OUT_DIR, "fig2_convergence_1x4.png")
    pdf = os.path.join(OUT_DIR, "fig2_convergence_1x4.pdf")
    fig.savefig(png, dpi=300, bbox_inches="tight", pad_inches=0.015)
    fig.savefig(pdf, bbox_inches="tight", pad_inches=0.015)
    plt.close(fig)

    print(json.dumps({"png": png, "pdf": pdf, "runs": report}, indent=2))
    return 0


def load_trials(path):
    if not os.path.exists(path):
        raise IOError(path)
    rows = []
    with open(path, "r") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    rows.sort(key=lambda row: int(row.get("iter") or 0))
    return rows


def best_so_far_curve(rows):
    xs = []
    ys = []
    current = None
    for row in rows:
        if row.get("J") is None:
            continue
        value = float(row["J"])
        if current is None or value < current:
            current = value
        xs.append(int(row["iter"]))
        ys.append(current)
    return xs, ys


if __name__ == "__main__":
    raise SystemExit(main())
