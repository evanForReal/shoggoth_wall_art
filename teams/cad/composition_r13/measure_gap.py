#!/usr/bin/env python3
"""r13: plate-edge to body-silhouette gaps and shelf reach, before (r11 H, r12s H+S2) vs after (H13, E1). Front-view (xy) silhouettes from the voxel solids (2 mm), distances in mm.
plate silhouette = columns of the plate planform at the top plane x the contiguous solid run below the top (flare at the limb entry included); body = trunk/head sweep + maw ellipse (body.npy);
body group = body + eye patch disc + held mask part (ball / disc, projected) + left-shoulder cluster ellipse.  python3 measure_gap.py -> gap_reach.json"""
import os, sys, json, numpy as np
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.abspath(__file__)); R12 = os.path.join(HERE, '..', 'composition_r12s', 'build'); R11 = os.path.join(HERE, '..', 'composition_r11', 'build'); R13 = os.path.join(HERE, 'build')
RES = 2.0
CASES = {'r11 H': (R11, 'H', -468.0, dict(patch=(8, 262, 108, 108), bulges=[(-122, 34, 52, 100)])),
         'r12s H+S2': (R12, 'S2', -468.0, dict(patch=(8, 262, 108, 108), bulges=[(-122, 34, 52, 100)])),
         'H13': (R13, 'H13', -468.0, None), 'E1': (R13, 'E1', -612.0, None)}
def ell(X, Y, c, a, b): return ((X - c[0]) / a) ** 2 + ((Y - c[1]) / b) ** 2 < 1
out = {}
for case, (d, sid, X0, extra) in CASES.items():
    meta = json.load(open(f'{d}/{sid}_meta.json')); solid = np.load(f'{d}/{sid}_solid.npy', mmap_mode='r'); body = np.load(f'{d}/{sid}_body.npy'); maskp = np.load(f'{d}/{sid}_maskpart.npy', mmap_mode='r')
    nx, ny = body.shape; XS = X0 + RES * np.arange(nx); YS = X0 + RES * np.arange(ny); Xg, Yg = np.meshgrid(XS, YS, indexing='ij')
    if extra is None: extra = dict(patch=(*meta['patch']['c'], meta['patch']['a'], meta['patch']['b']), bulges=[(*b['c'], b['a'], b['b']) for b in meta['bulges']])
    grp = body.copy(); grp |= ell(Xg, Yg, extra['patch'][:2], extra['patch'][2], extra['patch'][3]); grp |= np.asarray(maskp).any(2)
    for b in extra['bulges']: grp |= ell(Xg, Yg, b[:2], b[2], b[3])
    dgrp = ndi.distance_transform_edt(~grp) * RES; dbody = ndi.distance_transform_edt(~body) * RES
    rows = {}; ZS = -8 + RES * np.arange(solid.shape[2])
    for p in meta['plates']:
        top = p['top']; jt = int(round((top - X0) / RES)); i0 = int((p['cx'] - p['a'] * 1.5 - X0) // RES); i1 = int((p['cx'] + p['a'] * 1.5 - X0) // RES); i0 = max(i0, 0); i1 = min(i1, nx)
        plan = np.asarray(solid[i0:i1, jt - 1, :]).copy(); k_hi = int((p['cz'] + p['b'] * 1.5 + 8) // RES); plan[:, k_hi:] = False
        run = np.asarray(solid[i0:i1, jt - 80:jt, :]); run = run[:, ::-1, :]         # y descending from jt-1
        alive = np.cumprod(run, axis=1).astype(bool) if False else np.logical_and.accumulate(run, axis=1)
        depth = alive.sum(1)          # contiguous run length (voxels) below the top plane at each (x, z)
        depth = np.where(plan, depth, 0); mdepth = depth.max(1)      # max over z: deepest bottom at each x
        sil = np.zeros(body.shape, bool)
        for ii in range(i1 - i0):
            if mdepth[ii] > 0: sil[i0 + ii, jt - mdepth[ii]:jt] = True
        xs_cols = np.where(mdepth > 0)[0]
        g = dgrp[sil]; gb = dbody[sil]; ix = np.argmin(np.where(sil, dgrp, 1e9)); px, py = np.unravel_index(ix, sil.shape)
        ixb = np.argmin(np.where(sil, dbody, 1e9)); pbx, pby = np.unravel_index(ixb, sil.shape)
        rows[p['limb']] = dict(plate_x_range=[round(float(XS[i0 + xs_cols.min()])), round(float(XS[i0 + xs_cols.max()]))], plate_thickness_max_mm=round(float(mdepth.max() * RES)), gap_to_body_group_mm=round(float(g.min()), 1), at_plate_px=[round(float(XS[px])), round(float(YS[py]))],
                               gap_to_trunk_head_body_mm=round(float(gb.min()), 1), at_plate_px_body=[round(float(XS[pbx])), round(float(YS[pby]))])
    # reach: arm root (limb centreline first sample) to the plate centroid
    reach = {}
    for L in meta['limbs']:
        if L['name'] not in ('S1_UL', 'S2_UR', 'S3_LL'): continue
        rt = np.array(L['c'][0]); pl = [p for p in meta['plates'] if p['limb'] == L['name']][0]; cxx = pl.get('centroid_x', pl['cx']); czz = pl.get('centroid_z', pl['cz']); cy = pl['top']
        reach[L['name']] = dict(root=[round(float(v), 1) for v in rt], plate_centroid_xz=[round(float(cxx), 1), round(float(czz), 1)], plate_top_y=cy, dx_wall_plane=round(abs(cxx - rt[0]), 1), dz=round(czz - rt[2], 1), horizontal_xz=round(float(np.hypot(cxx - rt[0], czz - rt[2])), 1),
                                 dist_3d=round(float(np.linalg.norm([cxx - rt[0], cy - rt[1], czz - rt[2]])), 1), dist_xy_wall_plane=round(float(np.hypot(cxx - rt[0], cy - rt[1])), 1), limb_path_len_mm=round(L['length'], 1))
    out[case] = dict(id=sid, gaps=rows, reach=reach, scale=meta.get('scale', 1.0)); print(case, json.dumps({k: (v['gap_to_body_group_mm'], v['gap_to_trunk_head_body_mm']) for k, v in rows.items()}), json.dumps({k: (v['dx_wall_plane'], v['horizontal_xz']) for k, v in reach.items()}))
json.dump(out, open(f'{HERE}/gap_reach.json', 'w'), indent=1)
