"""assemble_system.m, beam/crack elements, crack_stiffness_harmonics.m"""
import numpy as np
from .geometry import breathing_functions, crack_geometry
from .params import RotorParams, dof_indices


def beam_element_matrices(Le, E, I, rho, A):
    k = E * I / Le**3
    Ke_y = k * np.array(
        [
            [12, 6 * Le, -12, 6 * Le],
            [6 * Le, 4 * Le**2, -6 * Le, 2 * Le**2],
            [-12, -6 * Le, 12, -6 * Le],
            [6 * Le, 2 * Le**2, -6 * Le, 4 * Le**2],
        ]
    )
    m = rho * A * Le / 420
    Me_y = m * np.array(
        [
            [156, 22 * Le, 54, -13 * Le],
            [22 * Le, 4 * Le**2, 13 * Le, -3 * Le**2],
            [54, 13 * Le, 156, -22 * Le],
            [-13 * Le, -3 * Le**2, -22 * Le, 4 * Le**2],
        ]
    )
    iy, iz = [0, 1, 4, 5], [2, 3, 6, 7]
    Ke = np.zeros((8, 8))
    Me = np.zeros((8, 8))
    Ke[np.ix_(iy, iy)] = Ke_y
    Ke[np.ix_(iz, iz)] = Ke_y
    Me[np.ix_(iy, iy)] = Me_y
    Me[np.ix_(iz, iz)] = Me_y
    return Me, Ke


def crack_element_stiffness(Ix, Iy, Ixy, Le, E):
    Ix, Iy, Ixy = float(Ix), float(Iy), float(Ixy)
    coef = 48 * E / Le**3

    def block(I):
        return coef * np.array(
            [
                [12 * I, 6 * Le * I, -12 * I, 6 * Le * I],
                [6 * Le * I, 4 * Le**2 * I, -6 * Le * I, 2 * Le**2 * I],
                [-12 * I, -6 * Le * I, 12 * I, -6 * Le * I],
                [6 * Le * I, 2 * Le**2 * I, -6 * Le * I, 4 * Le**2 * I],
            ]
        )

    ky, kz = block(Iy), block(Ix)
    kc = coef * np.array(
        [
            [0, 0, 12 * Ixy, 6 * Le * Ixy],
            [0, 0, 6 * Le * Ixy, 4 * Le**2 * Ixy],
            [12 * Ixy, 6 * Le * Ixy, 0, 0],
            [6 * Le * Ixy, 4 * Le**2 * Ixy, 0, 0],
        ]
    )
    iy, iz = [0, 1, 4, 5], [2, 3, 6, 7]
    Ke = np.zeros((8, 8))
    Ke[np.ix_(iy, iy)] = ky
    Ke[np.ix_(iz, iz)] = kz
    Ke[np.ix_(iy, iz)] = kc
    Ke[np.ix_(iz, iy)] = kc.T
    return Ke


def transform_crack_stiffness(Kr, theta):
    """Eq. (6) — same as transform_crack_stiffness.m (blocks at DOF 1,5,3,7 in MATLAB)."""
    c, s = np.cos(theta), np.sin(theta)
    R2 = np.array([[c, -s], [s, c]])
    P = np.zeros((8, 8))
    for i in (0, 4, 2, 6):  # 0-based: MATLAB blocks(:,1) = [1, 5, 3, 7]
        P[i : i + 2, i : i + 2] = R2
    return P.T @ Kr @ P


def assemble_system(p: RotorParams):
    n_dof = 4 * p.n_nodes
    M = np.zeros((n_dof, n_dof))
    K = np.zeros((n_dof, n_dof))
    G = np.zeros((n_dof, n_dof))
    for e in range(1, p.n_elem + 1):
        idx = np.concatenate([dof_indices(e), dof_indices(e + 1)])
        Me, Ke = beam_element_matrices(p.Le, p.E, p.I_intact, p.rho, p.A)
        M[np.ix_(idx, idx)] += Me
        K[np.ix_(idx, idx)] += Ke
    for node in p.disk_nodes:
        d = dof_indices(node)
        G[d[1], d[2]] += p.Ip
        G[d[2], d[1]] -= p.Ip
        M[d[0], d[0]] += p.m_d
        M[d[2], d[2]] += p.m_d
        M[d[1], d[1]] += p.Id
        M[d[3], d[3]] += p.Id
    for node in p.bearing_nodes:
        d = dof_indices(node)
        K[d[0], d[0]] += p.k_b
        K[d[2], d[2]] += p.k_b
    C = np.zeros((n_dof, n_dof))
    if p.damped:
        for node in p.bearing_nodes:
            d = dof_indices(node)
            C[d[0], d[0]] += p.c_b
            C[d[2], d[2]] += p.c_b
    cn = [p.crack_elem, p.crack_elem + 1]
    crack_dofs = np.concatenate([dof_indices(cn[0]), dof_indices(cn[1])])
    return dict(M=M, K=K, G=G, C=C, n_dof=n_dof, crack_dofs=crack_dofs)


def embed_delta_k(n_dof, crack_dofs, K8):
    Kg = np.zeros((n_dof, n_dof))
    for a in range(8):
        for b in range(8):
            Kg[crack_dofs[a], crack_dofs[b]] = K8[a, b]
    return Kg


def _fourier_coeffs(y, cos_flag=True):
    N = len(y)
    idx = np.arange(N)
    if cos_flag:
        a = np.zeros(N)
        a[0] = np.mean(y)
        for k in range(1, N):
            a[k] = 2 / N * np.sum(y * np.cos(k * idx * 2 * np.pi / N))
        return a
    b = np.zeros(N)
    for k in range(1, N):
        b[k] = 2 / N * np.sum(y * np.sin(k * idx * 2 * np.pi / N))
    return b


def crack_stiffness_harmonics(p: RotorParams, n_harm: int, n_theta: int = 180):
    geom = crack_geometry(p.mu, p.R, p.c_neutral)
    geom.n_f1, geom.p_f2 = p.n_f1, p.p_f2
    _, K_intact = beam_element_matrices(p.Le, p.E, p.I_intact, p.rho, p.A)
    thetas = np.linspace(0, 2 * np.pi, n_theta, endpoint=False)
    K_series = np.zeros((8, 8, n_theta))
    for i, th in enumerate(thetas):
        _, _, Ix, Iy, Ixy = breathing_functions(th, geom, p.n_f1, p.p_f2)
        Kr = crack_element_stiffness(Ix, Iy, Ixy, p.Le, p.E)
        K_series[:, :, i] = transform_crack_stiffness(Kr, th)
    K_mean = K_series.mean(axis=2)
    dK = K_series - K_mean[:, :, None]
    K_cos = [np.zeros((8, 8)) for _ in range(n_harm + 1)]
    K_sin = [np.zeros((8, 8)) for _ in range(n_harm + 1)]
    K_cos[0] = K_mean - K_intact
    for ii in range(8):
        for jj in range(8):
            y = dK[ii, jj, :]
            ac = _fourier_coeffs(y, True)
            bs = _fourier_coeffs(y, False)
            for k in range(1, min(n_harm, len(ac) - 1) + 1):
                K_cos[k][ii, jj] = ac[k]
                K_sin[k][ii, jj] = bs[k]
    return K_cos, K_sin, K_intact
