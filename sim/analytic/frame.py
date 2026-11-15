"""3D Euler-Bernoulli frame (12 dof/node) solved along the centerline stations. Independent of voxel FEA.
Units mm, N, MPa, tonne. Static: root fixed. Modal: consistent mass, generalized eigenproblem (dense)."""
from __future__ import annotations
import numpy as np
import scipy.linalg as sla

G_ACC = 9810.0


def _local_axes(p0, p1, u_ref):
    ex = p1 - p0; L = np.linalg.norm(ex); ex = ex / L
    ey = u_ref - ex * (ex @ u_ref); ey /= np.linalg.norm(ey)
    ez = np.cross(ex, ey)
    return L, np.vstack([ex, ey, ez])


def beam_k(E, G, A, Iy, Iz, J, L, kappa=0.0):
    """12x12 local stiffness. Iy: bending about local y (deflection in z), Iz about z (deflection in y)."""
    K = np.zeros((12, 12))
    EA = E * A / L
    K[0, 0] = K[6, 6] = EA; K[0, 6] = K[6, 0] = -EA
    GJ = G * J / L
    K[3, 3] = K[9, 9] = GJ; K[3, 9] = K[9, 3] = -GJ
    # bending in x-y plane (about z): dofs v(1,7), thz(5,11)
    a = E * Iz / L ** 3
    idx = [1, 5, 7, 11]
    k = a * np.array([[12, 6 * L, -12, 6 * L], [6 * L, 4 * L * L, -6 * L, 2 * L * L], [-12, -6 * L, 12, -6 * L], [6 * L, 2 * L * L, -6 * L, 4 * L * L]])
    K[np.ix_(idx, idx)] += k
    # bending in x-z plane (about y): w(2,8), thy(4,10); sign flips for coupling
    b = E * Iy / L ** 3
    idx = [2, 4, 8, 10]
    k = b * np.array([[12, -6 * L, -12, -6 * L], [-6 * L, 4 * L * L, 6 * L, 2 * L * L], [-12, 6 * L, 12, 6 * L], [-6 * L, 2 * L * L, 6 * L, 4 * L * L]])
    K[np.ix_(idx, idx)] += k
    return K


def beam_m(rhoA, rhoJ, L):
    M = np.zeros((12, 12))
    m = rhoA * L
    M[0, 0] = M[6, 6] = m / 3; M[0, 6] = M[6, 0] = m / 6
    M[3, 3] = M[9, 9] = rhoJ * L / 3; M[3, 9] = M[9, 3] = rhoJ * L / 6
    c = m / 420
    for idx, sg in (([1, 5, 7, 11], 1), ([2, 4, 8, 10], -1)):
        k = c * np.array([[156, sg * 22 * L, 54, -sg * 13 * L], [sg * 22 * L, 4 * L * L, sg * 13 * L, -3 * L * L], [54, sg * 13 * L, 156, -sg * 22 * L], [-sg * 13 * L, -3 * L * L, -sg * 22 * L, 4 * L * L]])
        M[np.ix_(idx, idx)] += k
    return M


def solve_frame(stations, E, nu, rho, extra_mass=None, loads=None, self_weight=True, skin_rhoA=None, modal=True, rho_fac_A=None):
    """stations: list of dicts from sections_along (need p, u, A_eff, Iu, Iv, J, and rhoA_eff).
    loads: list of (point_xyz, force_xyz) applied at nearest node. extra_mass: list of (point_xyz, mass_tonne).
    returns dict(disp (n,6), elem_forces, reaction, freqs)"""
    n = len(stations)
    Gm = E / (2 * (1 + nu))
    nd = 6 * n
    K = np.zeros((nd, nd)); Mg = np.zeros((nd, nd)); f = np.zeros(nd)
    Tm = []
    for i in range(n - 1):
        a, b = stations[i], stations[i + 1]
        L, R = _local_axes(a["p"], b["p"], 0.5 * (a["u"] + b["u"]))
        A = 0.5 * (a["A_eff"] + b["A_eff"])
        Iu = 0.5 * (a["Iu"] + b["Iu"]); Iv = 0.5 * (a["Iv"] + b["Iv"]); J = 0.5 * (a["J"] + b["J"])
        # local y = u (lateral), z = v (up): Iy (about y) = int z^2 = Iu ; Iz = int y^2 = Iv
        ke = beam_k(E, Gm, A, Iu, Iv, J, L)
        rA = 0.5 * (a["rhoA"] + b["rhoA"]) * 1.0
        me = beam_m(rA, rA * (Iu + Iv) / max(A, 1e-9), L)
        T = np.zeros((12, 12))
        for k in range(4):
            T[3 * k:3 * k + 3, 3 * k:3 * k + 3] = R
        Tm.append((T, ke, L, R))
        dof = np.r_[6 * i:6 * i + 6, 6 * (i + 1):6 * (i + 1) + 6]
        K[np.ix_(dof, dof)] += T.T @ ke @ T
        Mg[np.ix_(dof, dof)] += T.T @ me @ T
        if self_weight:
            w = rA * L * G_ACC
            f[6 * i + 2] -= w / 2; f[6 * (i + 1) + 2] -= w / 2
    pts = np.array([s["p"] for s in stations])
    if extra_mass:
        for pt, m in extra_mass:
            j = int(np.argmin(np.linalg.norm(pts - pt, axis=1)))
            for d in range(3):
                Mg[6 * j + d, 6 * j + d] += m
            if self_weight:
                f[6 * j + 2] -= m * G_ACC
    if loads:
        for pt, F in loads:
            j = int(np.argmin(np.linalg.norm(pts - pt, axis=1)))
            f[6 * j:6 * j + 3] += F
            # moment from eccentricity (load point vs node)
            r = np.asarray(pt) - pts[j]
            f[6 * j + 3:6 * j + 6] += np.cross(r, F)
    free = np.arange(6, nd)
    u = np.zeros(nd)
    u[free] = np.linalg.solve(K[np.ix_(free, free)], f[free])
    react = K[:6, :] @ u - f[:6]
    # internal forces at element ends (local), element i: end a (node i), end b (node i+1)
    ef = []
    for i, (T, ke, L, R) in enumerate(Tm):
        dof = np.r_[6 * i:6 * i + 6, 6 * (i + 1):6 * (i + 1) + 6]
        fl = ke @ (T @ u[dof])   # forces on element at its ends (local)
        ef.append(fl)
    res = {"u": u.reshape(n, 6), "ef": np.array(ef), "react": react, "K": K, "M": Mg, "free": free, "pts": pts}
    if modal:
        w2 = sla.eigh(K[np.ix_(free, free)], Mg[np.ix_(free, free)], eigvals_only=True, subset_by_index=[0, 5])
        res["freq"] = np.sqrt(np.abs(w2)) / (2 * np.pi)
    return res
