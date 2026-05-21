"""solve_harmonic_balance.m"""
import numpy as np
from scipy.linalg import solve

from .fe import assemble_system, crack_stiffness_harmonics, embed_delta_k
from .params import RotorParams, dof_indices


def _idx_slice(n_dof, Nh, k, is_cos):
    if k == 0:
        return slice(0, n_dof)
    j = 1 + 2 * (k - 1) + (0 if is_cos else 1)
    a = j * n_dof
    return slice(a, a + n_dof)


def _estimate_wc(K, M):
    try:
        lam, _ = np.linalg.eig(np.linalg.solve(M, K))
        lam = np.real(lam)
        lam = lam[lam > 0]
        return max(np.sqrt(lam.min()) if lam.size else 1.0, 2 * np.pi * 5)
    except Exception:
        return max(np.sqrt(K[0, 0] / max(M[0, 0], 1e-9)), 2 * np.pi * 5)


def hb_solve_regularized(A, b, reg_scale=1.0):
    n = A.shape[0]
    nf = np.linalg.norm(A, "fro")
    rc = np.linalg.cond(A)
    epsr = reg_scale * (1e-4 if rc > 1e11 or not np.isfinite(rc) else 1e-10) * max(nf / np.sqrt(n), 1)
    for _ in range(4):
        try:
            sol = solve(A + epsr * np.eye(n), b, assume_a="pos")
            if np.all(np.isfinite(sol)):
                return sol
        except Exception:
            pass
        epsr *= 10
    return np.linalg.pinv(A, rcond=1e-6) @ b


def solve_harmonic_balance(p: RotorParams, rpm: float):
    Omega = rpm * 2 * np.pi / 60
    sys = assemble_system(p)
    n_dof = sys["n_dof"]
    cd = sys["crack_dofs"]
    Nh = p.n_harmonics
    M, K, G, C = sys["M"], sys["K"], sys["G"], sys["C"].copy()
    if p.damped:
        for node in p.bearing_nodes:
            d = dof_indices(node)
            C[d[0], d[0]] += p.c_b
            C[d[2], d[2]] += p.c_b
    zeta = p.zeta_hb
    wc = _estimate_wc(K, M)
    C = C + 2 * zeta * wc * M
    K_cos, K_sin, _ = crack_stiffness_harmonics(p, Nh)
    dK0 = embed_delta_k(n_dof, cd, K_cos[0])
    n_u = n_dof * (1 + 2 * Nh)
    A = np.zeros((n_u, n_u))
    b = np.zeros(n_u)
    F0 = np.zeros(n_dof)
    for node in p.disk_nodes:
        d = dof_indices(node)
        F0[d[2]] -= p.m_d * p.g
    me_w2 = p.me_d * Omega**2
    sl0 = _idx_slice(n_dof, Nh, 0, True)
    A[sl0, sl0] = K + dK0
    b[sl0] = F0
    for k in range(1, Nh + 1):
        ic = _idx_slice(n_dof, Nh, k, True)
        is_ = _idx_slice(n_dof, Nh, k, False)
        Kblk = K + dK0 - (k * Omega) ** 2 * M
        Dblk = k * Omega * (C + Omega * G)
        A[ic, ic] = Kblk
        A[is_, is_] = Kblk
        A[ic, is_] = Dblk
        A[is_, ic] = -Dblk
        for j in range(1, Nh + 1):
            dKjc = embed_delta_k(n_dof, cd, K_cos[j])
            dKjs = embed_delta_k(n_dof, cd, K_sin[j])
            if k - j >= 1:
                kk = k - j
                slc = _idx_slice(n_dof, Nh, kk, True)
                sls = _idx_slice(n_dof, Nh, kk, False)
                A[ic, slc] += 0.5 * dKjc
                A[ic, sls] += 0.5 * dKjs
                A[is_, slc] += 0.5 * dKjs
                A[is_, sls] -= 0.5 * dKjc
            if k + j <= Nh:
                kk = k + j
                slc = _idx_slice(n_dof, Nh, kk, True)
                sls = _idx_slice(n_dof, Nh, kk, False)
                A[ic, slc] += 0.5 * dKjc
                A[ic, sls] -= 0.5 * dKjs
                A[is_, slc] -= 0.5 * dKjs
                A[is_, sls] -= 0.5 * dKjc
        if k == 1:
            d = dof_indices(p.unbalance_node)
            b[ic] = b[ic].copy()
            b[is_] = b[is_].copy()
            b[ic][d[0]] += me_w2 * np.cos(p.beta)
            b[is_][d[2]] += me_w2 * np.sin(p.beta)
    sol = hb_solve_regularized(A, b, p.hb_reg_scale)
    q0 = sol[sl0]
    harmonics = []
    for k in range(1, Nh + 1):
        harmonics.append(
            dict(
                qc=sol[_idx_slice(n_dof, Nh, k, True)],
                qs=sol[_idx_slice(n_dof, Nh, k, False)],
            )
        )
    return dict(rpm=rpm, Omega=Omega, q0=q0, harmonics=harmonics, n_dof=n_dof)


def harmonic_amp_node(hb, node: int, k_harm: int) -> float:
    d = dof_indices(node)
    if k_harm < 1 or k_harm > len(hb["harmonics"]):
        return 0.0
    h = hb["harmonics"][k_harm - 1]
    qc, qs = h["qc"], h["qs"]
    return float(
        np.sqrt(qc[d[0]] ** 2 + qs[d[0]] ** 2 + qc[d[2]] ** 2 + qs[d[2]] ** 2)
    )


def orbit_from_hb_mm(hb, node: int, keep_static=False, period_factor=2, n_phase=720):
    d = dof_indices(node)
    phi = np.linspace(0, 2 * np.pi * period_factor, n_phase)
    y = hb["q0"][d[0]] * np.ones_like(phi)
    z = hb["q0"][d[2]] * np.ones_like(phi)
    for k, h in enumerate(hb["harmonics"], start=1):
        qc, qs = h["qc"], h["qs"]
        y += qc[d[0]] * np.cos(k * phi) + qs[d[0]] * np.sin(k * phi)
        z += qc[d[2]] * np.cos(k * phi) + qs[d[2]] * np.sin(k * phi)
    if not keep_static:
        y -= y.mean()
        z -= z.mean()
    y_mm, z_mm = y * 1e3, z * 1e3
    return y_mm, z_mm, float(np.max(np.hypot(y_mm, z_mm)))
