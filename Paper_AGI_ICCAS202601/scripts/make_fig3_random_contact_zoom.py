#!/usr/bin/env python
"""Create a zoomed trajectory plot around the random-search cone contact."""

from __future__ import print_function

import json
import os

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
import matplotlib.pyplot as plt

from make_fig3_best_trajectories import (
    METHOD_TRIALS,
    OUT_DIR,
    PYLONS_CSV,
    col,
    load_float_csv,
    load_pylons,
)


CONTACT_X = 372.0
CONTACT_Y = -0.25


def main():
    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)

    pylons = load_pylons(PYLONS_CSV)
    fig, ax = plt.subplots(figsize=(3.45, 2.05))
    plotted_ref = False

    for item in METHOD_TRIALS:
        rows = load_float_csv(os.path.join(item["trial_dir"], "aligned_signals.csv"), downsample=2)

        if not plotted_ref:
            ax.plot(
                col(rows, "s"),
                col(rows, "t_ref"),
                color="#111111",
                linewidth=1.0,
                linestyle="--",
                label="Reference",
                zorder=2,
            )
            plotted_ref = True

        linewidth = 1.05 if item["label"] == "Random" else 0.95
        ax.plot(
            col(rows, "s"),
            col(rows, "t"),
            color=item["color"],
            linewidth=linewidth,
            linestyle=item["linestyle"],
            label=item["label"],
            zorder=4 if item["label"] == "Random" else 3,
        )

    plot_local_pylons(ax, pylons)
    ax.scatter(
        [CONTACT_X],
        [CONTACT_Y],
        s=42,
        c="#d62728",
        edgecolors="#111111",
        linewidths=0.6,
        marker="^",
        zorder=6,
    )

    ax.axhline(0.0, color="#dddddd", linewidth=0.65, zorder=1)
    ax.set_xlim(365.5, 378.5)
    ax.set_ylim(-1.32, -0.12)
    ax.set_xlabel("Road coordinate [m]", fontsize=8.5)
    ax.set_ylabel("Lateral position [m]", fontsize=8.5)
    ax.tick_params(axis="both", labelsize=7.5)
    ax.grid(True, alpha=0.24, linewidth=0.55)
    ax.legend(loc="upper right", ncol=1, frameon=True, framealpha=0.78, fontsize=5.4)
    fig.subplots_adjust(left=0.13, right=0.995, top=0.99, bottom=0.19)

    png = os.path.join(OUT_DIR, "fig3_random_contact_zoom.png")
    pdf = os.path.join(OUT_DIR, "fig3_random_contact_zoom.pdf")
    fig.savefig(png, dpi=300, bbox_inches="tight", pad_inches=0.015)
    try:
        fig.savefig(pdf, bbox_inches="tight", pad_inches=0.015)
    except IOError:
        pdf = os.path.join(OUT_DIR, "fig3_random_contact_zoom_new.pdf")
        fig.savefig(pdf, bbox_inches="tight", pad_inches=0.015)
    plt.close(fig)

    print(json.dumps({"png": png, "pdf": pdf}, indent=2))
    return 0


def plot_local_pylons(ax, pylons):
    visible = [
        p
        for p in pylons
        if 365.5 <= p["x"] <= 378.5 and -1.32 <= p["y"] <= -0.12
    ]
    ax.scatter(
        [p["x"] for p in visible],
        [p["y"] for p in visible],
        s=22,
        c="#d62728",
        marker="^",
        alpha=0.9,
        zorder=5,
    )


if __name__ == "__main__":
    raise SystemExit(main())
