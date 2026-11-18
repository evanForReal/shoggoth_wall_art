#!/usr/bin/env python3
"""Extra measurements for r08b: shelf flat-top rectangle + clear height above it, strand/bundle counts + min strand diameter, web open fractions, maw:mask area, IoU vs r07 G1a (png masks).
python3 measure_extra.py -> measure_extra.json"""
import os, sys, json, numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from engine import XS, YS, ZS, RES
import studies
def largest_rect(m):
    best = (0, 0, 0, 0, 0); h = np.zeros(m.shape[1], int)
    for i in range(m.shape[0]):
        h = np.where(m[i], h + 1, 0); st = []
        for j in range(m.shape[1] + 1):
            cur = h[j] if j < m.shape[1] else 0; s = j
            while st and st[-1][1] >= cur:
                s0, hh = st.pop(); a = hh * (j - s0)
                if a > best[0]: best = (a, hh, j - s0, i, s0)
                s = s0
            st.append((s, cur))
    return best     # area, rows(h in i), cols(w in j), end_i, start_j
out = {}
A0v = np.load(f'{HERE}/build/A0_solid.npy', mmap_mode='r')
for sid in studies.STUDIES:
    S = studies.STUDIES[sid]; meta = json.load(open(f'{HERE}/build/{sid}_meta.json')); vol = np.load(f'{HERE}/build/{sid}_solid.npy', mmap_mode='r'); d = {}
    sh = {}
    for p in meta['plates']:
        top = p['top']; jt = int(round((top - YS[0]) / RES)); i0 = max(int((p['cx'] - p['a'] * 1.4 - XS[0]) // RES), 0); i1 = int((p['cx'] + p['a'] * 1.4 - XS[0]) // RES)
        k0 = int((max(p['cz'] - p['b'] * 1.4, 0) + 8) // RES); k1 = int((p['cz'] + p['b'] * 1.4 + 8) // RES)
        under = np.asarray(vol[i0:i1, jt - 1, k0:k1]); jn = min(jt + 2 + int(300 // RES), len(YS) - 1)
        above = np.asarray(vol[i0:i1, jt + 2:jn, k0:k1]).any(axis=1)
        free = under & ~above; a, hh, ww, ie, sj = largest_rect(free)
        ri = slice(ie - hh + 1, ie + 1); rk = slice(sj, sj + ww); col = np.asarray(vol[i0:i1, jt + 2:jn, k0:k1])[ri, :, rk].any(axis=(0, 2)); clear = 300.0 if not col.any() else float(np.argmax(col) * RES + 2)
        # whole-footprint test: any solid above the plane anywhere on the plate footprint (incl. finger hooks), 300 mm
        ab = np.asarray(vol[i0:i1, jt + 2:jn, k0:k1]).any(axis=(0, 2)); first = float(np.argmax(ab) * RES + 2) if ab.any() else 300.0
        sh[p['limb']] = dict(top_y=top, cx=p['cx'], flat_top_x_mm=round(hh * RES), flat_top_z_mm=round(ww * RES), clear_above_flat_mm=round(clear), clear_above_footprint_mm=round(first), room_to_envelope_mm=round(457 - top), ok=bool(hh * RES >= 150 and ww * RES >= 150 and clear >= 299))
    d['shelves'] = sh
    # diff vs A0 (voxel): count, bbox (mm) of changed voxels
    dv = np.asarray(vol) ^ np.asarray(A0v); idxs = np.argwhere(dv)
    if len(idxs): lo = idxs.min(0); hi = idxs.max(0); d['diff_vs_A0'] = dict(voxels=int(len(idxs)), volume_cm3=round(len(idxs) * RES ** 3 / 1e3, 1), bbox_mm=[[round(float(XS[lo[0]])), round(float(XS[hi[0]]))], [round(float(YS[lo[1]])), round(float(YS[hi[1]]))], [round(float(ZS[lo[2]])), round(float(ZS[hi[2]]))]])
    else: d['diff_vs_A0'] = dict(voxels=0)
    sa = np.asarray(vol).any(2); sb = np.asarray(A0v).any(2); d['silhouette_xor_vs_A0_mm2'] = int((sa ^ sb).sum() * RES * RES); out[sid] = d
json.dump(out, open(f'{HERE}/measure_extra.json', 'w'), indent=1); print(json.dumps({k: (v['silhouette_xor_vs_A0_mm2'], v['diff_vs_A0']) for k, v in out.items()}, indent=1)[:3000])
