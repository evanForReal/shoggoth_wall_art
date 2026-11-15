"""Anchor screw-group hand calc (rigid plate, elastic screw group) + head pull-through + joint pin shear.
Independent of FEA. Frame: wall plane X=0, +X out of wall, screws at (y,z) positions. Reaction (F, M) = force/moment the
SUPPORT exerts on the structure, at origin; the load on the screw group is the opposite, but we only need magnitudes + signs
consistent: screw tension (pull-out, +X on the screw) arises from the structure's pull-away: demand = -reaction.
"""
from __future__ import annotations
import numpy as np


def group_loads(F_react, M_react, pos_yz, active, plate_z_edge=None, plate_y_edge=None):
    """Return per-screw dict for active screw indices. Demand on screw group = -reaction.
    Model A (screws-only elastic group): tension from axial force and moments about group centroid.
    If the active set has zero lever arm about an axis, pivot-at-plate-edge model is used for that axis (flagged)."""
    F = -np.asarray(F_react, float); M = -np.asarray(M_react, float)   # load applied to anchor by structure
    P = np.asarray(pos_yz, float)[active]
    n = len(P)
    cy, cz = P.mean(0)
    dy = P[:, 0] - cy; dz = P[:, 1] - cz
    Syy = (dy ** 2).sum(); Szz = (dz ** 2).sum()
    # moment about origin -> about centroid (shift): M_c = M - r_c x F, r_c=(0,cy,cz)
    rc = np.array([0.0, cy, cz])
    Mc = M - np.cross(rc, F)
    notes = []
    T = np.full(n, F[0] / n)
    # tension from M_y (about Y axis): force +X at height z gives moment about y = z * Fx  -> Tz_i = My*dz/Szz
    if Szz > 1e-6:
        T += Mc[1] * dz / Szz
    else:
        notes.append("zero vertical lever arm: M_y resisted by plate bearing (pivot-edge model used)")
        zp = (plate_z_edge if plate_z_edge is not None else -55.0)
        d = (P[:, 1] - zp); T += (M[1]) * d / (d ** 2).sum()
    # moment about Z axis: force +X at y gives moment about z = -y * Fx
    if Syy > 1e-6:
        T += -Mc[2] * dy / Syy
    else:
        notes.append("zero lateral lever arm: M_z resisted by plate bearing (pivot-edge model used)")
        yp = (plate_y_edge if plate_y_edge is not None else -80.0)
        d = (P[:, 0] - yp); T += (-M[2]) * d / (d ** 2).sum()
    # shear: Fy, Fz shared, torsion Mx about group centroid
    Jp = Syy + Szz
    Vy = np.full(n, F[1] / n); Vz = np.full(n, F[2] / n)
    if Jp > 1e-6:
        # torque Mc_x = sum(y*Vz - z*Vy)
        Vy += -Mc[0] * dz / Jp
        Vz += Mc[0] * dy / Jp
    V = np.hypot(Vy, Vz)
    return {"T_N": T.round(2).tolist(), "V_N": V.round(2).tolist(), "T_max": float(T.max()), "V_max": float(V.max()), "notes": notes}


def screw_util(g, cap, sf_req):
    """interaction (T+/Tu + V/Vu); T<0 (compression) ignored. returns util (<=1/sf passes) and SF."""
    T = np.maximum(np.array(g["T_N"]), 0.0); V = np.array(g["V_N"])
    u = T / cap["tension"] + V / cap["shear"]
    ui = float(u.max())
    return {"util": ui, "SF": float(1.0 / max(ui, 1e-12)), "sf_required": sf_req, "pass": bool(1.0 / max(ui, 1e-12) >= sf_req)}


def head_pullthrough(T, d_head, t_plate, d_hole, allow_z):
    tau = 0.577 * allow_z
    cap = np.pi * d_head * t_plate * tau
    return {"capacity_N": float(cap), "SF": float(cap / max(T, 1e-9)), "note": "punching shear around head, through-layer allowable 0.577*allow_z"}


def pin_shear(V, d_pin, n_pin, tau_ult):
    area = n_pin * np.pi * d_pin ** 2 / 4
    tau = V / area
    return {"tau_MPa": float(tau), "SF": float(tau_ult / max(tau, 1e-9))}
