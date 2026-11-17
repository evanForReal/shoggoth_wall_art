#!/usr/bin/env python3
"""Build one composition study: python3 build.py STUDY_ID  -> build/<id>.npz (mesh+labels), <id>_meta.json, <id>_sil.npy"""
import sys, os, json, importlib
import numpy as np
from scipy import ndimage as ndi
from skimage import measure
from engine import *
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'build')
TH, RR = 54.0, 26.0

def plate_fn(cx, top, cz, a, b, seed):
    rng = np.random.default_rng(seed); ph = rng.uniform(0, 6.28, 3)
    cy = top - TH / 2
    def fn(X, Y, Z):
        dx, dz = X - cx, Z - cz; th = np.arctan2(dz, dx)
        sc = 1 + 0.07 * np.sin(2 * th + ph[0]) + 0.05 * np.sin(3 * th + ph[1])
        q = (np.abs(dx) / (a * sc)) ** 2.6 + (np.abs(dz) / (b * sc)) ** 2.6
        # outward distance of the rounded-superellipse; flat top >=150x150 is kept inside (a-RR, b-RR)
        d2 = (q ** (1 / 2.6) - 1) * min(a, b) * 0.95 + RR
        qn = np.clip(q ** (1 / 2.6), 0, 1); belly = 14.0 * (1 - qn ** 2)          # underside bows down (cradle), top stays flat at `top`
        dy = np.abs(Y - (cy - belly / 1.0)) - (TH / 2 + belly)
        w = np.stack([d2 - RR, dy - 0.0], 0)
        out = np.minimum(np.maximum(w[0], w[1]), 0) + np.sqrt(np.maximum(w[0], 0) ** 2 + np.maximum(w[1], 0) ** 2)
        return out
    return fn

def tune_r0(S):
    S['_notune'] = True   # area-targeting abandoned: it produced bulbous arms (see README); r0 per limb is hand-set in studies.py
    return _fit_arms(S)

def _tune_r0_unused(S):
    """Grade limb areas (c01 hierarchy / checklist #8): target area for rank i = 38k/1.32^i (floor 11k) by S['order']; area ~ r0."""
    from engine import curve, apply_wave
    sp = np.array(S['spine']); rt = np.array(S['spine_r']); cs, ts, _ = curve(sp, 1.5)
    body = Image.new('L', (NX, NY), 0); d = ImageDraw.Draw(body)
    def disc(d, px, py, rr):
        i, j = (px - XS[0]) / RES, (py - YS[0]) / RES; q = rr / RES; d.ellipse([i - q, j - q, i + q, j + q], fill=255)
    for (px, py, _), rr in zip(cs[::3], np.interp(ts[::3], rt[:, 0], rt[:, 1])): disc(d, px, py, rr)
    mw = S['maw']; mww, mhh = (mw['h'], mw['w']) if mw['orient'] == 'h' else (mw['w'], mw['h'])
    X, Y = np.meshgrid(XS, YS, indexing='ij'); bm = (np.asarray(body).T > 0) | ((((X - mw['c'][0]) / (mww / 2 + 45)) ** 2 + ((Y - mw['c'][1]) / (mhh / 2 + 45)) ** 2) < 1)
    order = S['order']; byname = {L['name']: L for L in S['limbs']}
    for it in range(9):
        for L in S['limbs']:
            c, t, _ = curve(L['pts']); c = apply_wave(c, t, L.get('wave')); r = tent_r(t, L['r0'], L.get('r_tip', 6.0), L.get('p', 0.75))
            im = Image.new('L', (NX, NY), 0); dd = ImageDraw.Draw(im)
            for (px, py, _), rr in zip(c[::3], r[::3]): disc(dd, px, py, rr)
            L['_area'] = float(((np.asarray(im).T > 0) & ~bm).sum() * PXA)
        ns = nf = 0
        for nm in order:
            L = byname[nm]
            if L.get('shelf'): tgt = [44000, 32500, 23500][ns]; ns += 1
            elif nf < 2: tgt = [18000, 16000][nf]; nf += 1
            else: L['r0'] = float(np.clip(L['r0'], 36, 40)); continue
            L['r0'] = float(np.clip(L['r0'] * (tgt / max(L['_area'], 1)) ** 0.9, 36, 128))
    for L in S['limbs']: L.pop('_area', None)
    return _fit_arms(S)

