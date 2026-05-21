"""get_paper_amp + resonance fallback — mirrors get_paper_amp.m / amp_resonance_model.m"""
from __future__ import annotations

import numpy as np

from .harmonic_balance import harmonic_amp_node, solve_harmonic_balance
from .params import RotorParams


def literature_wc_rpm(p: RotorParams, mu: float | None = None) -> float:
    wc0 = 2980.0
    if mu is None:
        return wc0
    return wc0 * (1.0 - 0.13 * float(np.clip(mu, 0, 1)))


def amp_resonance_model(p: RotorParams, rpm: float, node: int = 10) -> tuple[float, float]:
    zeta = 0.025
    mu = float(np.clip(p.mu, 0, 1))
    e = p.me_d / max(p.m_d, 0.571)
    Om = rpm * 2 * np.pi / 60
    wc_rpm = literature_wc_rpm(p, mu)
    wc1 = wc_rpm * 2 * np.pi / 60
    wc2 = 0.49 * wc1
    r1 = Om / max(wc1, 1e-6)
    den1 = max(np.sqrt((1 - r1**2) ** 2 + (2 * zeta * r1) ** 2), 0.06)
    a1 = e * r1 / den1
    r2 = Om / max(wc2, 1e-6)
    den2 = max(np.sqrt((1 - r2**2) ** 2 + (2 * zeta * r2) ** 2), 0.10)
    a2 = e * r2 / den2
    crack_gain = 0.08 + 2.2 * mu**1.3
    a1 *= crack_gain
    a2 *= crack_gain * (0.45 + 0.55 * mu)
    if mu < 1e-4:
        return 5e-10, 2e-10
    return max(a1, 1e-10), max(a2, 1e-10)


def get_paper_amp(p: RotorParams, rpm: float, node: int = 10) -> tuple[float, float, str]:
    try:
        hb = solve_harmonic_balance(p, float(rpm))
        a1h = harmonic_amp_node(hb, node, 1)
        a2h = harmonic_amp_node(hb, node, 2)
        if np.isfinite(a1h) and a1h > 1e-12:
            return float(a1h), float(max(a2h, 0)), "HB"
    except Exception:
        pass
    a1, a2 = amp_resonance_model(p, rpm, node)
    return a1, a2, "model"
