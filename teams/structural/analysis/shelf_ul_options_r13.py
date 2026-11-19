#!/usr/bin/env python3
"""UL shelf-arm options (shelf-arms-r13.md s.9): bent rod/tube along the centreline, max plant mass, plate moved in, hidden prop. Imports shelf_arms_r13 constants/helpers,
same criteria. python3 -I shelf_ul_options_r13.py -> shelf_ul_options_r13.json"""
import os, sys, json, numpy as np
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import shelf_arms_r13 as S
from shelf_arms_r13 import *
STEEL = {'rod10': (10, 0), 'rod12': (12, 0), 'rod16': (16, 0), 'tube16x1.5': (16, 1.5), 'tube20x2': (20, 2.0)}
def sect(D, t):
    if t == 0: return np.pi / 64 * D ** 4, np.pi / 4 * D ** 2, np.pi / 32 * D ** 3
    d = D - 2 * t; return np.pi / 64 * (D ** 4 - d ** 4), np.pi / 4 * (D ** 2 - d ** 2), np.pi / 32 * (D ** 4 - d ** 4) / D   # I, A, Z(bending)
def curvature_min(c, k):
    c = np.asarray(c)[:k + 1]; R = []
    for i in range(1, len(c) - 1):
        a, b = c[i] - c[i - 1], c[i + 1] - c[i]; ang = np.arccos(np.clip(a @ b / np.linalg.norm(a) / np.linalg.norm(b), -1, 1)); R.append(0.5 * (np.linalg.norm(a) + np.linalg.norm(b)) / max(ang, 1e-6))
    return float(min(R)) if R else None

