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
for sid in studies.STUDIES:
    S = studies.STUDIES[sid]; meta = json.load(open(f'{HERE}/build/{sid}_meta.json')); vol = np.load(f'{HERE}/build/{sid}_solid.npy', mmap_mode='r'); d = {}
    sh = {}
    for p in meta['plates']:
        top = p['top']; jt = int(round((top - YS[0]) / RES)); i0 = max(int((p['cx'] - p['a'] * 1.4 - XS[0]) // RES), 0); i1 = int((p['cx'] + p['a'] * 1.4 - XS[0]) // RES)
        k0 = int((max(p['cz'] - p['b'] * 1.4, 0) + 8) // RES); k1 = int((p['cz'] + p['b'] * 1.4 + 8) // RES)
        under = np.asarray(vol[i0:i1, jt - 1, k0:k1]); jn = min(jt + 2 + int(300 // RES), len(YS) - 1)
        above = np.asarray(vol[i0:i1, jt + 2:jn, k0:k1]).any(axis=1)
        free = under & ~above; a, hh, ww, ie, sj = largest_rect(free)
        # clear height over the rectangle (first solid above plane inside it), capped 300
        ri = slice(ie - hh + 1, ie + 1); rk = slice(sj, sj + ww); col = np.asarray(vol[i0:i1, jt + 2:jn, k0:k1])[ri, :, rk].any(axis=(0, 2)); clear = 300.0 if not col.any() else float(np.argmax(col) * RES + 2)
        # largest intrusion above the plane anywhere on the plate footprint (fingers' hook)
        ab = np.asarray(vol[i0:i1, jt + 2:jt + 60, k0:k1]).any(axis=(0, 2)); intr = float(np.nonzero(ab)[0].max() * RES + 2) if ab.any() else 0.0
        sh[p['limb'] + '@' + str(p['cx'])] = dict(flat_top_x_mm=round(hh * RES), flat_top_z_mm=round(ww * RES), clear_above_flat_mm=round(clear), max_rise_above_top_mm=round(intr, 1), top_y=top)
    d['shelves'] = sh
    d['maw_to_mask_area'] = None
    ch = json.load(open(f'{HERE}/checks/{sid}.json')) if os.path.exists(f'{HERE}/checks/{sid}.json') else None
    if ch: d['maw_to_mask_area'] = ch['checks']['5']['maw_to_mask_area']
    d['eyes'] = meta['eyes']; d['n_teeth'] = meta['teeth']; d['limb_R0_diam_mm'] = {L['name']: round(2 * L['r0']) for L in meta['limbs']}; d['n_limbs_total'] = len(meta['limbs']); d['n_webs'] = len(S['webs'])
    out[sid] = d
json.dump(out, open(f'{HERE}/measure_extra.json', 'w'), indent=1); print(json.dumps(out, indent=1)[:6000])
