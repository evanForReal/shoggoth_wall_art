#!/usr/bin/env python3
"""Structural r13 shelf-arm reach check (shelf-arms-r13.md). Reads CAD composition_r13 build/{H13,E1}_{meta.json,solid.npy} (build/ is gitignored; run CAD ./run_all.sh first)
and gap_reach.json (plate thickness caps). Units N, mm, MPa. Method: 3D polyline beam along each shelf limb centreline (meta 'c','r'), vertical plant load at the plate,
self-weight lumped, unit-load deflection with bending + torsion, steel-rod and printed-section options, wall-anchor couple. python3 -I shelf_arms_r13.py -> shelf_arms_r13.json"""
import os, sys, json, numpy as np
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.abspath(__file__)); CAD = os.path.join(HERE, '..', '..', 'cad', 'composition_r13'); B = os.path.join(CAD, 'build') + '/'
RES = 2.0; Z0 = -8.0
# ---- assumptions (A-numbers continue rp2-strut-limb-voids.md A1-A12; see shelf-arms-r13.md s.2)
G = 9.81; W_PLANT = 5.0 * G; K_FACT = 1.5; W_FACT = K_FACT * W_PLANT          # 49.05 N sustained, 73.6 N factored (DECISIONS 2026-11-15)
BUMP_V = 40.0; BUMP_H = 40.0                                                    # A13 lean/bump at the pot, service, no factor (same 40 N as mask-arm-v1 s.1.2)
INSET = 50.0                                                                   # A14 pot CG 50 mm inside the farthest flat-top point (min pot dia 100, CAD proxy pots 100-140)
E_LT, E_LT40, E_S, NU_P, G_S = 640.0, 400.0, 200000.0, 0.38, 77000.0          # A3/A4 [GENERAL]; steel 200 GPa
SIG_SUS, SIG_TRN, FY, DC_ROD = 7.0, 22.0, 300.0, 0.7                           # A5, mask-arm s.1.5
RHO_P = 1.27e-6 * G; RHO_S = 7.85e-6 * G; RET = 0.42; T_RING = 3.0              # N/mm^3; A12 high retention 0.42; shell-only credit 3.0 mm (rp2 s.3.3 hollow wall floor)
MARGIN_PRINTED = 1.33                                                          # A15 printed-only options need sag <= limit/1.33 (E_lt, creep unmeasured [GENERAL]); steel options 1.0
SAG_DIV = 50.0                                                                 # A9: long-term rim sag <= L/50
COVER, COVER_FLOOR, ZMIN_ROD = 5.0, 3.0, 8.0                                   # mask-arm S2 cover; rod axis above the 6 mm back plate (z >= 8 + r)
S_ROWS = (75.0, 100.0); A_STUD = 406.0; SCREW_T, SCREW_V = 530.0, 350.0; SCULPT_SHEAR = 28.0   # S10 row s=75; rp2 A11; rp2 s.4.2 (14 kg cap, per screw)
RODS = (10, 12, 16, 20, 25)
if not os.path.exists(B + 'H13_solid.npy'): sys.exit('CAD build missing: run teams/cad/composition_r13/run_all.sh')
gap = json.load(open(os.path.join(CAD, 'gap_reach.json')))


def dense(c, r, step=4.0):
    c = np.asarray(c); r = np.asarray(r); s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(c, axis=0), axis=1))]; sd = np.arange(0, s[-1] + 1e-6, step)
    cd = np.stack([np.interp(sd, s, c[:, i]) for i in range(3)], 1); rd = np.interp(sd, s, r); t = np.gradient(cd, axis=0); t /= np.linalg.norm(t, axis=1)[:, None]
    return sd, cd, rd, t


