"""Table 3 + Fig.10/11 — mirrors rotor_params.m"""
from dataclasses import dataclass, field
import numpy as np


@dataclass
class RotorParams:
    L: float = 0.724
    R: float = 15.88e-3
    rho: float = 7800.0
    E: float = 2.1e11
    R_o: float = 0.0762
    R_i: float = 15.88e-3
    m_d: float = 0.571
    k_b: float = 7e7
    c_b: float = 500.0
    mu: float = 0.3
    n_f1: int = 12
    p_f2: int = 16
    c_neutral: float = 0.0
    n_elem: int = 18
    crack_elem: int = 6
    disk_nodes: tuple = (4,)
    unbalance_node: int = 16
    bearing_nodes: tuple = (1, 19)
    me_d: float = 1e-6
    beta: float = 0.0
    n_harmonics: int = 4
    damped: bool = True
    zeta_hb: float = 0.008
    hb_reg_scale: float = 3e-4
    g: float = 9.81

    @property
    def n_nodes(self) -> int:
        return self.n_elem + 1

    @property
    def Le(self) -> float:
        return self.L / self.n_elem

    @property
    def A(self) -> float:
        return np.pi * self.R**2

    @property
    def I_intact(self) -> float:
        return np.pi * self.R**4 / 4

    @property
    def Id(self) -> float:
        return 0.25 * self.m_d * (self.R_o**2 + self.R_i**2)

    @property
    def Ip(self) -> float:
        return 0.5 * self.m_d * (self.R_o**2 + self.R_i**2)


def dof_indices(node: int) -> np.ndarray:
    base = (node - 1) * 4
    return np.arange(base, base + 4)


def rotor_params(preset: str = "table3") -> RotorParams:
    p = RotorParams()
    preset = (preset or "table3").lower()
    if preset == "fig12":
        p.mu, p.me_d, p.n_harmonics = 0.3, 4.5e-4, 6
    elif preset == "fig16":
        p.mu, p.me_d, p.n_harmonics = 0.5, 3e-4, 6
    elif preset == "waterfall":
        p.me_d, p.n_harmonics = 1e-6, 4
    return p
