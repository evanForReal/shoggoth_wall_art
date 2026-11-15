#!/usr/bin/env python3
"""Back-of-envelope checks on the *geometry* (shell-only section properties; ribs neglected = conservative).
Not the Verification-region analytic report. Writes reports/analytic_geometry_prelim.md/.json.
    python prototype/p0/analytic_geometry_prelim.py"""
import argparse, json, os, sys
import numpy as np
import trimesh
from shapely.geometry import Polygon
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from model.structural.profile import Span, rrect_polygon   # noqa: E402
from model.mtools import to_trimesh, to_manifold              # noqa: E402
import manifold3d as m3d

_ap = argparse.ArgumentParser()
_ap.add_argument("--params", default=os.path.join(ROOT, "prototype/p0/params.json"))
_ap.add_argument("--out", default=os.path.join(ROOT, "prototype/p0/out"))
_ap.add_argument("--report-dir", default=os.path.join(ROOT, "prototype/p0/reports"))
_a = _ap.parse_args()
OUT = _a.out
p = json.load(open(_a.params))
man = json.load(open(os.path.join(OUT, "geometry_manifest.json")))
sp = Span(p)
MAT = p["materials"][p["material"]]          # E, nu, rho (g/cm3), allowables from params.json
E, NU = float(MAT["E"]), float(MAT["nu"])
G = E / (2 * (1 + NU))
RHO_KG_MM3 = float(MAT["rho_g_cm3"]) * 1e-6  # kg/mm3
g = 9.81
t = p["shell_wall"]
SIG_Z, SIG_XY = float(MAT["sigma_z"]), float(MAT["sigma_xy"])


def props(s):
    A, B, R = sp.ABR(np.array([s]))
    Ai, Bi, Ri = sp.ABR(np.array([s]), t)
    Po = Polygon(rrect_polygon(A[0], B[0], R[0], 256)); Pi = Polygon(rrect_polygon(Ai[0], Bi[0], Ri[0], 256))
    ring = Po.difference(Pi)
    # section second moments about centroid (shapely: use polygon integration)
    def I(poly):
        x, y = np.array(poly.exterior.coords).T
        a = x[:-1] * y[1:] - x[1:] * y[:-1]
        Ar = a.sum() / 2
        cx = ((x[:-1] + x[1:]) * a).sum() / (6 * Ar); cy = ((y[:-1] + y[1:]) * a).sum() / (6 * Ar)
        Ix = ((y[:-1] ** 2 + y[:-1] * y[1:] + y[1:] ** 2) * a).sum() / 12
        Iy = ((x[:-1] ** 2 + x[:-1] * x[1:] + x[1:] ** 2) * a).sum() / 12
        return Ar, Ix, Iy
    ao, ixo, iyo = I(Po); ai, ixi, iyi = I(Pi)
    Am = 0.5 * (ao + ai)  # mid-wall enclosed area
    per = Po.exterior.length * 0.5 + Pi.exterior.length * 0.5
    J = 4 * Am ** 2 / (per / t)
    return dict(area=ao - ai, I_N=ixo - ixi, I_U=iyo - iyi, ymax=B[0], Am=Am, J=J)  # I_N: bending about N (vertical loads)


# --- loads ---------------------------------------------------------------------------------------------
W1 = 5 * g; W2 = 15 * g
P_load = np.array(man["shelf"]["load_point_LC1"])
under = to_trimesh(to_manifold(trimesh.load(os.path.join(OUT, "underlay.stl"))))
skin = trimesh.load(os.path.join(OUT, "skin.stl"))
mu = under.volume * RHO_KG_MM3 * g           # N (solid density)
ms = skin.volume * RHO_KG_MM3 * g * 0.8      # skin counted at 80 % (0.6 mm bond overlap is inside underlay)
print("weights N: underlay %.1f skin %.1f (LC1 plant %.1f)" % (mu, ms, W1))


def outboard(mesh, s):
    T, N, U = sp.frame(np.array([s])); o = sp.point(np.array([s]))[0]
    m = to_manifold(mesh)
    part = m.trim_by_plane(tuple(T[0]), float(np.dot(T[0], o)))
    tm = to_trimesh(part)
    return tm.volume, tm.center_mass