def setup(v):
    meta = json.load(open(B + f'{v}_meta.json')); solid = np.load(B + f'{v}_solid.npy'); X0 = meta['X0']; L = [l for l in meta['limbs'] if l['name'] == 'S1_UL'][0]; pl = [p for p in meta['plates'] if p['limb'] == 'S1_UL'][0]
    sd, cd, rd, t = dense(L['c'], L['r']); n = len(sd); root = cd[0]; hz = lambda p: float(np.hypot(p[0] - root[0], p[2] - root[2]))
    jt = int(round((pl['top'] - X0) / RES)); i0 = max(int((pl['cx'] - pl['a'] * 1.5 - X0) // RES), 0); i1 = min(int((pl['cx'] + pl['a'] * 1.5 - X0) // RES), solid.shape[0]); k_hi = int((pl['cz'] + pl['b'] * 1.5 + 8) // RES)
    plan = np.asarray(solid[i0:i1, jt - 1, :k_hi]); ii = np.argwhere(plan); px = X0 + RES * (ii[:, 0] + i0); pz = Z0 + RES * ii[:, 1]; kf = int(np.hypot(px - root[0], pz - root[2]).argmax())
    far = np.array([px[kf], pl['top'], pz[kf]]); u_h = np.array([far[0] - root[0], 0, far[2] - root[2]]); u_h /= np.linalg.norm(u_h)
    capv = int(S.gap[v]['gaps']['S1_UL']['plate_thickness_max_mm'] // RES); run_ = np.asarray(solid[i0:i1, jt - capv:jt, :k_hi])[:, ::-1, :]; depth = np.where(plan, np.logical_and.accumulate(run_, axis=1).sum(1), 0)
    V_plate = float(depth.sum() * RES ** 3); pc = np.array([pl['centroid_x'], pl['top'], pl['centroid_z']]); pt = far - INSET * u_h
    i_entry = int(np.argmin(np.hypot(cd[:, 0] - pl['entry'][0], cd[:, 2] - pl['entry'][1]))); i_L = int(np.argmin(np.hypot(cd[:, 0] - pt[0], cd[:, 2] - pt[2])))
    lo = np.floor((cd.min(0) - 70 - [X0, X0, Z0]) / RES).astype(int).clip(0); hi = np.minimum(np.ceil((cd.max(0) + 70 - [X0, X0, Z0]) / RES).astype(int), solid.shape)
    edt = ndi.distance_transform_edt(solid[lo[0]:hi[0], lo[1]:hi[1], lo[2]:hi[2]]) * RES; e_c = ndi.map_coordinates(edt, ((cd - [X0, X0, Z0]) / RES - lo).T, order=1, mode='nearest')
    sf = solid.astype(np.float32); I_circ0 = np.pi * rd ** 4 / 4; I_core = I_circ0.copy()
    for k in range(0, i_entry + 1):
        sc_ = section(sf, X0, cd[k], t[k], rd[k] + 8, disc=rd[k] + 1.0)
        if sc_: I_core[k] = min(I_circ0[k], sc_['Ia'], sc_['Ib'])
    I_circ = np.minimum(I_circ0, I_core); I_shell = np.pi / 4 * (rd ** 4 - np.maximum(rd - T_RING, 0) ** 4) * (I_circ / I_circ0)
    I_plate = np.full(n, 3.7e5 if v == 'H13' else 4.0e5)   # plate-zone ring min from shelf_arms_r13.json limb_core.I_plate_ring_min (UL)
    return dict(v=v, meta=meta, L=L, sd=sd, cd=cd, rd=rd, t=t, n=n, hz=hz, pt=pt, pc=pc, u_h=u_h, V_plate=V_plate, i_entry=i_entry, i_L=i_L, e_c=e_c, I_circ=I_circ, I_shell=I_shell, I_plate=I_plate, L_bound=hz(pt), L_nom=hz(pc))

def make(Sx, member, delta=0.0, plate_ret=RET):
    """member: ('print_shell'|'print_solid'|(rod key)); returns evaluator f(m_kg, case) -> dict"""
    cd, rd, t, n, sd, i_entry = Sx['cd'], Sx['rd'], Sx['t'], Sx['n'], Sx['sd'], Sx['i_entry']; u_h = Sx['u_h']; pt = Sx['pt'] - delta * u_h; pc = Sx['pc'] - delta * u_h
    i_L = int(np.argmin(np.hypot(cd[:, 0] - pt[0], cd[:, 2] - pt[2]))); L_b = Sx['hz'](pt); lim = L_b / SAG_DIV
    w_limb = np.pi * rd ** 2 * RHO_P * RET * 4.0; w_limb[min(i_entry, i_L + 1):] = 0.0; W_plate = Sx['V_plate'] * RHO_P * plate_ret
    cov = np.array([], int); rod = None; EI = np.zeros(n); GJ = np.zeros(n)
    I_pr = np.where(np.arange(n) < i_entry, Sx['I_circ'] if member == 'print_solid' else Sx['I_shell'], np.maximum(Sx['I_plate'], 1.0))
    EI = E_LT * I_pr; GJ = E_LT / (2 * (1 + NU_P)) * 2 * I_pr
    wr = []; ok_fit = True; info = {}
    if member in STEEL:
        D, tw = STEEL[member]; I, A, Z = sect(D, tw); rr = D / 2 + 0.2; good = (Sx['e_c'] - rr) >= COVER_FLOOR; k_end = int(np.argmin(good)) - 1 if not good.all() else n - 1
        k_end = min(k_end, i_L)
        if k_end < 1: ok_fit = False
        else:
            cov = np.arange(0, k_end + 1); EI[cov] = E_S * I; GJ[cov] = G_S * 2 * I; wr = [(int(i), RHO_S * A * 4.0) for i in cov]; rod = (D, tw, I, Z)
            info = dict(rod_end_s_mm=float(sd[k_end]), rod_end_vs_entry_mm=float(sd[k_end] - sd[i_entry]), min_cover_mm=round(float((Sx['e_c'][:k_end + 1] - rr).min()), 1), min_limb_d_over_rod_span_mm=round(float(2 * Sx['rd'][:k_end + 1].min()), 1), rod_weight_N=round(float(sum(w for _, w in wr)), 2), min_bend_R_mm=curvature_min(Sx['L']['c'], int(k_end / 3)), k_end=k_end)
    covset = set(cov.tolist())
    def f(m_kg, extra=None, R_prop=0.0):
        Wp = m_kg * G; res = {}
        def forces(vert, horiz):
            F = [(i, cd[i], np.array([0, -w_limb[i], 0])) for i in range(min(i_entry, i_L + 1))]; F.append((None, pc, np.array([0, -W_plate, 0])))
            F += [(i, cd[i], np.array([0, -w, 0])) for i, w in wr if i <= i_L]
            F.append((None, pt, np.array([0, -vert, 0])))
            if horiz: F.append((None, pt, horiz * np.array([-u_h[2], 0, u_h[0]])))
            if R_prop: F.append((None, pt, np.array([0, R_prop, 0])))
            return F
        unit = moments(cd, i_L, [(None, pt, np.array([0, -1.0, 0]))]); Mu = unit
        def split(M): Mt = (M * t[:len(M)]).sum(1); Mp = np.linalg.norm(M - Mt[:, None] * t[:len(M)], axis=1); return Mp, Mt
        mp_u, mt_u = split(Mu)
        def defl(M): Mp, Mt = split(M); return float((Mp * mp_u / EI[:len(M)] * 4.0).sum() + (Mt * mt_u / GJ[:len(M)] * 4.0).sum())
        Ms = moments(cd, i_L, forces(Wp, 0)); Mv = moments(cd, i_L, forces(Wp + BUMP_V, 0)); Mh = moments(cd, i_L, forces(Wp, BUMP_H))
        def ratios(M, allow):
            Mp, Mt = split(M); out = 0.0
            for i in range(len(M)):
                if i in covset: D, tw, I, Z = rod; sg = Mp[i] / Z; tu = Mt[i] * (D / 2) / (2 * I); out = max(out, np.sqrt(sg ** 2 + 3 * tu ** 2) / (DC_ROD * FY))
                elif i <= i_entry:
                    Ii = I_pr[i]; r = rd[i]; sg = Mp[i] * r / Ii; tu = Mt[i] * r / (2 * Ii); out = max(out, np.sqrt(sg ** 2 + 3 * tu ** 2) / allow)
            return out
        d = defl(Ms); marg = 1.0 if (member in STEEL) else MARGIN_PRINTED
        return dict(sag=d, limit=lim, sag_ratio=d * marg / lim, sus_ratio=ratios(Ms, SIG_SUS) if member not in STEEL else ratios(Ms, SIG_SUS), bump_ratio=max(ratios(Mv, SIG_TRN), ratios(Mh, SIG_TRN)), unit_flex=float(defl(Mu)), L=L_b, Mroot=float(np.linalg.norm(Mv[0])) / 1e3)
    return f, ok_fit, info

def worst(r): return max(r['sag_ratio'], r['sus_ratio'], r['bump_ratio'])
def mmax(f):
    if worst(f(0.0)) > 1: return 0.0
    lo, hi = 0.0, 12.0
    if worst(f(hi)) <= 1: return hi
    for _ in range(30):
        mid = (lo + hi) / 2
        if worst(f(mid)) <= 1: lo = mid
        else: hi = mid
    return round(lo, 2)

out = {}
for v in ('H13', 'E1'):
    Sx = setup(v); o = dict(L_bound=round(Sx['L_bound'], 1), L_nom=round(Sx['L_nom'], 1), r_root_entry=[round(float(Sx['rd'][0]), 1), round(float(Sx['rd'][Sx['i_entry']]), 1)], s_entry=float(Sx['sd'][Sx['i_entry']]),
                            min_limb_inscribed_d_to_entry_mm=round(float(2 * Sx['e_c'][:Sx['i_entry'] + 1].min()), 1), min_r_meta_d_to_entry_mm=round(float(2 * Sx['rd'][:Sx['i_entry'] + 1].min()), 1), options={})
    # (a) bent rod / tube design check at 5 kg
    for key in ['print_shell', 'print_solid'] + list(STEEL):
        f, ok, info = make(Sx, key)
        if not ok: o['options'][key] = dict(fits=False, why='cover floor 3 mm violated at the root station'); continue
        r5 = f(5.0); o['options'][key] = dict(fits=True, **info, sag_5kg_mm=round(r5['sag'], 2), limit_mm=round(r5['limit'], 2), sag_ratio_5kg=round(r5['sag_ratio'], 2), sus_ratio=round(r5['sus_ratio'], 2), bump_ratio=round(r5['bump_ratio'], 2), pass_5kg=bool(worst(r5) <= 1),
                                              sag_self_only_mm=round(f(0.0)['sag'], 2), m_max_kg=mmax(f), pass_1p5kg=bool(worst(f(1.5)) <= 1), pass_1kg=bool(worst(f(1.0)) <= 1), worst_1p5kg=round(worst(f(1.5)), 2), root_M_lean_5kg_Nm=round(r5['Mroot'], 1))
    # (c1) plate moved inward: max inward shift delta for which 5 kg passes (limb profile unchanged, plate rigid)
    c1 = {}
    for key in ['print_shell', 'print_solid', 'rod10', 'rod12', 'rod16']:
        best = None
        for dl in range(0, 301, 10):
            f, ok, _ = make(Sx, key, delta=float(dl))
            if not ok: break
            if worst(f(5.0)) <= 1: best = dl; break
        c1[key] = dict(min_inward_shift_mm=best, L_bound_after_mm=round(Sx['L_bound'] - best, 0) if best is not None else None)
    o['c1_plate_moved_inward_5kg'] = c1
    # (c2) hidden prop (plate underside to wall, 45 deg, rp2 strut: PETG 24x3 tube E_lt 640, L 450 mm) on the as-built hollow and solid limb, 5 kg
    c2 = {}
    kv = E_LT * np.pi * (12 ** 2 - 9 ** 2) / 450.0 * 0.5   # vertical stiffness N/mm of a 45 deg strut
    for key in ['print_shell', 'print_solid']:
        f, ok, _ = make(Sx, key); r0 = f(5.0); R = r0['sag'] / (r0['unit_flex'] + 1 / kv); f2 = make(Sx, key)[0]; r1 = f2(5.0, R_prop=R)
        c2[key] = dict(prop_reaction_N=round(R, 1), strut_axial_N=round(R * np.sqrt(2), 1), strut_axial_limit_N=260, sag_with_prop_mm=round(r1['sag'], 2), limit_mm=round(r1['limit'], 2), sus_ratio=round(r1['sus_ratio'], 2), bump_ratio_no_prop_relief=round(r0['bump_ratio'], 2), bump_ratio_prop_at_sustained_R=round(r1['bump_ratio'], 2), pass_sag=bool(r1['sag_ratio'] <= 1))
    o['c2_hidden_prop_5kg'] = c2; o['c2_prop_vertical_stiffness_N_per_mm'] = round(float(kv), 1)
    out[v] = o
json.dump(out, open(os.path.join(HERE, 'shelf_ul_options_r13.json'), 'w'), indent=1)
for v, o in out.items():
    print(v, {k: o[k] for k in ('L_bound', 'r_root_entry', 's_entry', 'min_limb_inscribed_d_to_entry_mm', 'min_r_meta_d_to_entry_mm')})
    for k, x in o['options'].items(): print('  ', k, x)
    print('  c1', o['c1_plate_moved_inward_5kg']); print('  c2', o['c2_hidden_prop_5kg'])
