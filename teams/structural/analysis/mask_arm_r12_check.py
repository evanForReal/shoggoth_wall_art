#!/usr/bin/env python3
"""Structural r12 mask-arm spot-check (mask-arm-v1.md s.10). Reads CAD's composition_r12 build/*.npy + *_meta.json (build/ is gitignored; run ./run_all.sh build there first).
Method = s.9.2: design mask 0.8 kg = 7.85 N, 40 N bump at the farthest mask voxel from the rod exit, torsion 40 N x max(125 mm, farthest mask voxel from rod axis),
rod 10 mm steel EI 9.82e7 N.mm^2, droop at mask edge (CoM + 100 mm x rotation), cantilever fixed 20 mm inside the block face. Arm free-span weight = voxel volume beyond exit x 1.27 g/cm3 (100% solid, conservative).
python3 -I mask_arm_r12_check.py -> mask_arm_r12_check.json"""
import sys, os, json, numpy as np
CAD = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'cad', 'composition_r12'); sys.path.insert(0, CAD)
from engine import XS, YS, ZS, RES
import heldmask as hm
B = os.path.join(CAD, 'build') + '/'; RHO = 1.27e-3; EI = 2e5 * np.pi * 10 ** 4 / 64; WM = 7.85; out = {}
for sid in ['C1', 'C2', 'C3', 'C4', 'C6', 'C8', 'C9', 'C10']:
    m = json.load(open(B + sid + '_meta.json')); g = m['held_geo']; A = np.array(g['A']); d = np.array(g['d']); Rx = np.array(g['Rx'])
    maskp = np.load(B + sid + '_maskpart.npy'); armp = np.load(B + sid + '_armpart.npy'); solid = np.load(B + sid + '_solid.npy')
    mi = np.argwhere(maskp); P = np.stack([XS[mi[:, 0]], YS[mi[:, 1]], ZS[mi[:, 2]]], 1); com = P.mean(0); rel = P - Rx; far3 = np.linalg.norm(rel, axis=1); iF = far3.argmax()
    pa = P - A; perp = np.linalg.norm(pa - (pa @ d)[:, None] * d, axis=1)
    ai = np.argwhere(armp); Q = np.stack([XS[ai[:, 0]], YS[ai[:, 1]], ZS[ai[:, 2]]], 1); sA = (Q - A) @ d; sel = sA > g['s_exit']
    Wa = sel.sum() * RES ** 3 * RHO * 9.81e-3; cga = Q[sel].mean(0); la = np.hypot(cga[0] - Rx[0], cga[2] - Rx[2]); Lh = np.hypot(com[0] - Rx[0], com[2] - Rx[2])
    M = WM * Lh + Wa * la + 40 * far3[iF]; Tq = 40 * max(125.0, perp.max())          # N.mm
    sig = 32 * M / (np.pi * 1000); tau = 16 * Tq / (np.pi * 1000); vm = np.sqrt(sig ** 2 + 3 * tau ** 2)
    perpg = np.sqrt(1 - d[1] ** 2); L = (com - Rx) @ d + 20; Wp = (WM + Wa) * perpg; dc = Wp * L ** 3 / (3 * EI); th = Wp * L ** 2 / (2 * EI)
    Mw = WM * com[2] + Wa * cga[2] + 40 * P[:, 2].max(); ps = Mw / 75 / 2
    Rm = hm.rotmat(*[np.radians(m['held_in'].get(k, 0)) for k in ('yaw', 'pitch', 'roll')]); en = Rm[:, 2]; nd = float(d @ en); obl = float(np.degrees(np.arccos(nd)))
    k0 = int(round((2 - ZS[0]) / RES)); k6 = int(round((6 - ZS[0]) / RES)) + 1; Xg, Yg = np.meshgrid(XS, YS, indexing='ij'); pm = (abs(Xg - A[0]) <= 50) & (abs(Yg - A[1]) <= 50)
    a = np.array([1.0, 0, 0]) if abs(d[0]) < 0.9 else np.array([0, 1.0, 0]); u = np.cross(d, a); u /= np.linalg.norm(u); v = np.cross(d, u)
    G = {k: (np.array(x) if isinstance(x, list) else x) for k, x in g.items()}; G['H'] = m['held_in']; hole = None
    if m['held_in'].get('grip') == 'E':
        uu, vv, ww = hm.loc(G, P[:, 0], P[:, 1], P[:, 2]); s_, rad, _, _ = hm.axc(G, P[:, 0], P[:, 1], P[:, 2]); pad = (rad <= hm.PAD_R + 1) & (s_ > g['s_T'] + 4) & (s_ < g['s_plane'] + 14)
        D = 2 * G['R']; cu, cv, a_, b_ = hm.EYE_HOLE['eu'] * D, hm.EYE_HOLE['ev'] * D, hm.EYE_HOLE['a'] * D / 2, hm.EYE_HOLE['b'] * D / 2; t = np.linspace(0, 2 * np.pi, 720); hb = np.stack([cu + a_ * np.cos(t), cv + b_ * np.sin(t)], 1); pp = np.stack([uu[pad], vv[pad]], 1)
        hole = float(np.sqrt(((pp[:, None, :] - hb[None, ::6, :]) ** 2).sum(-1)).min(1).min())
    out[sid] = dict(CoM=com.round(1).tolist(), lever_h_mm=round(Lh, 1), farthest_from_exit_mm=round(float(far3[iF]), 1), farthest_from_axis_mm=round(float(perp.max()), 1), arm_free_span_N=round(Wa, 2), M_total_Nm=round(M / 1e3, 2), T_bump_Nm=round(Tq / 1e3, 2),
                    sigma_MPa=round(sig, 0), tau_MPa=round(tau, 1), vonMises_MPa=round(vm, 0), DC_vs_300=round(vm / 300, 2), droop_CoM_mm=round(dc, 2), droop_edge_mm=round(dc + th * 100, 2), M_wall_Nm=round(Mw / 1e3, 1), per_upper_screw_N=round(ps, 0), DC_screw_350=round(ps / 350, 2),
                    mask_z_max=float(P[:, 2].max()), mask_normal_tilt_deg=round(float(np.degrees(np.arccos(en[2]))), 1), rod_to_mask_normal_deg=round(obl, 1), pad_depth_r20_near_mm=round(38 - 20 * np.tan(np.radians(obl)), 1), pad_depth_r35_near_mm=round(38 - 35 * np.tan(np.radians(obl)), 1),
                    plate_100x100_z2_6_fraction=round(float(solid[:, :, k0:k6][pm].mean()), 3), A_xyz=A.round(0).tolist(), armpart_xyz_extent_mm=(np.ptp(Q, 0) + RES).round(0).tolist(), armpart_rodframe_extent_mm=[round(float(np.ptp(sA) + RES)), round(float(np.ptp(Q @ u) + RES)), round(float(np.ptp(Q @ v) + RES))], rod_length_mm=round(float(g['s_rod']), 1), eye_hole_to_pad_min_mm=hole)
    print(sid, out[sid])
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mask_arm_r12_check.json'), 'w'), indent=1)
