"""crack_geometry.m + breathing_functions.m"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass
class CrackGeom:
    I: float
    Ix: float
    Iy: float
    I1: float
    I2: float
    I1_bar: float
    I2_bar: float
    A1: float
    e: float
    theta1: float
    theta2: float
    gamma: float
    n_f1: int = 12
    p_f2: int = 16


def crack_geometry(mu: float, R: float, c: float = 0.0) -> CrackGeom:
    mu = float(np.clip(mu, 1e-6, 0.95))
    gamma = np.sqrt(mu * (2 - mu))
    I = np.pi / 4 * R**4
    Ix = np.pi / 8 * R**4 - R**4 / 4 * (
        (1 - mu) ** 2 * (2 * mu**2 - 4 * mu + 1) * gamma + np.arcsin(1 - mu)
    )
    Iy = np.pi / 4 * R**4 - R**4 / 12 * (
        (1 - mu) ** 2 * (2 * mu**2 - 4 * mu - 3) * gamma + 3 * np.arcsin(gamma)
    )
    I1, I2 = I - Ix, I - Iy
    A1 = R**2 * (np.pi - np.arccos(1 - mu) + (1 - mu) * gamma)
    e = 2 * R**3 / (3 * A1) * (mu * (2 - mu)) ** 1.5
    th1 = np.arctan2(e + R * (1 - mu), R * gamma)
    if c != 0:
        th1 = np.arctan2(c + R * (1 - mu), R * gamma)
    th2 = np.pi / 2 + np.arccos(1 - mu)
    return CrackGeom(I, Ix, Iy, I1, I2, I1 - A1 * e**2, I2, A1, e, th1, th2, gamma)


def breathing_functions(theta, geom: CrackGeom, n: Optional[int] = None, p: Optional[int] = None):
    scalar_in = np.isscalar(theta)
    theta = np.atleast_1d(theta).astype(float)
    n = n or geom.n_f1
    p = p or geom.p_f2
    f1 = 0.5 * np.cos(theta) ** n
    val = (geom.theta1 + geom.theta2) / (2 * np.pi)
    denom = geom.theta2 - geom.theta1
    f2 = np.full_like(theta, val, dtype=float)
    if abs(denom) > 1e-14:
        for i in range(1, p + 1):
            f2 -= (
                2
                / denom
                * (np.cos(i * geom.theta2) - np.cos(i * geom.theta1))
                / i**2
                * np.cos(i * theta)
            )
    I1, I2, I = geom.I1, geom.I2, geom.I
    Ix = I - (I - I1) * f1
    Iy = I + (I - I1) * f1 - 2 * (I - I1 - I2) * f2
    Ixy = (-(I1 - I2) / 2 + geom.A1 * geom.e**2 / 2) * np.sin(2 * theta)
    if scalar_in:
        return float(f1[0]), float(f2[0]), float(Ix[0]), float(Iy[0]), float(Ixy[0])
    return f1, f2, Ix, Iy, Ixy
