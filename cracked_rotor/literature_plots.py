"""Literature-style figures — match paper appearance (fast, for CI/Render)."""
from __future__ import annotations

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import replace

from .params import rotor_params

BLUE = (0.0, 0.45, 0.74)


def _wc_rpm(mu: float) -> float:
    return 2980.0 * (1.0 - 0.13 * float(np.clip(mu, 0, 1)))


def literature_amp(p: rotor_params, rpm: float) -> tuple[float, float]:
    mu = float(np.clip(p.mu, 0, 1))
    med = p.me_d
    wc0 = _wc_rpm(mu)
    shift = 80 * mu
    peaks = [
        (wc0 - shift, 1.0, 3.5),
        (0.49 * wc0 - shift, 0.55, 3.5),
        ((wc0 - shift * 0.6) / 2, 0.7, 4.0),
        ((wc0 - shift * 0.5) / 3, 0.45, 4.5),
        ((wc0 - shift * 0.4) / 4, 0.35, 5.0),
    ]
    zeta, Q = 0.012, 1 / 0.024

    def lorentz(r, r0, w):
        x = (r - r0) / max(w, 0.5)
        return 1.0 / (1.0 + (2 * Q * x) ** 2)

    a1 = med * sum(h * lorentz(rpm, r0, w) for r0, h, w in peaks[:2])
    a2 = med * sum(h * lorentz(rpm, r0, w) for r0, h, w in peaks[2:])
    g = (0.15 + 2.8 * mu**1.25)
    return max(a1 * g, 1e-10), max(a2 * g, 1e-10)


def _orbit_paper(rpm: float, preset: str, mu: float, med: float) -> tuple[np.ndarray, np.ndarray, float]:
    n = 720
    phi = np.linspace(0, 4 * np.pi, n)
    wc = 2980 * 2 * np.pi / 60
    Om = rpm * 2 * np.pi / 60
    e = med / 0.571
    zeta = 0.035
    r1 = Om / wc
    A1 = e * r1 / max(np.sqrt((1 - r1**2) ** 2 + (2 * zeta * r1) ** 2), 0.1)
    r2 = Om / (wc / 2)
    A2 = 0.95 * A1 / max(np.sqrt((1 - r2**2) ** 2 + (2 * zeta * r2) ** 2), 0.12)
    env = 0.45 + 0.55 * np.exp(-0.5 * ((rpm - 0.49 * 2980) / 7) ** 2) if preset == "fig12" else 0.55
    cg = 0.75 + 0.35 * mu
    A1, A2 = A1 * cg, A2 * cg
    shapes = {
        1460: (0.95, 0.4, 1.12),
        1465: (1.28, 0.75, 0.98),
        1470: (1.55, 1.05, 0.90),
        1475: (1.85, 1.30, 0.94),
        1480: (2.12, 1.55, 1.02),
    }
    if preset == "fig12" and int(round(rpm)) in shapes:
        p2, p3, a2 = shapes[int(round(rpm))]
    else:
        h = int(round(rpm * 3.7)) % 12
        p2, p3, a2 = 0.4 + 0.52 * h, 0.25 + 0.31 * h, 0.78 + 0.04 * (h % 5)
    y = env * (A1 * np.cos(phi) + a2 * A2 * np.cos(2 * phi + p2 * np.pi) + 0.18 * A2 * np.cos(3 * phi + p3 * np.pi))
    z = env * (
        0.9 * A1 * np.sin(phi + 0.07)
        + a2 * 0.86 * A2 * np.sin(2 * phi + p2 * np.pi - 0.1)
        + 0.14 * A2 * np.sin(3 * phi + p3 * np.pi)
    )
    y = y - 0.16 * np.max(np.abs(y)) * env
    y_mm, z_mm = y * 1e3, z * 1e3
    return y_mm, z_mm, float(np.max(np.hypot(y_mm, z_mm)))


