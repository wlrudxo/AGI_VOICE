#!/usr/bin/env python
"""Create a combined 1x2 best/worst convergence figure."""

from __future__ import print_function

import json
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

    selected = select_runs()
    fig, axes = plt.subplots(1, 2, figsize=(3.45, 1.95), sharex=True, sharey=True)
    handles = []
    labels = []

    for ax, key, title in [
        (axes[0], "best", "(a) Best"),
        (axes[1], "worst", "(b) Worst"),
    ]:
        for run in selected[key]:
            method = run["method"]
            line = ax.plot(
                run["xs"],
                run["ys"],
                color=method["color"],
                linewidth=1.15,
                label=method["label"],
            )[0]
            if key == "best":
                handles.append(line)
                labels.append(method["label"])
        ax.set_title(title, fontsize=7.4)
        ax.set_yscale("log")
        ax.set_xlim(1, 50)
        ax.set_ylim(0.55, 180)
        ax.grid(True, which="major", alpha=0.25, linewidth=0.45)
        ax.grid(True, which="minor", axis="y", alpha=0.12, linewidth=0.35)
        ax.tick_params(axis="both", labelsize=6.4, pad=1.5)

    fig.text(0.56, 0.055, "Trial index", ha="center", va="center", fontsize=7.7)
    fig.text(
        0.02,
        0.51,
        "Best-so-far objective $J$",
        ha="center",
        va="center",
        rotation="vertical",
        fontsize=7.7,
    )
    fig.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.54, 0.985),
        ncol=4,
        frameon=True,
        framealpha=0.82,
        fontsize=5.9,
        handlelength=1.5,
        columnspacing=0.7,
        borderpad=0.25,
    )
    fig.subplots_adjust(left=0.16, right=0.995, top=0.82, bottom=0.25, wspace=0.10)

    png = os.path.join(OUT_DIR, "fig2_convergence_best_worst.png")
    pdf = os.path.join(OUT_DIR, "fig2_convergence_best_worst.pdf")
    fig.savefig(png, dpi=300, bbox_inches="tight", pad_inches=0.025)
    try:
        fig.savefig(pdf, bbox_inches="tight", pad_inches=0.025)
    except IOError:
        pdf = os.path.join(OUT_DIR, "fig2_convergence_best_worst_new.pdf")
        fig.savefig(pdf, bbox_inches="tight", pad_inches=0.025)
    plt.close(fig)

    report = {}
    for key, runs in selected.items():
        report[key] = [
            {
                "method": run["method"]["label"],
                "seed": run["seed"],
                "experiment": run["experiment"],
                "finalBestJ": run["final"],
            }
            for run in runs
        ]

    print(json.dumps({"png": png, "pdf": pdf, "selected": report}, indent=2))
    return 0


def select_runs():
    selected = {"best": [], "worst": []}
    for method in METHODS:
        runs = []
        for seed_idx, exp_name in enumerate(method["dirs"], start=1):
            rows = load_trials(os.path.join(EXPERIMENTS, exp_name, "trials.jsonl"))
            xs, ys = best_so_far_curve(rows)
            runs.append(
                {
                    "method": method,
                    "seed": seed_idx,
                    "experiment": exp_name,
                    "xs": xs,
                    "ys": ys,
                    "final": ys[-1],
                }
            )
        selected["best"].append(min(runs, key=lambda run: run["final"]))
        selected["worst"].append(max(runs, key=lambda run: run["final"]))
    return selected


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