def section(sf, X0, c, t, rcap, ring_px=2, disc=None):
    a = np.cross([0, 1, 0], t); a /= np.linalg.norm(a); b = np.cross(t, a); g = np.arange(-rcap, rcap + 0.1, 1.0); U, V = np.meshgrid(g, g, indexing='ij')
    P = c[None, None, :] + U[..., None] * a + V[..., None] * b; ijk = ((P - [X0, X0, Z0]) / RES).transpose(2, 0, 1)
    val = ndi.map_coordinates(sf, ijk, order=1, mode='constant', cval=0) > 0.5
    if disc is not None: val &= (U ** 2 + V ** 2 <= disc ** 2)
    lab, n = ndi.label(val); h = len(g) // 2; l0 = lab[h, h]
    if l0 == 0:
        if n == 0: return None
        ii = ndi.distance_transform_edt(lab == 0, return_indices=True)[1]; l0 = lab[ii[0][h, h], ii[1][h, h]]
    comp = lab == l0; A = int(comp.sum()); va = (V * comp).sum() / A; ua = (U * comp).sum() / A
    ring = comp & ~ndi.binary_erosion(comp, iterations=ring_px, border_value=1)
    touch = bool(comp[0, :].any() or comp[-1, :].any() or comp[:, 0].any() or comp[:, -1].any())
    return dict(A=A, Ia=float(((V - va) ** 2 * comp).sum()), Ib=float(((U - ua) ** 2 * comp).sum()), Ia_ring=float(((V - va) ** 2 * ring).sum()), Ib_ring=float(((U - ua) ** 2 * ring).sum()), touch=touch,
                ext_u=float(np.ptp(U[comp]) + 1), ext_v=float(np.ptp(V[comp]) + 1))


def moments(cd, i_last, forces):
    """M_i = sum (p - c_i) x F for forces (p, F) beyond station i; F purely given as vectors. forces: list of (idx_after or None, pos, vec)."""
    n = i_last + 1; M = np.zeros((n, 3))
    for i in range(n):
        for (j0, p, F) in forces:
            if j0 is not None and j0 <= i: continue
            M[i] += np.cross(np.asarray(p) - cd[i], F)
    return M