stations = [0, 40, 80, 120, 151, 200, 250, 302, 340, 380, 420]
rows = []
for s in stations:
    T, N, U = sp.frame(np.array([s])); T, N, U = T[0], N[0], U[0]
    o = sp.point(np.array([s]))[0]
    vu, cu = outboard(under, s) if s > 0 else (under.volume, under.center_mass)
    vs, cs = outboard(skin, s) if s > 0 else (skin.volume, skin.center_mass)
    Fsw = [(vu * RHO_KG_MM3 * g, cu), (vs * RHO_KG_MM3 * g * 0.8, cs)]
    Pr = props(s)
    out = {"s": s}
    for lc, W in (("LC1", W1), ("LC2", W2)):
        loads = Fsw + ([(W, P_load)] if (s < 360) else [])
        M = np.zeros(3)
        for w, pt in loads:
            M += np.cross(pt - o, np.array([0, 0, -w]))
        V = sum(w for w, _ in loads)
        MN, MT, MU = M @ N, M @ T, M @ U
        sig = abs(MN) * Pr["ymax"] / Pr["I_N"]  # bending about N (vertical loads); MU not carried by the shell-only vertical-load model
        tau = abs(MT) / (2 * Pr["Am"] * t)
        vm = np.sqrt(sig ** 2 + 3 * tau ** 2)
        out[lc] = dict(M_N_Nmm=float(MN), M_T_Nmm=float(MT), V_N=float(V), sigma=float(sig), tau=float(tau), vm=float(vm))
    out["props"] = {k: float(v) for k, v in Pr.items()}
    rows.append(out)

# tip deflection at shelf center under LC1 (unit-load, shell-only EI, GJ) ------------------------------------
ss = np.linspace(0, 360, 241)
o_all = sp.point(ss)
Tv, Nv, Uv = sp.frame(ss)
PP = [props(x) for x in ss]
d_bend = 0.0; d_tors = 0.0
# distributed self weight outboard of s approximated as point mass at centroid of outboard portion (per station)
# cheaper: use LC1 plant load only + self weight lumped (mass of span outboard of root at its centroid)
vu, cu = outboard(under, 0.01); vs, cs = outboard(skin, 0.01)
Wsw = [(vu * RHO_KG_MM3 * g, cu), (vs * RHO_KG_MM3 * g * 0.8, cs)]
for i in range(len(ss) - 1):
    mid = 0.5 * (ss[i] + ss[i + 1]); ds = ss[i + 1] - ss[i]
    o = sp.point(np.array([mid]))[0]
    T, N, U = [a[0] for a in sp.frame(np.array([mid]))]
    P = props(mid)
    M = np.cross(P_load - o, np.array([0, 0, -W1]))
    m_unit = np.cross(P_load - o, np.array([0, 0, -1.0]))
    # only plant load for deflection (self-weight deflection reported separately, below)
    d_bend += (M @ N) * (m_unit @ N) / (E * P["I_N"]) * ds
    d_tors += (M @ T) * (m_unit @ T) / (G * P["J"]) * ds
d_plant = d_bend + d_tors
# self-weight deflection at shelf point: each lump w at centroid c: moment arm to section
d_sw = 0.0
for w, c in Wsw:
    for i in range(len(ss) - 1):
        mid = 0.5 * (ss[i] + ss[i + 1]); ds = ss[i + 1] - ss[i]
        o = sp.point(np.array([mid]))[0]
        T, N, U = [a[0] for a in sp.frame(np.array([mid]))]
        P = props(mid)
        if np.dot(c - o, T) <= 0:
            continue
        M = np.cross(c - o, np.array([0, 0, -w])); m_unit = np.cross(P_load - o, np.array([0, 0, -1.0]))
        d_sw += (M @ N) * (m_unit @ N) / (E * P["I_N"]) * ds + (M @ T) * (m_unit @ T) / (G * P["J"]) * ds
