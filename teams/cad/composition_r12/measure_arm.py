#!/usr/bin/env python3
"""r11 holding-arm / mask measurements for Structural (mask-arm-v1.md s.7 P1-P12) + gap / max z / mass / components. python3 measure_arm.py [ID...] -> arm_report.json"""
import os, sys, json, numpy as np
from scipy import ndimage as ndi
from skimage import measure
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from engine import XS, YS, ZS, RES, X0
import heldmask as hm
B = os.path.join(HERE, 'build'); RHO = 1.27e-3     # g/mm3 PETG
IDS = sys.argv[1:] or ['C%d' % i for i in range(1, 11)]
def vox(p): return np.clip(np.round((np.asarray(p) - np.array([XS[0], YS[0], ZS[0]])) / RES).astype(int), 0, [len(XS) - 1, len(YS) - 1, len(ZS) - 1])
def crop(P, pad, G=None):
    lo = vox(np.min(P, 0) - pad); hi = vox(np.max(P, 0) + pad) + 1; return tuple(slice(a, b) for a, b in zip(lo, hi))
out = {}
for sid in IDS:
    meta = json.load(open(f'{B}/{sid}_meta.json')); g = meta['held_geo']; G = {k: (np.array(v) if isinstance(v, list) else v) for k, v in g.items()}; G['H'] = meta['held_in']
    solid = np.load(f'{B}/{sid}_solid.npy'); rest = np.load(f'{B}/{sid}_rest.npy'); armp = np.load(f'{B}/{sid}_armpart.npy'); maskp = np.load(f'{B}/{sid}_maskpart.npy'); r = {}
    A, d, Rx, T = G['A'], G['d'], G['Rx'], G['T']; sT, sx, sr = G['s_T'], G['s_exit'], G['s_rod']
    # ---- placement / envelope
    zm_ = np.where(solid.any(2), 0, 0); zt = np.where(solid.any(2), (len(ZS) - 1 - np.argmax(solid[:, :, ::-1], axis=2)), -1); zmax = float(ZS[zt.max()])
    Xg, Yg = np.meshgrid(XS, YS, indexing='ij'); mc = G['mc']
    fp = ((Xg - mc[0]) ** 2 + (Yg - mc[1]) ** 2) < 100 ** 2; rest_top = np.where(rest.any(2), ZS[len(ZS) - 1 - np.argmax(rest[:, :, ::-1], axis=2)], 0)
    r['max_z_mm'] = zmax; r['mask_front_z_max'] = float(G['zm'] + G['dz']); r['mask_back_z_at_centre'] = float(G['z_back']); r['flesh_patch_peak_z_before_eyes'] = float(G['surf_pk'])
    r['gap_mask_back_to_flesh_mm'] = float(G['z_back'] - G['surf_pk']); r['gap_mask_back_to_highest_rest_solid_under_mask_mm'] = float(G['z_back'] - rest_top[fp].max())
    ix, iy = vox([mc[0], mc[1], 0])[:2]; r['flesh_z_under_mask_centre_incl_eyes'] = float(rest_top[ix, iy]); r['mask_roll_deg'] = float(np.degrees(G['roll']))
    # ---- axis geometry
    r['rod_axis'] = dict(A=A.round(1).tolist(), exit=Rx.round(1).tolist(), tip_pad_face=T.round(1).tolist(), B0_mask_back=G['B0'].round(1).tolist(), dir=d.round(4).tolist(), tilt_from_wall_normal_deg=float(np.degrees(np.arccos(d[2]))),
                         rod_length_mm=float(sr), rod_embed_in_root_mm=float(sx), rod_into_mask_from_pad_face_mm=float(sr - sT), free_span_exit_to_pad_face_mm=float(sT - sx), arm_centreline_exit_to_tip_mm=float(sT - sx + 6), arm_centreline_A_to_tip_mm=float(sT + 6))
    # ---- fill internal cavities (bore) then EDT for core / cover
    sol_f = ndi.binary_fill_holes(solid); sl = crop(np.array([A, T, Rx]), 70)
    sub = np.pad(sol_f[sl], ((0, 0), (0, 0), (1, 0)), constant_values=False); sub[:, :, 0] = False
    # z<0 is wall: treat as solid for distance purposes
    sub = np.concatenate([np.ones(sub.shape[:2] + (6,), bool), sub[:, :, 1:]], 2) if sl[2].start == 0 else sub
    dt = ndi.distance_transform_edt(sub) * RES
    ss = np.arange(0, sr, 2.0); pts = A[None] + ss[:, None] * d[None]; off = np.array([sl[0].start, sl[1].start, sl[2].start + (6 if sl[2].start == 0 else 0) - (1 if False else 0)])
    ii = vox(pts) - np.array([sl[0].start, sl[1].start, sl[2].start]) + np.array([0, 0, 6 if sl[2].start == 0 else 0]); ii = np.clip(ii, 0, np.array(sub.shape) - 1); dd = dt[ii[:, 0], ii[:, 1], ii[:, 2]]
    span = (ss >= 0) & (ss <= sT); free = (ss >= sx) & (ss <= sT)
    r['P7_core_min_diameter_mm_over_rod_span_A_to_pad_face'] = float(2 * dd[span].min()); r['P7_core_min_diameter_free_span_mm'] = float(2 * dd[free].min()); r['P1_radial_cover_over_rod_min_mm_A_to_pad_face'] = float(dd[span].min() - hm.BORE_D / 2); r['P1_radial_cover_free_span_min_mm'] = float(dd[free].min() - hm.BORE_D / 2)
    # root diameter at the trunk exit (sheath radius there)
    c_, R_, sw_ = hm.sheath(G); iex = int(np.argmin(abs(np.linspace(0, sT + 6, len(c_)) - sx))); r['root_dia_at_exit_mm'] = float(2 * R_[iex]); r['arm_dia_root_mid_tip_mm'] = [float(2 * R_[iex]), float(2 * R_[(iex + len(R_) - 1) // 2]), float(2 * R_[-1])]; r['root_block_dia_mm'] = 2 * hm.BLOCK_R
    r['P8_rod_axis_vs_centreline_max_offset_mm'] = float(np.abs(sw_).max()); r['P8_sheath_centreline_lateral_offset_samples_mm'] = [round(float(x), 1) for x in sw_[::len(sw_) // 6]]
    # ---- P2/P3 root block solid + plate
    s_, rad_, U_, V_ = hm.axc(G, *np.meshgrid(XS[sl[0]], YS[sl[1]], ZS[sl[2]], indexing='ij')); blk = (rad_ < hm.BLOCK_R) & (s_ >= 0) & (s_ <= sx + 10); fl = ndi.binary_fill_holes(solid)[sl]
    r['P3_root_block_solid_fraction_60dia_x_82deep'] = float((fl & blk).sum() / blk.sum()); r['P3_block_dia_mm'] = 2 * hm.BLOCK_R; r['P3_block_depth_along_axis_mm'] = float(sx)
    pm = (np.abs(Xg - A[0]) <= 50) & (np.abs(Yg - A[1]) <= 50); k6 = int(round((6 - ZS[0]) / RES)) + 1; k0 = int(round((2 - ZS[0]) / RES))
    r['P3_back_plate_100x100x6_solid_fraction_in_trunk'] = float(solid[:, :, k0:k6][pm].mean()); r['P3_A_z_mm'] = float(A[2]); r['P3_block_min_z_mm'] = float(A[2] - hm.BLOCK_R * np.sqrt(1 - d[2] ** 2))
    # ---- P4 pad
    sm, rm_, Um, Vm = hm.axc(G, *np.meshgrid(XS[sl[0]], YS[sl[1]], ZS[sl[2]], indexing='ij')); mp = maskp[sl] | ndi.binary_fill_holes(maskp)[sl]
    pl = (sm > sT + 8) & (sm < sT + 24); ring = pl & (np.abs(rm_ - 33.5) < 1.5); air = pl & (np.abs(rm_ - 39) < 1.5)
    r['P4_pad_solid_fraction_on_r33.5_ring'] = float(mp[ring].mean()); r['P4_pad_solid_fraction_on_r39_ring'] = float(mp[air].mean()); r['P4_pad_dia_mm'] = 2 * hm.PAD_R; r['P4_pad_depth_along_axis_mm'] = hm.PAD_LEN; r['P4_fillet_smin_k'] = hm.FIL_K; r['P4_fillet_radius_est_mm'] = round(0.6 * hm.FIL_K, 1)
    # ---- mask CoM, lever, mass
    mfn = hm.mask_sdf_fn(G); mi = np.argwhere(maskp); com = np.array([XS[mi[:, 0]].mean(), YS[mi[:, 1]].mean(), ZS[mi[:, 2]].mean()]); V_total = maskp.sum() * RES ** 3 / 1e3
    p_ = com - A; perp = np.linalg.norm(p_ - np.dot(p_, d) * d); r['mask_CoM'] = com.round(1).tolist(); r['P5_CoM_offset_from_rod_axis_mm'] = float(perp)
    r['P5_horizontal_lever_exit_axis_to_CoM_mm'] = float(np.hypot(com[0] - Rx[0], com[2] - Rx[2])); r['P5_lever_incl_vertical_offset_3D_mm'] = float(np.linalg.norm(com - Rx)); r['P5_tilt_roll_deg'] = float(np.degrees(G['roll'])); r['P5_tilt_yaw_deg'] = float(np.degrees(G['yaw'])); r['P5_tilt_pitch_deg'] = float(np.degrees(G['pitch'])); r['P5_total_tilt_deg'] = float(np.degrees(np.sqrt(G['roll'] ** 2 + G['yaw'] ** 2 + G['pitch'] ** 2)))
    r['P5_lever_from_trunk_wall_plane_z0_horizontal_mm'] = float(np.hypot(com[0] - A[0], com[2] - 0.0)) if False else None
    nzm = np.argwhere(maskp); lo_, hi_ = nzm.min(0), nzm.max(0) + 1; sl2 = tuple(slice(int(a), int(b)) for a, b in zip(lo_, hi_)); gx = np.meshgrid(XS[sl2[0]], YS[sl2[1]], ZS[sl2[2]], indexing='ij'); disc = mfn(*gx) < 0
    mp2 = maskp[sl2]; dvol = mp2 & disc; pfvol = mp2 & ~disc; Vd = dvol.sum() * RES ** 3; Vpf = pfvol.sum() * RES ** 3
    vs, fs, _, _ = measure.marching_cubes(ndi.gaussian_filter(dvol.astype(np.float32), 0.8), 0.5, spacing=(RES,) * 3); Ad = measure.mesh_surface_area(vs, fs); shell = min(Ad * 2.0, Vd); inter = Vd - shell; mass = RHO * (shell + 0.15 * inter + Vpf)
    r['P6_mask_mass_calc'] = dict(V_disc_cm3=round(Vd / 1e3, 1), area_disc_cm2=round(Ad / 1e2, 1), shell_2mm_cm3=round(shell / 1e3, 1), interior_cm3=round(inter / 1e3, 1), infill15_cm3=round(0.15 * inter / 1e3, 1), V_pad_fingers_solid_cm3=round(Vpf / 1e3, 1), V_total_cm3=round(V_total, 1), PETG_g_cm3=1.27,
                                  mass_g=round(mass, 0), mass_with_5pct_finish_g=round(mass * 1.05, 0))
    r['P6_mask_mass_kg'] = round(mass * 1.05 / 1000, 3)
    # ---- P9 seam
    Rt = float(R_[-1]); r['P9'] = dict(arm_integral_with_trunk=True, root_seam=None, mask_end_seam_land_mm2=round(np.pi * Rt ** 2 - np.pi * (hm.BORE_D / 2) ** 2), spigot_socket_depth_mm=hm.SPIG_L, spigot_dia_mm=2 * hm.SPIG_R, d_flat_mm_from_axis=hm.FLAT, tip_dia_at_pad_face_mm=2 * Rt)
    r['P10_arm_axis_angle_from_XY_plane_deg'] = float(np.degrees(np.arcsin(abs(d[2])))); r['P11'] = dict(grip=G['H'].get('grip'), n_fingers=sum(1 for f_ in meta['fingers'] if 'ang' in f_), grip_items=meta['fingers'], d_flat_key=True)
    # ---- P12 clearances
    dr = ndi.distance_transform_edt(~rest[:, :, :]) * RES; mi_ = np.argwhere(maskp); r['P12_mask_part_min_dist_to_rest_of_piece_mm'] = float(dr[mi_[:, 0], mi_[:, 1], mi_[:, 2]].min())
    ai = np.argwhere(armp); P_ = np.stack([XS[ai[:, 0]], YS[ai[:, 1]], ZS[ai[:, 2]]], 1); far = np.linalg.norm(P_ - Rx, axis=1) > 45; zin = P_[:, 2] > 6; sA = (P_ - A) @ d
    sel = far & zin & (sA > sx + 20); r['P12_arm_free_span_min_dist_to_rest_mm_beyond_45mm_of_exit'] = float(dr[ai[sel, 0], ai[sel, 1], ai[sel, 2]].min()) if sel.any() else None
    sel2 = zin & (sA > sx + 45); r['P12_arm_free_span_min_dist_to_rest_mm_beyond_45mm_ALONG_AXIS'] = float(dr[ai[sel2, 0], ai[sel2, 1], ai[sel2, 2]].min()) if sel2.any() else None; sel3 = zin & (sA > sx + 5); r['P12_arm_min_dist_to_rest_beyond_5mm_of_exit_incl_blend'] = float(dr[ai[sel3, 0], ai[sel3, 1], ai[sel3, 2]].min()) if sel3.any() else None; r['P12_arm_free_span_min_z_mm'] = float(P_[sA > sx + 5, 2].min()); r['arm_part_z_range_mm'] = [float(P_[:, 2].min()), float(P_[:, 2].max())]; r['mask_part_z_range_mm'] = [float(ZS[nzm[:, 2].min()]), float(ZS[nzm[:, 2].max()])]; r['P12_wall_plane_clear_mm'] = r['P12_arm_free_span_min_z_mm']
    # ---- components
    lab, n = ndi.label(solid); sz = np.bincount(lab.ravel())[1:]; r['connected_components'] = int(n); r['components_over_0.1cm3'] = int((sz * RES ** 3 / 1e3 > 0.1).sum()); r['largest_components_cm3'] = sorted((sz * RES ** 3 / 1e3).round(1).tolist())[-3:]; r['component_volumes_cm3_smallest'] = sorted((sz * RES ** 3 / 1e3).round(2).tolist())[:6]
    r['veins'] = meta.get('veins'); r['eyes'] = {grp: [e['G'] for e in meta['eyes'] if e.get('grp') == grp] for grp in sorted({e.get('grp') for e in meta['eyes']})}
    # S10 nearest cleat seat: shelf roots
    roots = {a_['name']: tuple(a_['pts'][0][:2]) for a_ in [dict(name=l['name'], pts=[l['c'][0]]) for l in meta['limbs'] if l['name'] in ('S1_UL', 'S2_UR', 'S3_LL')]}; r['nearest_shelf_root'] = {k: round(float(np.hypot(Rx[0] - v[0], Rx[1] - v[1])), 0) for k, v in roots.items()}
    out[sid] = r; print(sid, json.dumps({k: v for k, v in r.items() if k.startswith(('P1_', 'P3', 'P5', 'P6_mask_mass_kg', 'P7', 'P12', 'max_z', 'gap', 'connected'))}, indent=0)[:1800])
json.dump(out, open(f'{HERE}/arm_report.json', 'w'), indent=1)