def run(v):
    meta = json.load(open(B + f'{v}_meta.json')); solid = np.load(B + f'{v}_solid.npy'); sf = solid.astype(np.float32); X0 = meta['X0']; out = {}
    for L in meta['limbs']:
        if not L['shelf']: continue
        nm = L['name']; pl = [p for p in meta['plates'] if p['limb'] == nm][0]; sd, cd, rd, t = dense(L['c'], L['r']); n = len(sd); root = cd[0]
        hz = lambda p: float(np.hypot(p[0] - root[0], p[2] - root[2]))
        # plate flat-top plane (y = top - 1 voxel), farthest voxel, volume of the contiguous run below the top (capped at CAD's measured max plate thickness)
        jt = int(round((pl['top'] - X0) / RES)); i0 = max(int((pl['cx'] - pl['a'] * 1.5 - X0) // RES), 0); i1 = min(int((pl['cx'] + pl['a'] * 1.5 - X0) // RES), solid.shape[0]); k_hi = int((pl['cz'] + pl['b'] * 1.5 + 8) // RES)
        plan = np.asarray(solid[i0:i1, jt - 1, :k_hi]).copy(); ii = np.argwhere(plan); px = X0 + RES * (ii[:, 0] + i0); pz = Z0 + RES * ii[:, 1]; dh = np.hypot(px - root[0], pz - root[2]); kf = int(dh.argmax())
        far = np.array([px[kf], pl['top'], pz[kf]]); u_h = np.array([far[0] - root[0], 0, far[2] - root[2]]); u_h /= np.linalg.norm(u_h)
        capv = int(gap[v]['gaps'][nm]['plate_thickness_max_mm'] // RES); run_ = np.asarray(solid[i0:i1, jt - capv:jt, :k_hi])[:, ::-1, :]; depth = np.logical_and.accumulate(run_, axis=1).sum(1); depth = np.where(plan, depth, 0)
        V_plate = float(depth.sum() * RES ** 3); pc = np.array([pl['centroid_x'], pl['top'], pl['centroid_z']])
        pt_bound = far - INSET * u_h; pt_nom = pc; L_rim = hz(far); L_bound = hz(pt_bound); L_nom = hz(pc)
        i_entry = int(np.argmin(np.hypot(cd[:, 0] - pl['entry'][0], cd[:, 2] - pl['entry'][1]))); i_L = int(np.argmin(np.hypot(cd[:, 0] - pt_bound[0], cd[:, 2] - pt_bound[2])))
        # sections: measured (voxel, merged-flag) vs circle of meta r; plate-zone shell-only (2 mm ring) credit
        sec_rows = []; ring_plate = {}
        for k in range(0, n, 8):
            rc = max(3 * rd[k] + 25, 45) if k < i_entry else 130.0
            s_ = section(sf, X0, cd[k], t[k], rc)
            if s_: sec_rows.append(dict(s=round(float(sd[k])), r_meta=round(float(rd[k]), 1), zone='limb' if k < i_entry else 'plate', A_meas=s_['A'], A_circ=round(float(np.pi * rd[k] ** 2)), Ia_meas=round(s_['Ia']), I_circ=round(float(np.pi * rd[k] ** 4 / 4)),
                                         Ia_ring=round(s_['Ia_ring']), merged=s_['touch'], ext_u=s_['ext_u'], ext_v=s_['ext_v']))
            if k >= i_entry and s_: ring_plate[k] = min(s_['Ia_ring'], s_['Ib_ring'])
        ks = sorted(ring_plate); I_plate_ring = np.array([ring_plate[min(ks, key=lambda q: abs(q - i))] if ks else 0.0 for i in range(n)])
        # limb-zone I per option. I_core = measured voxel section of the sweep itself (component through the centreline, clipped to a disc r_meta + 1 mm so webs/lumps outside the nominal sweep earn no credit, cuts into it do), about its own centroid
        I_circ0 = np.pi * rd ** 4 / 4; I_core = I_circ0.copy(); A_ratio = np.ones(n)
        for k in range(0, i_entry + 1):
            sc_ = section(sf, X0, cd[k], t[k], rd[k] + 8, disc=rd[k] + 1.0)
            if sc_: I_core[k] = min(I_circ0[k], sc_['Ia'], sc_['Ib']); A_ratio[k] = sc_['A'] / (np.pi * rd[k] ** 2)
        I_circ = np.minimum(I_circ0, I_core); I_shell = np.pi / 4 * (rd ** 4 - np.maximum(rd - T_RING, 0) ** 4) * (I_circ / I_circ0)
        # self-weight: limb zone solid * RET, plate lump
        dsl = np.r_[np.diff(sd), 0]; w_limb = np.pi * rd ** 2 * RHO_P * RET * 4.0; w_limb[i_entry:] = 0.0
        W_plate = V_plate * RHO_P * RET; W_limb = float(w_limb.sum())
        # EDT around the limb for rod clearance
        lo = np.floor((cd.min(0) - 70 - [X0, X0, Z0]) / RES).astype(int).clip(0); hi = np.minimum(np.ceil((cd.max(0) + 70 - [X0, X0, Z0]) / RES).astype(int), solid.shape)
        edt = ndi.distance_transform_edt(solid[lo[0]:hi[0], lo[1]:hi[1], lo[2]:hi[2]]) * RES
        def edt_at(P): return ndi.map_coordinates(edt, ((np.asarray(P) - [X0, X0, Z0]) / RES - lo).T, order=1, mode='nearest')

        def forces_for(case, rod_w=None):
            pt = pt_bound if case != 'nom' else pt_nom; F = []
            for i in range(i_entry):
                F.append((i, cd[i], np.array([0, -w_limb[i], 0])))
            F.append((None, pc, np.array([0, -W_plate, 0])))
            if rod_w is not None:
                for i, wr in rod_w: F.append((i, cd[i], np.array([0, -wr, 0])))
            if case in ('sus', 'nom'): F.append((None, pt, np.array([0, -W_PLANT, 0])))
            elif case == 'fact': F.append((None, pt, np.array([0, -W_FACT, 0])))
            elif case == 'bump_v': F.append((None, pt, np.array([0, -(W_PLANT + BUMP_V), 0])))
            elif case == 'bump_h':
                uperp = np.array([-u_h[2], 0, u_h[0]]); F.append((None, pt, np.array([0, -W_PLANT, 0]))); F.append((None, pt, BUMP_H * uperp))
            return F
        unit = [(None, pt_bound, np.array([0, -1.0, 0]))]; m_unit = moments(cd, i_L, unit)
        def split(M): Mt = (M * t[:len(M)]).sum(1); Mp = np.linalg.norm(M - Mt[:, None] * t[:len(M)], axis=1); return Mp, Mt
        mp_u, mt_u = split(m_unit)
        def deflect(M, EI, GJ): Mp, Mt = split(M); return float((Mp * mp_u / EI[:len(M)] * 4.0).sum() + (Mt * mt_u / GJ[:len(M)] * 4.0).sum())
        # option profiles
        def prof(opt, rod=None):
            I = np.where(np.arange(n) < i_entry, I_circ if opt == 'solid' else I_shell, np.maximum(I_plate_ring, 1.0)); Ee = np.full(n, E_LT); I = I.copy()
            if rod is not None:
                Ir = np.pi * rod['d'] ** 4 / 64; cov = rod['cov_idx']; EIr = E_S * Ir; EI = Ee * I; EI[cov] = EIr; GJ = Ee / (2 * (1 + NU_P)) * 2 * I; GJ[cov] = G_S * 2 * Ir; return EI, GJ
            return Ee * I, Ee / (2 * (1 + NU_P)) * 2 * I
        res = dict(plate=dict(limb=nm, plan_flat_top_voxels=int(plan.sum()), far_rim_pt=[round(float(q), 1) for q in far], bound_load_pt=[round(float(q), 1) for q in pt_bound], centroid_pt=[round(float(q), 1) for q in pc],
                              L_nom_mm=round(L_nom, 1), L_bound_mm=round(L_bound, 1), L_rim_mm=round(L_rim, 1), z_rim=round(float(far[2]), 1), V_plate_cm3=round(V_plate / 1e3, 1), W_plate_N_ret042=round(W_plate, 2), W_limb_N_ret042=round(W_limb, 2),
                              i_entry_s_mm=float(sd[i_entry]), s_load_mm=float(sd[i_L]), path_len_mm=round(float(sd[-1]), 1), root=[round(float(q), 1) for q in root], t_root=[round(float(q), 3) for q in t[0]]),
                   r_limb_root_entry_mm=[round(float(rd[0]), 1), round(float(rd[i_entry]), 1)], sections=sec_rows)
        # 0.5 L station per rp2 s.3.3 and I_req(L)
        w_arm = W_limb / max(sd[i_entry], 1)   # N/mm, limb-zone self-weight
        Ireq = lambda Lh: (W_PLANT * Lh ** 3 / 3 + w_arm * Lh ** 4 / 8) / (E_LT * Lh / SAG_DIV)
        i_half = int(np.argmin(np.abs(np.hypot(cd[:, 0] - root[0], cd[:, 2] - root[2]) - 0.5 * L_bound)))
        res['spec_rp2'] = dict(I_req_rp2_1p2e5_p300=124000, I_req_this_L_bound_mm4=round(float(Ireq(L_bound))), d_solid_req_mm=round(float((64 * Ireq(L_bound) / np.pi) ** 0.25), 1), I_circ_at_half_L=round(float(I_circ[i_half])), I_circ_root=round(float(I_circ[0])), I_circ_entry=round(float(I_circ[i_entry])),
                               d_root_mm=round(float(2 * rd[0]), 1), d_halfL_mm=round(float(2 * rd[i_half]), 1), d_entry_mm=round(float(2 * rd[i_entry]), 1), solid_d40_ok_to_entry=bool((2 * rd[:i_entry + 1] >= 40).all()), min_d_to_entry_mm=round(float(2 * rd[:i_entry + 1].min()), 1))
        # loads, no rod
        cases = ['sus', 'nom', 'fact', 'bump_v', 'bump_h']; Ms = {c: moments(cd, i_L, forces_for(c)) for c in cases}
        res['root_moment'] = {c: dict(M_vec_Nm=[round(float(q) / 1e3, 2) for q in Ms[c][0]], M_Nm=round(float(np.linalg.norm(Ms[c][0])) / 1e3, 2), Mp_Nm=round(float(split(Ms[c])[0][0]) / 1e3, 2), T_root_Nm=round(float(split(Ms[c])[1][0]) / 1e3, 2),
                                  V_N=round(float(sum(-f[2][1] for f in forces_for(c))), 1)) for c in cases}
        opts = {}
        for opt in ('shell', 'solid'):
            EI, GJ = prof(opt); d23 = deflect(Ms['sus'], EI, GJ); EI4 = EI * E_LT40 / E_LT; d40 = deflect(Ms['sus'], EI4, GJ * E_LT40 / E_LT); lim = L_bound / SAG_DIV
            Mp_s = split(Ms['sus'])[0]; Mp_b = split(Ms['bump_v'])[0]; Mt_s = split(Ms['sus'])[1]; Mt_b = split(Ms['bump_v'])[1]; Mp_h, Mt_h = split(Ms['bump_h'])
            Iz = (I_circ if opt == 'solid' else I_shell)[:i_entry + 1]; rz = rd[:i_entry + 1]
            def vm(Mp, Mt): sg = Mp[:i_entry + 1] * rz / Iz; tu = Mt[:i_entry + 1] * rz / (2 * Iz); return np.sqrt(sg ** 2 + 3 * tu ** 2)
            vs = vm(Mp_s, Mt_s); vb = np.maximum(vm(Mp_b, Mt_b), vm(Mp_h, Mt_h))
            opts[opt] = dict(rim_sag_23C_mm=round(d23, 2), rim_sag_40C_mm=round(d40, 2), limit_mm=round(lim, 2), sigma_sus_max_MPa=round(float(vs.max()), 2), sigma_bump_max_MPa=round(float(vb.max()), 2), limb_zone_len_mm=float(sd[i_entry]), limb_zone_solid_mass_kg=round(float((np.pi * rd[:i_entry] ** 2 * 4.0).sum() * 1.27e-6), 2),
                             sag_ok=bool(d23 <= lim), sag_ok_with_margin=bool(d23 <= lim / MARGIN_PRINTED), sag_ok_40C=bool(d40 <= lim), sus_ok=bool(vs.max() <= SIG_SUS), bump_ok=bool(vb.max() <= SIG_TRN), worst_station_s_mm=float(sd[int(vb.argmax())]))
        res['printed'] = opts
        pz = [q for q in sec_rows if q['zone'] == 'plate' and q['Ia_ring'] > 0]; Mpb = split(np.maximum.reduce([np.abs(Ms['bump_v']), np.abs(Ms['bump_h'])]))[0]
        sg_pl = [Mpb[min(int(round(q['s'] / 4.0)), len(Mpb) - 1)] * (q['ext_v'] / 2.0) / q['Ia_ring'] for q in pz if q['s'] <= sd[i_L]]
        res['plate_zone'] = dict(max_sigma_bump_shell3mm_MPa=round(float(max(sg_pl)), 2) if sg_pl else None, allow_MPa=SIG_TRN, note='3 mm ring of the voxel section, no infill/ribs credited; flat-top skin and 5.5 mm rim not checked')
        # rods
        rods = {}
        for dmm in RODS:
            rr = dmm / 2.0 + 0.2; best = None
            for kend in range(i_L, max(i_entry - 1, 1), -1):
                Pm = cd[:kend + 1].mean(0); u = np.linalg.svd(cd[:kend + 1] - Pm)[2][0]
                if (cd[kend] - cd[0]) @ u < 0: u = -u
                a0 = (cd[0] - Pm) @ u; a1 = (cd[kend] - Pm) @ u; smp = Pm[None, :] + np.arange(a0, a1 + 1e-6, 4.0)[:, None] * u; P_a = Pm + a0 * u
                e_all = edt_at(smp); cov = float((e_all - rr).min()); sc_len = float(a1 - a0)
                if cov >= COVER_FLOOR: best = (kend, sc_len, cov, u, P_a); break
            if best is None:
                Pm = cd[:i_entry + 1].mean(0); u = np.linalg.svd(cd[:i_entry + 1] - Pm)[2][0]; u = -u if (cd[i_entry] - cd[0]) @ u < 0 else u; a0 = (cd[0] - Pm) @ u; a1 = (cd[i_entry] - Pm) @ u
                e_all = edt_at(Pm[None, :] + np.arange(a0, a1 + 1e-6, 4.0)[:, None] * u); dv = float(np.linalg.norm(np.cross(cd[:i_entry + 1] - Pm, u), axis=1).max())
                rods[dmm] = dict(fits=False, why='no straight axis from root to plate entry with cover >= 3 mm', best_fit_axis_min_cover_mm=round(float((e_all - rr).min()), 1), centreline_dev_from_axis_mm=round(dv, 1)); continue
            kend, sc_len, cov, u, P_a = best; emb_target = 8 * dmm; tz = u[2]; emb_av = (P_a[2] - (ZMIN_ROD + dmm / 2)) / tz if tz > 1e-6 else emb_target; emb = float(min(emb_target, max(emb_av, 0)))
            P0 = P_a - emb * u; proj = (cd - P0) @ u; cov_idx = np.where((proj >= 0) & (np.arange(n) <= kend))[0]; dev = float(np.linalg.norm(np.cross(cd[:kend + 1] - P_a, u), axis=1).max())
            rod = dict(d=dmm, cov_idx=cov_idx); Ir = np.pi * dmm ** 4 / 64; wr = [(int(i), RHO_S * np.pi * dmm ** 2 / 4 * 4.0) for i in cov_idx]
            Mr = {c: moments(cd, i_L, forces_for(c, wr)) for c in ('sus', 'fact', 'bump_v', 'bump_h')}
            EI, GJ = prof('shell', rod); dsag = deflect(Mr['sus'], EI, GJ); lim = L_bound / SAG_DIV; dc = {}
            for c in ('fact', 'bump_v', 'bump_h'):
                Mp, Mt = split(Mr[c]); ids = [i for i in cov_idx if i <= i_L]; sg = 32 * Mp[ids] / (np.pi * dmm ** 3); tu = 16 * Mt[ids] / (np.pi * dmm ** 3); dc[c] = round(float(np.sqrt(sg ** 2 + 3 * tu ** 2).max() / FY), 2)
            Mroot = float(np.linalg.norm(Mr['bump_v'][0])); bear_F = Mroot / (0.67 * emb) if emb > 0 else float('inf'); bear_stress = bear_F / (dmm * emb / 2) if emb > 0 else float('inf')
            rods[dmm] = dict(fits=True, rod_end_s_mm=float(sd[kend]), rod_len_in_limb_mm=round(sc_len, 0), embed_mm=round(emb, 0), embed_8d_mm=emb_target, embed_ok=bool(emb >= emb_target - 1e-6), min_cover_mm=round(cov, 1), cover5_ok=bool(cov >= COVER),
                             chord_dev_from_centreline_mm=round(dev, 1), rim_sag_mm=round(dsag, 2), limit_mm=round(lim, 2), sag_ok=bool(dsag <= lim), DC_fact=dc['fact'], DC_bump_v=dc['bump_v'], DC_bump_h=dc['bump_h'], DC_max=max(dc.values()), rod_weight_N=round(RHO_S * np.pi * dmm ** 2 / 4 * float(sc_len + emb), 2),
                             root_bearing_MPa=round(bear_stress, 2), rod_end_to_load_pt_mm=round(float(np.linalg.norm(cd[kend] - pt_bound)), 0),
                             ok=bool(dsag <= lim and max(dc.values()) <= DC_ROD))
        res['limb_core'] = dict(A_core_over_A_circ_min=round(float(A_ratio[:i_entry + 1].min()), 2), I_core_min_entry_mm4=round(float(I_circ[:i_entry + 1].min())), I_core_root=round(float(I_circ[0])), I_core_at_entry=round(float(I_circ[i_entry])), I_plate_ring_min=round(float(I_plate_ring[i_entry:i_L + 1].min())) if i_L > i_entry else None)
        res['rods'] = rods
        ok_rods = [d for d, r in rods.items() if r.get('ok')]; res['rod_min_ok_mm'] = min(ok_rods) if ok_rods else None
        # wall: moments of the sustained+bump (C_b) and factored (C_f) cases at the root, anchors on a dedicated 2-stud cleat row; rod weight not included (small)
        wall = {}
        for cname, c in (('C_f', 'fact'), ('C_b', 'bump_v')):
            Fs = forces_for(c); V = float(sum(-f[2][1] for f in Fs)); Mx = float(sum(-f[2][1] * f[1][2] for f in Fs)); Xm = float(sum(-f[2][1] * (f[1][0] - root[0]) for f in Fs)); dx = Xm / V   # lever of resultant from the root, x; z lever Mx/V
            row = {}
            for s in S_ROWS:
                Tup = Mx / s / 2.0   # per upper screw (1 per stud, 2 studs)
                for phase, e in (('stud_at_root', abs(dx)), ('mid', max(abs(dx) - A_STUD / 2, 0.0))):
                    Rn = V * (1 + e / A_STUD); Ru = V * e / A_STUD
                    near = (Tup / SCREW_T + (Rn / 2 + SCULPT_SHEAR) / SCREW_V); far = (Tup + Ru / 2) / SCREW_T
                    n2 = max((Tup / 2) / SCREW_T + (Rn / 4 + SCULPT_SHEAR / 2) / SCREW_V, (Tup / 2 + Ru / 4) / SCREW_T)
                    row[f's{int(s)}_{phase}'] = dict(T_upper_screw_N=round(Tup, 0), R_near_N=round(Rn, 0), R_uplift_N=round(Ru, 0), DC_near=round(near, 2), DC_far=round(far, 2), DC=round(max(near, far), 2), DC_two_screws_per_row_per_stud=round(n2, 2))
            wall[cname] = dict(V_N=round(V, 1), Mx_Nm=round(Mx / 1e3, 2), Mz_Nm=round(Xm / 1e3, 2), lever_x_mm=round(dx, 0), lever_z_mm=round(Mx / V, 0), **row)
        res['wall'] = wall
        pr = res['printed']; wc = wall['C_b']['s100_stud_at_root']; ok_stress = lambda o: o['sus_ok'] and o['bump_ok']
        if ok_stress(pr['shell']) and pr['shell']['sag_ok_with_margin']: arm = 'PASS'; cond = 'printed hollow limb, continuous wall >= %.1f mm, no sockets through it' % T_RING
        elif ok_stress(pr['solid']) and pr['solid']['sag_ok_with_margin']: arm = 'CONDITIONAL'; cond = 'limb zone (s 0-%d mm) 100%% infill solid, or steel rod' % sd[i_entry]
        elif res['rod_min_ok_mm']: arm = 'CONDITIONAL'; cond = 'straight steel rod d >= %d mm (Fy >= 300), no printed option passes' % res['rod_min_ok_mm']
        else: arm = 'FAIL'; cond = 'no printed option and no straight rod fits the sweep'
        wv = 'PASS' if wc['DC'] <= 0.45 else ('CONDITIONAL' if wc['DC_two_screws_per_row_per_stud'] <= 0.5 else 'FAIL')
        res['verdict'] = dict(arm=arm, arm_condition=cond, wall=wv, wall_DC_C_b_s100_worst_phase_1_screw=wc['DC'], wall_DC_2_screws=wc['DC_two_screws_per_row_per_stud'])
        out[nm] = res
    return out


if __name__ == '__main__':
    R = {v: run(v) for v in ('H13', 'E1')}
    R['studs_under_width'] = {str(w): dict(width_mm=w, bays=round(w / A_STUD, 2), n_studs_min=int(w // A_STUD), n_studs_max=int(w // A_STUD) + 1, P_max_count=round(float(w / A_STUD - w // A_STUD), 2)) for w in (914, 1206)}   # 406 mm OC; P = fraction of stud phases giving n_max
    R['assumptions'] = dict(W_plant_N=W_PLANT, W_fact_N=W_FACT, bump_N=BUMP_V, inset_mm=INSET, E_lt_MPa=E_LT, E_lt40_MPa=E_LT40, E_steel_MPa=E_S, sigma_sus_MPa=SIG_SUS, sigma_trn_MPa=SIG_TRN, Fy_MPa=FY, DC_rod=DC_ROD, retention=RET, t_ring_mm=T_RING, sag_div=SAG_DIV, margin_printed=MARGIN_PRINTED, cover_mm=COVER, cover_floor_mm=COVER_FLOOR, rows_s_mm=list(S_ROWS), stud_oc_mm=A_STUD, screw_T_N=SCREW_T, screw_V_N=SCREW_V, sculpt_shear_N=SCULPT_SHEAR)
    json.dump(R, open(os.path.join(HERE, 'shelf_arms_r13.json'), 'w'), indent=1)
    for v, d in ((k, R[k]) for k in ('H13', 'E1')):
        for nm, r in d.items():
            p = r['plate']; print(v, nm, 'L_bound', p['L_bound_mm'], 'L_rim', p['L_rim_mm'], 'Wplate', p['W_plate_N_ret042'], 'Wlimb', p['W_limb_N_ret042'], 'Mroot_bump', r['root_moment']['bump_v']['M_Nm'], 'Mroot_sus', r['root_moment']['sus']['M_Nm'])
            print('   printed', {k: (o['rim_sag_23C_mm'], o['limit_mm'], o['sigma_sus_max_MPa'], o['sigma_bump_max_MPa']) for k, o in r['printed'].items()}, 'rod_min', r['rod_min_ok_mm'])
            print('   rods', {d: (x.get('rim_sag_mm'), x.get('DC_max'), x.get('embed_mm'), x.get('min_cover_mm'), x.get('ok')) for d, x in r['rods'].items()})
            print('   verdict', r['verdict'])