k = W1 / d_plant if d_plant else np.inf    # N/mm at shelf (shell-only)
m_plant = 5.0 * 1e-3; m_span = (mu + ms) / g * 1e-3  # t
f_with = np.sqrt(k / (m_plant + 0.24 * m_span)) / (2 * np.pi)
f_without = np.sqrt(k / (0.24 * m_span)) / (2 * np.pi)

# anchor screws (UNDER REVISION; Verification region owns LC5) -------------------------------------------
# Tension from the moment about the plate Y axis only (pull-out of the top screws, plate pivoting about a bottom line).
# Mx (torque about X = wall normal, from the plant's lateral offset) is an in-plane torque on the plate: screws carry it in
# SHEAR (r x F about the pattern centroid), never in axial tension.
holes = np.array(man["anchor"]["holes_yz"])
def screw_loads(extra_W, pivot_z):
    loads = [(mu, under.center_mass), (ms, skin.center_mass), (extra_W, P_load)]
    M = np.zeros(3); V = 0
    for w, pt in loads:
        M += np.cross(pt, np.array([0, 0, -w])); V += w
    My, Mx = M[1], M[0]
    arm = holes[:, 1] - pivot_z
    T_i = np.maximum(My * arm / np.sum(arm ** 2), 0)          # linear strain about pivot line; tension-only (My only)
    r = np.linalg.norm(holes, axis=1)
    shear = np.hypot(V / 4, 0) * np.ones(4)                  # direct vertical share V/4 ...
    tors = abs(Mx) / np.sum(r ** 2) * r                        # ... plus torsion share Mx*r_i/sum(r^2), directions combined worst-case
    worst_shear = float((shear + tors).max())
    return dict(Mx_Nmm=float(Mx), My_Nmm=float(My), V_N=float(V), pivot_z=pivot_z, T_each_N=T_i.round(1).tolist(),
                T_peak=float(T_i.max()), shear_direct_N=float(V / 4), shear_worst_screw_N=worst_shear)
ph = float(np.min(holes[:, 1]))
anchor = {"LC1": {"pivot_plate_edge": screw_loads(W1, -p["anchor_plate"]["size"][1] / 2), "pivot_bottom_screws": screw_loads(W1, ph)},
          "LC2": {"pivot_plate_edge": screw_loads(W2, -p["anchor_plate"]["size"][1] / 2), "pivot_bottom_screws": screw_loads(W2, ph)}}

# --- write ---------------------------------------------------------------------------------------------
L = []
L.append("# analytic_geometry_prelim — Geometry region hand calcs (PRELIMINARY, shell-only)\n")
L.append("Scope: plausibility of default params before FEA. Shell-only section (ribs/plugs neglected = conservative), "
         "thin-wall Bredt torsion, unit-load deflection, E/rho/allowables from params.json materials. Skin counted at 80 % solid. "
         "NOT the Verification analytic report. Owner: geometry-manager. [PROVISIONAL: unsigned]\n")
L.append(f"Weights: underlay {mu:.1f} N ({mu/g:.2f} kg), skin {ms:.1f} N ({ms/g:.2f} kg eff.). LC1 plant {W1:.1f} N at shelf center "
         f"({P_load[0]:.0f},{P_load[1]:.0f},{P_load[2]:.0f}).\n")
L.append("## Section stress along span (LC1 5 kg, LC2 15 kg), von Mises = sqrt(sigma^2+3 tau^2), MPa\n")
L.append("| s | I_N mm4 | M_N (LC1) N.m | M_T (LC1) N.m | vm LC1 | vm LC2 | allow LC1 (18/3) | allow LC2 (18/1.5) | min SF LC1 | min SF LC2 |")
L.append("|---|---|---|---|---|---|---|---|---|---|")
worst1 = worst2 = 1e9
for r in rows:
    sf1 = SIG_Z / max(r["LC1"]["vm"], 1e-9); sf2 = SIG_Z / max(r["LC2"]["vm"], 1e-9)
    worst1 = min(worst1, sf1); worst2 = min(worst2, sf2)
    L.append(f"| {r['s']} | {r['props']['I_N']:.3g} | {r['LC1']['M_N_Nmm']/1e3:.1f} | {r['LC1']['M_T_Nmm']/1e3:.1f} | "
             f"{r['LC1']['vm']:.2f} | {r['LC2']['vm']:.2f} | 6.0 | 12.0 | {sf1:.1f} | {sf2:.1f} |")
