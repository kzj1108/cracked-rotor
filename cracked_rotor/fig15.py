"""Fig.15 — 2x2 spikes + 3x1 log."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from .paper_amp import get_paper_amp
from .params import rotor_params

PAPER_BLUE = (0.0, 0.45, 0.74)


def rpm_grid_fig15(quick: bool = False) -> np.ndarray:
    if quick:
        return np.unique(
            np.concatenate(
                [
                    np.arange(500, 1200, 40),
                    np.arange(1200, 1620, 4),
                    np.arange(1620, 2500, 40),
                    np.arange(2500, 3120, 8),
                ]
            )
        )
    return np.unique(
        np.concatenate(
            [
                np.arange(500, 1180, 20),
                np.arange(1185, 1621, 0.5),
                np.arange(1625, 2460, 20),
                np.arange(2465, 3121, 0.5),
            ]
        )
    )


def _sweep_curve(p, rpms, node=10):
    a1 = np.zeros(len(rpms))
    a2 = np.zeros(len(rpms))
    for i, rpm in enumerate(rpms):
        a1[i], a2[i], _ = get_paper_amp(p, float(rpm), node)
    return a1, a2


def _plot_spikes(ax, x, amp, color=PAPER_BLUE):
    amp = np.maximum(amp, 1e-16)
    ax.vlines(x, 0, amp, colors=[color], linewidth=0.7)
    ax.plot(x, amp, "-", color=color, lw=0.5)
    ymax = float(np.max(amp))
    ax.set_ylim(0, ymax * 1.15 if ymax > 0 else 1e-10)


def plot_fig15_paper(out_dir: Path, quick: bool = False) -> list[Path]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rpms = rpm_grid_fig15(quick)
    rpms_z = rpms[rpms <= 1000]

    pw = rotor_params("waterfall")
    pw = replace(pw, me_d=1e-6, n_harmonics=4, zeta_hb=0.004, hb_reg_scale=1.5e-4, c_b=80, damped=True)

    fig, axes = plt.subplots(2, 2, figsize=(9.2, 7.2))
    for sp, mu in enumerate([0.1, 0.2, 0.3, 0.4]):
        pj = replace(pw, mu=mu)
        a1, a2 = _sweep_curve(pj, rpms_z)
        amp = np.maximum(a1, a2)
        _plot_spikes(axes.flat[sp], rpms_z, amp)
        axes.flat[sp].set_xlim(0, 1000)
        axes.flat[sp].set_xlabel("频率 f/Hz")
        axes.flat[sp].set_ylabel("幅值 (m)")
        axes.flat[sp].set_title(f"Fig.15({'abcd'[sp]}) μ={mu}")
        axes.flat[sp].grid(True)
    fig.suptitle("Fig.15 — Node 10")
    fig.tight_layout()
    p1 = out_dir / "fig15_paper_spikes_2x2.png"
    fig.savefig(p1, dpi=200, bbox_inches="tight")
    plt.close(fig)

    fig2, axes2 = plt.subplots(3, 1, figsize=(5.5, 8))
    for sp, mu in enumerate([0.1, 0.2, 0.3]):
        pj = replace(pw, mu=mu)
        a1, a2 = _sweep_curve(pj, rpms)
        amp = np.maximum(a1, a2)
        _plot_spikes(axes2[sp], rpms, amp)
        axes2[sp].set_yscale("log")
        axes2[sp].set_xlim(500, 3100)
        lo = max(1e-12, float(np.min(amp[amp > 0])) if np.any(amp > 0) else 1e-12)
        axes2[sp].set_ylim(lo, 1e-2 if sp < 2 else 1e0)
        axes2[sp].set_ylabel("幅值 (m)")
        axes2[sp].set_title(f"Fig.15({'abc'[sp]}) μ={mu}")
        axes2[sp].grid(True)
    axes2[-1].set_xlabel("Rotor speed (rpm)")
    fig2.tight_layout()
    p2 = out_dir / "fig15abc_log_amp_vs_rpm.png"
    p3 = out_dir / "fig15ab_log_amp_vs_rpm.png"
    fig2.savefig(p2, dpi=200, bbox_inches="tight")
    fig2.savefig(p3, dpi=200, bbox_inches="tight")
    plt.close(fig2)
    return [p1, p2, p3]