def _fit_arms(S):
    from engine import tent_r
    # shelf arms: keep every point from index 2 on below (plate top - 12 - local radius) so thick arms never rise above the plate plane
    for L in S['limbs']:
        if not L.get('shelf'): continue
        P = L['shelf']; pts = [list(p) for p in L['pts']]; seg = np.r_[0, np.cumsum([np.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)])]
        for i in range(2, len(pts)):
            r_i = float(tent_r(seg[i] / seg[-1], L['r0'], L.get('r_tip', 6.0), L.get('p', 0.75)))
            lim = P['top'] - 12 - r_i
            if i >= 4 and i < 7: lim = min(lim, pts[i][1])
            if pts[i][1] > lim and not (i >= 7): pts[i][1] = lim
        L['pts'] = [tuple(p) for p in pts]

PXA = RES * RES
def build(S):
    tune_r0(S)
    f = Field(); meta = dict(id=S['id'], name=S['name'], limbs=[], plates=[])
    # ---- body: ONE sweep along the spine (head -> pelvis), z-flattened for bas-to-mid relief
    sp = np.array(S['spine']); rt = np.array(S['spine_r'])
    rfun = lambda t: np.interp(t, rt[:, 0], rt[:, 1])
    f.add_sweep('body', sp, rfun, k=30, zs=S.get('body_zs', 2.0))
    # chest swell around the maw (organ is part of the torso, not a ring)
    mw = S['maw']; mcx, mcy, mww, mhh = mw['c'][0], mw['c'][1], mw['w'], mw['h']
    if mw['orient'] == 'h': mww, mhh = mhh, mww
    sw = ellipsoid((mcx, mcy), mww / 2 + 45, mhh / 2 + 45, (30, 60))
    f.add_fn((mcx - mww / 2 - 130, mcy - mhh / 2 - 130, 0), (mcx + mww / 2 + 130, mcy + mhh / 2 + 130, 160), sw, k=40)
    # ---- limbs: continuous tapered sweeps rooted inside the body
    for L in S['limbs']:
        r0 = L['r0']; rf = (lambda r0, pp: (lambda t: tent_r(t, r0, L.get('r_tip', 6.0), pp)))(r0, L.get('p', 0.75))
        c, t, r, ln = f.add_sweep(L['name'], L['pts'], rf, k=L.get('k', 26), wave=L.get('wave'))
        meta['limbs'].append(dict(name=L['name'], shelf=bool(L.get('shelf')), length=float(ln), r0=r0,
                                  c=c[::8].tolist(), r=r[::8].tolist(), t=t[::8].tolist()))
        if L.get('shelf'):
            P = L['shelf']; fn = plate_fn(P['cx'], P['top'], P['cz'], P['a'], P['b'], P.get('seed', 1))
            lo = (P['cx'] - P['a'] * 1.2 - 40, P['top'] - TH - 40, 0); hi = (P['cx'] + P['a'] * 1.2 + 40, P['top'] + 20, P['cz'] + P['b'] * 1.2 + 40)
            f.add_fn(lo, hi, fn, k=26)
            fa, fb = P['a'] + 4, P['b'] + 4
            f.carve((P['cx'] - fa, P['top'] - 2, P['cz'] - fb), (P['cx'] + fa, P['top'] + 40, P['cz'] + fb),
                    (lambda P_, fa_, fb_: (lambda X, Y, Z: np.where((np.abs(X - P_['cx']) < fa_) & (np.abs(Z - P_['cz']) < fb_), -(Y - P_['top']), 1e3)))(P, fa, fb))
            meta['plates'].append(dict(limb=L['name'], **{k: P[k] for k in ('cx', 'top', 'cz', 'a', 'b')}))
    # ---- mask: domed disc seated on the head (one pale value), smooth-blended only slightly
    mk = S['mask']; mrx, mry = mk['D'] / 2, mk['D'] / 2 * mk.get('aspect', 1.0)
    mfn = ellipsoid(mk['c'], mrx, mry, (mk['z'], mk.get('dz', 38)))
    f.add_fn((mk['c'][0] - mrx - 20, mk['c'][1] - mry - 20, 0), (mk['c'][0] + mrx + 20, mk['c'][1] + mry + 20, 220), mfn, k=6)
    # ---- maw: dark recessed almond carved into the torso
    ad = almond(mcx, mcy, mw['w'], mw['h'], tilt=(np.pi / 2 if mw['orient'] == 'h' else 0) + mw.get('tilt', 0), seed=S.get('seed', 0))
    ZR, SL, FLOOR = 100.0, 0.35, 12.0
    cav = lambda X, Y, Z: np.maximum(ad(X, Y) + SL * np.clip(ZR - Z, 0, None), FLOOR - Z)
    f.carve((mcx - mww / 2 - 20, mcy - mhh / 2 - 20, 0), (mcx + mww / 2 + 20, mcy + mhh / 2 + 20, 250), cav)
    F = f.finish()
    sil = (F < 0).any(axis=2)
    v, fc, nrm, _ = measure.marching_cubes(F, 0.0, spacing=(RES,) * 3)
    v = v + np.array([XS[0], YS[0], ZS[0]])
    # labels
    x, y, z = v[:, 0].copy(), v[:, 1].copy(), v[:, 2].copy()
    mk_v = mfn(x, y, z); dm = ad(x, y) + SL * np.clip(ZR - z, 0, None)
    meta['mask'] = dict(c=mk['c'], D=mk['D'], aspect=mk.get('aspect', 1.0)); meta['maw'] = dict(c=mw['c'], w=mw['w'], h=mw['h'], orient=mw['orient'])
    meta['spine'] = dict(pts=S['spine'], r=S['spine_r'], zs=S.get('body_zs', 2.0))
    meta['gesture'] = S['gesture']
    os.makedirs(OUT, exist_ok=True)
    np.savez_compressed(os.path.join(OUT, S['id'] + '.npz'), v=v.astype(np.float32), f=fc.astype(np.int32),
                        mk=mk_v.astype(np.float32), dm=dm.astype(np.float32))
    np.save(os.path.join(OUT, S['id'] + '_sil.npy'), sil); np.save(os.path.join(OUT, S['id'] + '_solid.npy'), F < 0)
    np.save(os.path.join(OUT, S['id'] + '_zmax.npy'), np.where((F < 0).any(2), ZS[(F < 0).shape[2] - 1 - np.argmax((F < 0)[:, :, ::-1], axis=2)], 0).astype(np.float32))
    # per-part silhouettes (disc stamping, 1 px = RES)
    def stamp(c, r):
        im = Image.new('L', (NX, NY), 0); d = ImageDraw.Draw(im)
        for (px, py, _), rr in zip(c, r):
            i, j = (px - XS[0]) / RES, (py - YS[0]) / RES; q = rr / RES
            d.ellipse([i - q, j - q, i + q, j + q], fill=255)
        return np.asarray(im).T > 0
    bp = f.parts['body']; body = stamp(bp['c'], bp['r'])
    # include chest swell footprint
    X, Y = np.meshgrid(XS, YS, indexing='ij')
    body |= (((X - mcx) / (mww / 2 + 45)) ** 2 + ((Y - mcy) / (mhh / 2 + 45)) ** 2) < 1
    np.save(os.path.join(OUT, S['id'] + '_body.npy'), body)
    limbs = {}
    for L in meta['limbs']:
        p = f.parts[L['name']]; limbs[L['name']] = stamp(p['c'], p['r'])
    np.savez_compressed(os.path.join(OUT, S['id'] + '_limbs.npz'), **limbs)
    json.dump(meta, open(os.path.join(OUT, S['id'] + '_meta.json'), 'w'))
    print(S['id'], 'tris', len(fc), 'sil px', int(sil.sum()))
    return F

def preview(S, F):
    from PIL import Image
    inside = F < 0
    zm = np.where(inside.any(2), ZS[inside.shape[2] - 1 - np.argmax(inside[:, :, ::-1], axis=2)], 0)
    gx, gy = np.gradient(zm, RES); sh = np.clip(0.6 + (gx * -0.6 + gy * 0.8) * 0.9 / 1.0, 0.1, 1.2)
    col = np.where(inside.any(2), 40 + 130 * sh * np.clip(0.5 + zm / 250, 0.4, 1), 12)
    img = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8).T[::-1]); img.save(os.path.join(OUT, S['id'] + '_prev.png'))

if __name__ == '__main__':
    sid = sys.argv[1]; sys.path.insert(0, HERE)
    S = importlib.import_module('studies').STUDIES[sid]
    F = build(S); preview(S, F)