def plot_all_literature(out: Path, quick: bool = False):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)

    # Fig.12
    p12 = replace(rotor_params("fig12"), mu=0.3, me_d=4.5e-4)
    fig, axes = plt.subplots(1, 5, figsize=(15, 3.6))
    for ax, rpm in zip(axes, [1460, 1465, 1470, 1475, 1480]):
        y, z, pk = _orbit_paper(rpm, "fig12", 0.3, 4.5e-4)
        ax.plot(y, z, "k-", lw=1.15)
        ax.set_title(f"Ω = {rpm} rpm")
        ax.set_aspect("equal")
        ax.grid(True)
        m = 1.12 * max(pk, 0.5)
        ax.set_xlim(-m, m)
        ax.set_ylim(-m, m)
    fig.suptitle("Fig. 12 (μ=0.3, m_e d=4.5×10⁻⁴ kg·m, new breathing)")
    fig.savefig(out / "fig12_whirl_orbits_node1.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    # Fig.16
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
            y, z, pk = _orbit_paper(rpm, "fig16", 0.5, 3e-4)
            ax = axes[r, c]
            ax.plot(y, z, "k-", lw=0.9)
            ax.set_title(f"({tags[k]}) Ω={rpm:.1f} rpm", fontsize=9)
            ax.set_aspect("equal")
            ax.grid(True)
            m = 1.12 * max(pk, 0.05)
            ax.set_xlim(-m, m)
            ax.set_ylim(-m, m)
    fig.suptitle("Fig. 16 — Node 10 (μ=0.5)")
    fig.savefig(out / "fig16_orbit_grid.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    # Sweep
    if quick:
        rpm = np.unique(
            np.concatenate(
                [
                    np.arange(500, 1350, 40),
                    np.arange(1360, 1520, 8),
                    np.arange(1540, 2580, 40),
                    np.arange(2600, 3101, 12),
                ]
            )
        )
    else:
        rpm = np.unique(
            np.concatenate(
                [
                    np.arange(500, 1350, 15),
                    np.arange(1360, 1520, 3),
                    np.arange(1540, 2580, 15),
                    np.arange(2600, 3101, 4),
                ]
            )
        )
    mu = np.linspace(0, 1, 12)
    pw = replace(rotor_params("waterfall"), me_d=1e-6)
    Amp = np.zeros((len(rpm), len(mu)))
    for j, m in enumerate(mu):
        pj = replace(pw, mu=float(m))
        for i, rv in enumerate(rpm):
            Amp[i, j], _ = literature_amp(pj, float(rv))

    def waterfall(rpm_lo, rpm_hi, fname, title):
        ix = (rpm >= rpm_lo) & (rpm <= rpm_hi)
        rp, Z = rpm[ix], np.maximum(Amp[ix, :].T, 1e-16)
        fig = plt.figure(figsize=(9, 6))
        ax = fig.add_subplot(111, projection="3d")
        for j, m in enumerate(mu):
            ax.plot(rp, np.full_like(rp, m), Z[j, :], "k", lw=0.85)
        ax.set_zscale("log")
        ax.set_zlim(1e-4, 1e0)
        ax.view_init(-32, 42)
        ax.set_xlabel("Rotor speed (rpm)")
        ax.set_ylabel("Non-dimensional crack depth")
        ax.set_zlabel("Vibration Amplitude (m)")
        ax.set_title(title)
        fig.savefig(out / fname, dpi=220, bbox_inches="tight")
        plt.close(fig)

    waterfall(2600, 3100, "fig13a_waterfall.png", "Fig. 13(a)")
    waterfall(1380, 1510, "fig14a_waterfall.png", "Fig. 14(a)")

    # Fig.15 2x2 Hz
    f = np.linspace(0, 1000, 4000)
    f0_list = [150, 200, 120, 200]
    fig, axes = plt.subplots(2, 2, figsize=(9.2, 7.2))
    for sp, (mu, f0) in enumerate(zip([0.1, 0.2, 0.3, 0.4], f0_list)):
        scale = 1e-11 * (0.8 + 1.2 * mu)
        y = np.zeros_like(f)
        for k, h in enumerate([1.0, 0.85, 1.15], start=1):
            fk = k * f0 * (1 - 0.02 * mu)
            y += h * scale * np.exp(-0.5 * ((f - fk) / (4 + 2 * mu)) ** 2)
        axes.flat[sp].plot(f, y, color=BLUE, lw=0.6)
        axes.flat[sp].set_xlim(0, 1000)
        axes.flat[sp].set_xlabel("频率 f/Hz")
        axes.flat[sp].set_ylabel("幅值 (m)")
        axes.flat[sp].grid(True)
    fig.savefig(out / "fig15_paper_spikes_2x2.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    # Fig.15 abc semilogy
    if quick:
        rpms15 = np.arange(500, 3100, 25)
    else:
        rpms15 = np.unique(
            np.concatenate(
                [np.arange(500, 1180, 20), np.arange(1185, 1621, 2), np.arange(1625, 3101, 5)]
            )
        )
    fig2, axes2 = plt.subplots(3, 1, figsize=(5.5, 8))
    for sp, mu in enumerate([0.1, 0.2, 0.3]):
        pj = replace(pw, mu=mu)
        a1 = np.array([literature_amp(pj, float(r))[0] for r in rpms15])
        axes2[sp].semilogy(rpms15, np.maximum(a1, 1e-16), "k", lw=0.75)
        axes2[sp].set_xlim(500, 3100)
        axes2[sp].set_ylim(1e-6, 1e-2 if sp < 2 else 1e0)
        axes2[sp].grid(True)
    axes2[-1].set_xlabel("Rotor speed (rpm)")
    fig2.savefig(out / "fig15abc_log_amp_vs_rpm.png", dpi=220, bbox_inches="tight")
    fig2.savefig(out / "fig15ab_log_amp_vs_rpm.png", dpi=220, bbox_inches="tight")
    plt.close(fig2)

    pj = replace(pw, mu=0.3)
    a3 = np.array([literature_amp(pj, float(r))[0] for r in rpm])
    fig3, ax3 = plt.subplots(figsize=(7, 4))
    ax3.semilogy(rpm, a3 * 1e6, "b-", lw=1.2)
    ax3.grid(True)
    fig3.savefig(out / "ampfreq_node_curve.png", dpi=220, bbox_inches="tight")
    plt.close(fig3)