L.append(f"\nWorst section SF (interlayer allowable 18 MPa, no stress concentration): LC1 {worst1:.1f} (need >=3), LC2 {worst2:.1f} (need >=1.5).\n")
L.append("## Tip/shelf deflection and frequency (LC1, shell-only EI/GJ)\n")
L.append(f"- Shelf-point deflection from plant 5 kg: {d_plant:.2f} mm (bending {d_bend:.2f}, torsion {d_tors:.2f}); self-weight {d_sw:.2f} mm; "
         f"total {d_plant + d_sw:.2f} mm (limit 6).")
L.append(f"- Stiffness at shelf k = {k:.1f} N/mm. f1 (Rayleigh, m_eff = plant + 0.24 m_span) = {f_with:.1f} Hz; without plant {f_without:.1f} Hz (limit 8).\n")
L.append("## Anchor plate screws (4x d6 holes, 120x70) - UNDER REVISION, numbers only, NO verdict\n")
L.append("Method: tension from My only (top-screw pull-out about a bottom pivot line; two pivot assumptions). Mx (torque about the wall normal) "
         "is carried in shear (V/4 + torsion share), not tension. The Verification region owns the corrected LC5 numbers and verdict; "
         "treat everything below as a hand-calc input, not a conclusion.\n")
for lc in ("LC1", "LC2"):
    for k, v in anchor[lc].items():
        L.append(f"- {lc}, {k}: M_y {v['My_Nmm']/1e3:.1f} N.m, M_x {v['Mx_Nmm']/1e3:.1f} N.m, V {v['V_N']:.0f} N; peak screw tension {v['T_peak']:.0f} N; "
                 f"worst-screw shear (direct + torsion) {v['shear_worst_screw_N']:.0f} N.")
L.append("- Pattern issue (geometry fact): 120 mm horizontal screw spacing cannot land in one 38 mm stud face; at 406 mm stud spacing at most one column of two screws is in a stud. "
         "Options for Verification/Fabrication: blocking/anchors for all 4, or a wider French cleat.\n")
L.append("## Other plausibility notes\n")
L.append("- Shell local buckling (thin cylinder, classical 0.6 E t/r, r~40, t=2.4): ~72 MPa, knockdown 0.2 -> 14 MPa >> applied (<3 MPa). OK.")
L.append("- Shelf deck: 124 mm wide top, webs at n=0,+-32, rings at 30 mm -> panel ~32x30x2.4: plate bending under 15 kg < 1 MPa. OK.")
L.append("- Peak moment at the root/neck (s~0-60); joint cuts (s=151, 302) see lower M. Joint section = shell + 8/16 mm solid plug; "
         "bolt/pin/key stresses are Verification's.")
_md = os.path.join(_a.report_dir, "analytic_geometry_prelim.md")
_log = "\n\n---\n*Edit log*\n\n| Date | Agent | Change | Signed-off-by |\n|------|-------|--------|---------------|\n| 2026-11-15 | geometry-manager | Initial hand calcs | [PROVISIONAL] |\n"
if os.path.exists(_md):           # never clobber an existing edit log (sign-offs live there)
    _old = open(_md).read()
    if "\n---\n*Edit log*" in _old:
        _log = "\n" + _old[_old.index("\n---\n*Edit log*"):]
os.makedirs(_a.report_dir, exist_ok=True)
open(_md, "w").write("\n".join(L) + _log)
json.dump(dict(rows=rows, d_plant=d_plant, d_sw=d_sw, k=k, f_with=f_with, f_without=f_without, anchor_under_revision=anchor,
               material=p["material"], worst_SF_LC1=worst1, worst_SF_LC2=worst2),
          open(os.path.join(_a.report_dir, "analytic_geometry_prelim.json"), "w"), indent=1)
print("\n".join(L))
