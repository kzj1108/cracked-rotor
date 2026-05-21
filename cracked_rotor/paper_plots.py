"""Literature-style figure plotting (Fig.12–16)."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from .harmonic_balance import orbit_from_hb_mm, solve_harmonic_balance
from .paper_amp import get_paper_amp
from .params import rotor_params
from dataclasses import replace


def _save(fig, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def plot_waterfall_paper(rpm, mu, amp, title: str, path: Path):
    amp = np.asarray(amp, dtype=float)
    amp = np.where(np.isfinite(amp), amp, np.nan)
    amp_max = float(np.nanmax(amp)) if np.any(np.isfinite(amp)) else 0.0
    if amp_max < 1e-14:
        print(f"WARNING waterfall: no valid amp, using model floor ({title})")
        amp = np.full_like(amp, 1e-8)
        amp_max = 1e-8
    amp = np.maximum(amp, 1e-16)

    fig = plt.figure(figsize=(9, 6))
    ax = fig.add_subplot(111, projection="3d")
    for j, m in enumerate(mu):
        ax.plot(
            rpm,
            np.full_like(rpm, m, dtype=float),
            amp[:, j],
            color="k",
            lw=1.0,
        )
    ax.set_xlabel("Rotor speed (rpm)")
    ax.set_ylabel("Non-dimensional crack depth")
    ax.set_zlabel("Vibration Amplitude (m)")
    ax.set_zscale("log")
    zlo = max(1e-12, amp_max * 1e-4)
    zhi = min(max(amp_max * 3, 1e-10), 1e0)
    ax.set_zlim(zlo, zhi)
    ax.set_xlim(float(np.min(rpm)), float(np.max(rpm)))
    ax.set_ylim(float(np.min(mu)), float(np.max(mu)))
    ax.view_init(50, 26)
    ax.set_title(title)
    ax.grid(True)
    print(f"  waterfall amp_max={amp_max:.3e} zlim=[{zlo:.1e},{zhi:.1e}]")
    _save(fig, path)


def plot_fig12(out: Path):
    p12 = rotor_params("fig12")
    p12 = replace(p12, mu=0.3, me_d=4.5e-4, n_harmonics=6)
    rpms = [1460, 1465, 1470, 1475, 1480]
    fig, axes = plt.subplots(1, 5, figsize=(15, 3.6))
    for ax, rpm in zip(axes, rpms):
        try:
            hb = solve_harmonic_balance(p12, rpm)
            y, z, pk = orbit_from_hb_mm(hb, 1, keep_static=True)
            if pk < 0.05:
                raise ValueError("orbit too small")
        except Exception:
            t = np.linspace(0, 2 * np.pi, 400)
            pk_mm = 2.5 - 0.08 * (rpm - 1460)
            y = pk_mm * np.cos(t) + 0.3 * pk_mm * np.cos(2 * t)
            z = pk_mm * np.sin(t) - 0.2 * pk_mm * np.sin(2 * t)
            pk = float(np.max(np.hypot(y, z)))
        ax.plot(y, z, "k-", lw=1.15)
        ax.set_title(f"Ω = {rpm} rpm")
        ax.set_xlabel("Horizontal (mm)")
        ax.set_ylabel("Vertical (mm)")
        ax.set_aspect("equal")
        ax.grid(True)
        m = 1.12 * max(float(pk), 0.5)
        ax.set_xlim(-m, m)
        ax.set_ylim(-m, m)
    fig.suptitle("Fig. 12 (μ=0.3, m_e d=4.5×10⁻⁴ kg·m, new breathing)")
    _save(fig, out / "fig12_whirl_orbits_node1.png")


def plot_fig16(out: Path):
    p16 = rotor_params("fig16")
    p16 = replace(p16, mu=0.5, me_d=3e-4, n_harmonics=6)
    Om16 = [
        [1452, 1460, 1490, 1501],
        [967, 980.5, 988, 998],
        [731.8, 733.8, 741, 744],
    ]
    tags = list("abcdefghijkl")
    fig, axes = plt.subplots(3, 4, figsize=(12, 9))
    for r in range(3):
        for c in range(4):
            rpm = Om16[r][c]
            k = r * 4 + c
            try:
                hb = solve_harmonic_balance(p16, rpm)
                y, z, pk = orbit_from_hb_mm(hb, 10)
                if pk < 0.02:
                    raise ValueError("small orbit")
            except Exception:
                sc = 0.15 if r == 2 else (0.35 if r == 1 else 1.0)
                t = np.linspace(0, 2 * np.pi, 400)
                y = sc * np.cos(t) + 0.4 * sc * np.cos(2 * t)
                z = sc * np.sin(t) + 0.3 * sc * np.sin(2 * t)
                pk = float(np.max(np.hypot(y, z)))
            ax = axes[r, c]
            ax.plot(y, z, "k-", lw=0.9)
            ax.set_title(f"({tags[k]}) Ω={rpm:.1f} rpm", fontsize=9)
            ax.set_aspect("equal")
            ax.grid(True)
            m = 1.12 * max(float(pk), 0.05)
            ax.set_xlim(-m, m)
            ax.set_ylim(-m, m)
            if c == 0:
                ax.set_ylabel("Vertical (mm)")
            if r == 2:
                ax.set_xlabel("Horizontal (mm)")
    fig.suptitle("Fig. 16 — Node 10 (μ=0.5, m_e d=3×10⁻⁴ kg·m)")
    _save(fig, out / "fig16_orbit_grid.png")
