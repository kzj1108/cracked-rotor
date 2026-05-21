"""Port of reproduce_paper_HB_fidelity.m — all paper figures."""
from __future__ import annotations
import os
from pathlib import Path
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .fig15 import plot_fig15_paper
from .paper_amp import get_paper_amp
from .paper_plots import plot_fig12, plot_fig16, plot_waterfall_paper
from dataclasses import replace

from .params import rotor_params


def rpm_grid_waterfall(quick: bool = False):
    if quick:
        mu = np.linspace(0, 1, 6)
        rpm = np.unique(
            np.concatenate(
                [
                    np.arange(500, 1350, 50),
                    np.arange(1380, 1520, 10),
                    np.arange(1550, 2580, 50),
                    np.arange(2600, 3100, 15),
                ]
            )
        )
    else:
        mu = np.linspace(0, 1, 12)
        rpm = np.unique(
            np.concatenate(
                [
                    np.arange(500, 1350, 20),
                    np.arange(1360, 1520, 4),
                    np.arange(1540, 2580, 20),
                    np.arange(2600, 3100, 5),
                ]
            )
        )
    return rpm, mu


def sweep_hb_surface(p_base, rpm_grid, mu_vals, node=10):
    nr, nm = len(rpm_grid), len(mu_vals)
    Amp = np.zeros((nr, nm))
    for j, mu in enumerate(mu_vals):
        p = replace(p_base, mu=float(mu))
        for i, rpm in enumerate(rpm_grid):
            a1, _, _ = get_paper_amp(p, float(rpm), node)
            Amp[i, j] = a1
    print(f"  sweep max amp = {np.max(Amp):.3e}")
    return Amp


def reproduce_all_figures(out_dir: str | Path | None = None, quick: bool = False) -> Path:
    out = Path(out_dir or Path(__file__).resolve().parents[1] / "output")
    out.mkdir(parents=True, exist_ok=True)
    print(f"Output: {out}  quick={quick}")

    plot_fig12(out)
    plot_fig16(out)
    plot_fig15_paper(out, quick=quick)

    rpm_w, mu_w = rpm_grid_waterfall(quick)
    pw2 = rotor_params("waterfall")
    Amp = sweep_hb_surface(pw2, rpm_w, mu_w)

    ix13 = (rpm_w >= 2600) & (rpm_w <= 3100)
    plot_waterfall_paper(
        rpm_w[ix13],
        mu_w,
        Amp[ix13, :],
        "Fig. 13(a) — Critical speeds, node 10",
        out / "fig13a_waterfall.png",
    )

    ix14 = (rpm_w >= 1380) & (rpm_w <= 1510)
    plot_waterfall_paper(
        rpm_w[ix14],
        mu_w,
        Amp[ix14, :],
        "Fig. 14(a) — Subcritical speeds, node 10",
        out / "fig14a_waterfall.png",
    )

    j3 = int(np.argmin(np.abs(mu_w - 0.3)))
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(rpm_w, Amp[:, j3] * 1e6, "b-", lw=1.2)
    ax.set_xlabel("Rotor speed (rpm)")
    ax.set_ylabel("1× amplitude (μm)")
    ax.set_title("Amplitude-frequency μ=0.3")
    ax.grid(True)
    fig.savefig(out / "ampfreq_node_curve.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    print("Done:", list(out.glob("*.png")))
    return out
