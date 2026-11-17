#!/usr/bin/env python3
"""Build one r08 study: python3 build.py ID -> build/<id>.npz (mesh + labels), _meta.json, _sil/_solid/_body/_limbs, preview."""
import sys, os, json, importlib
import numpy as np
from scipy import ndimage as ndi
from skimage import measure
from PIL import Image, ImageDraw
from engine import *

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'build')
TH, RR = 40.0, 18.0

def plate_fn(cx, top, cz, a, b, seed):
    ph = np.random.default_rng(seed).uniform(0, 6.28, 4); cy = top - TH / 2
    def fn(X, Y, Z):
        dx, dz = X - cx, Z - cz; th = np.arctan2(dz, dx)
        sc = 1 + 0.10 * np.sin(2 * th + ph[0]) + 0.07 * np.sin(3 * th + ph[1]) + 0.04 * np.sin(5 * th + ph[2])
        q = (np.abs(dx) / (a * sc)) ** 2.4 + (np.abs(dz) / (b * sc)) ** 2.4
        d2 = (q ** (1 / 2.4) - 1) * min(a, b) * 0.95 + RR; qn = np.clip(q ** (1 / 2.4), 0, 1)
        belly = 20.0 * (1 - qn ** 2); dy = np.abs(Y - (cy - belly)) - (TH / 2 + belly)
        w0, w1 = d2 - RR, dy
        return np.minimum(np.maximum(w0, w1), 0) + np.sqrt(np.maximum(w0, 0) ** 2 + np.maximum(w1, 0) ** 2)
    return fn

def mask_features(mk):
    """iconic smiley (feature-references s.1.1), lengths in D; returns sd fn (<0 inside feature, xy only) and constants."""
    D = mk['D']; cx, cy = mk['c']
    def ell(ex, ey, w, h, rot):
        ct, st = np.cos(rot), np.sin(rot)
        def f(X, Y):
            u = ct * (X - cx - ex * D) + st * (Y - cy - ey * D); v = -st * (X - cx - ex * D) + ct * (Y - cy - ey * D)
            return (np.sqrt((u / (w * D / 2)) ** 2 + (v / (h * D / 2)) ** 2) - 1) * (w * D / 2)
        return f
    eL = ell(-0.165, 0.160, 0.095, 0.215, 0.0); eR = ell(0.165, 0.160, 0.100, 0.228, np.radians(-2.0))
    # smile: arc through L end (-0.29,-0.080), bottom (0,-0.2475), R end (+0.29,-0.060) in D units
    P = np.array([[-0.29, -0.080], [0.0, -0.2475], [0.29, -0.060]]) * D; A = np.linalg.solve(np.c_[2 * P[:, 0], 2 * P[:, 1], np.ones(3)], -(P ** 2).sum(1)) if False else None
    M = np.c_[2 * P[:, 0], 2 * P[:, 1], np.ones(3)]; b = (P ** 2).sum(1); sol = np.linalg.solve(M, b); ccx, ccy = sol[0], sol[1]; R = np.sqrt(sol[2] + ccx ** 2 + ccy ** 2)
    a0 = np.arctan2(P[0, 1] - ccy, P[0, 0] - ccx); a1 = np.arctan2(P[2, 1] - ccy, P[2, 0] - ccx)
    if a1 < a0: a1 += 2 * np.pi
    ang = np.linspace(a0, a1, 400); arc = np.stack([ccx + R * np.cos(ang), ccy + R * np.sin(ang)], 1)
    # arc passes through the bottom point going L->R through the lower half: choose the sweep that contains the bottom
    mid = np.arctan2(P[1, 1] - ccy, P[1, 0] - ccx)
    if not (a0 <= mid <= a1 or a0 <= mid + 2 * np.pi <= a1):
        a0, a1 = a1, a0 + 2 * np.pi; ang = np.linspace(a0, a1, 400); arc = np.stack([ccx + R * np.cos(ang), ccy + R * np.sin(ang)], 1)
    tr = cKDTree(arc); stroke = 0.070 * D
    def mouth(X, Y):
        d, _ = tr.query(np.stack([(X - cx).ravel(), (Y - cy).ravel()], 1)); return d.reshape(X.shape) - stroke / 2
    def sd(X, Y): return np.minimum(np.minimum(eL(X, Y), eR(X, Y)), mouth(X, Y))
    return sd

def build(S):
    f = Field(); meta = dict(id=S['id'], name=S['name'], limbs=[], plates=[], webs=len(S.get('webs', [])), ribs=len(S.get('ribs', [])))
    # ---- body: ONE sweep along the spine (apex -> hanging end), z-flattened
    rf, sp = spine_rfun(S['spine4']); zsb = S.get('body_zs', 2.0)
    c, t, r, L = f.add_sweep('body', sp, rf, k=34, zs=zsb, kind=1)
    mw = S['maw']; mcx, mcy, mww, mhh = mw['c'][0], mw['c'][1], mw['w'], mw['h']
    sw = ellipsoid((mcx, mcy), mww / 2 + 40, mhh / 2 + 40, (28, 56))
    f.add_fn((mcx - mww / 2 - 120, mcy - mhh / 2 - 120, 0), (mcx + mww / 2 + 120, mcy + mhh / 2 + 120, 160), sw, k=40, kind=1)
    # ---- sinew cords: meridian strands over the trunk (fibrous read), broken around the mask and the maw
    cd = S.get('cords')
    if cd:
        cs_, ts_, _ = curve(sp, 3.0); rr_ = rf(ts_); tg_ = np.gradient(cs_[:, :2], axis=0); tg_ /= np.linalg.norm(tg_, axis=1)[:, None] + 1e-9; nr_ = np.stack([-tg_[:, 1], tg_[:, 0]], 1)
        adm = almond(mcx, mcy, mww + 20, mhh + 20, tilt=mw.get('tilt', 0.0), seed=S.get('seed', 0)); rng_ = np.random.default_rng(S.get('seed', 0) + 7)
        for ci, fr in enumerate(cd['f']):
            ph_ = rng_.uniform(0, 6.28); am_ = rng_.uniform(4, 9); sel = (ts_ > cd['t0']) & (ts_ < cd['t1']); idx_ = np.where(sel)[0][::7]
            P = []
            for i in idx_:
                q = cs_[i, :2] + nr_[i] * (fr * rr_[i] * 0.9 + am_ * np.sin(9 * ts_[i] + ph_))
                bad = (np.hypot(q[0] - S['mask']['c'][0], q[1] - S['mask']['c'][1]) < S['mask']['D'] / 2 + 18) or (adm(np.array([q[0]]), np.array([q[1]]))[0] < 22)
                P.append(None if bad else (float(q[0]), float(q[1])))
            run = []
            for q in P + [None]:
                if q is None:
                    if len(run) >= 4: f.add_rib(f'cord{ci}_{len(f.parts)}', run, r0=cd.get('r', 9.0), r1=6.5, lift=cd.get('lift', 5.0))
                    run = []
                else: run.append(q)
    # ---- ribs riding the trunk surface
    for i, xy in enumerate(S.get('ribs', [])): f.add_rib(f'rib{i}', xy, r0=S.get('rib_r', 8.0), r1=5.5)
    # ---- limbs (bundles) + plates + claws
    for Lm in S['limbs']:
        c, t, R, ln = f.add_bundle(Lm['name'], Lm['pts'], Lm['R0'], n=Lm.get('n', 5), p=Lm.get('p', 0.75), r_tip=Lm.get('r_tip', 6.0), wave=Lm.get('wave'), twist=Lm.get('twist', 1.3), seed=Lm.get('seed', 0.0), k=Lm.get('k', 10.0))
        meta['limbs'].append(dict(name=Lm['name'], shelf=bool(Lm.get('shelf')), length=float(ln), r0=Lm['R0'], c=c[::8].tolist(), r=R[::8].tolist(), t=t[::8].tolist()))
        if Lm.get('shelf'):
            P = Lm['shelf']; fn = plate_fn(P['cx'], P['top'], P['cz'], P['a'], P['b'], P.get('seed', 1))
            lo = (P['cx'] - P['a'] * 1.25 - 30, P['top'] - TH - 50, 0); hi = (P['cx'] + P['a'] * 1.25 + 30, P['top'] + 20, P['cz'] + P['b'] * 1.25 + 30)
            f.add_fn(lo, hi, fn, k=22, kind=5)
            fa, fb = P['a'] + 4, P['b'] + 4
            f.carve((P['cx'] - fa, P['top'] - 2, P['cz'] - fb), (P['cx'] + fa, P['top'] + 40, P['cz'] + fb),
                    (lambda P_, fa_, fb_: (lambda X, Y, Z: np.where((np.abs(X - P_['cx']) < fa_) & (np.abs(Z - P_['cz']) < fb_), -(Y - P_['top']), 1e3)))(P, fa, fb))
            sd_ = 1 if P['cx'] > Lm['pts'][0][0] else -1
            for j, off in enumerate((-0.35, 0.30)):   # claw strands cradle the front rim from below (stay under the plane)
                x0 = P['cx'] + off * P['a'] * 2 * 0.8; z1 = P['cz'] + P['b'] * 0.80
                cl = [(x0 - 14 * sd_, P['top'] - 52, P['cz'] + 10), (x0, P['top'] - 40, z1 - 40), (x0 + 6 * sd_, P['top'] - 30, z1 + 6), (x0 + 6 * sd_, P['top'] - 17, z1 + 12)]
                cc, tt, _ = curve(cl, 1.5); f.sweep(f"{Lm['name']}.claw{j}", cc, 7.0 - 2.5 * tt, 6.0, store=False, kind=2)
            meta['plates'].append(dict(limb=Lm['name'], **{k: P[k] for k in ('cx', 'top', 'cz', 'a', 'b')}))
    # ---- lace webs
    for i, W in enumerate(S.get('webs', [])):
        f.add_web(W['poly'], W['anchors'], sag=W.get('sag', 0.22), th=W.get('th', 8.0), cell=W.get('cell', 46.0), sw=W.get('sw', 9.0), rim=W.get('rim', 9.0), seed=W.get('seed', i))
    # ---- mask: domed disc + bezel, then carved smiley
    mk = S['mask']; D = mk['D']; mrx = mry = D / 2; mcz = mk['z']; dzm = mk.get('dz', 26)
    mfn = ellipsoid(mk['c'], mrx, mry, (mcz, dzm))
    f.add_fn((mk['c'][0] - mrx - 20, mk['c'][1] - mry - 20, 0), (mk['c'][0] + mrx + 20, mk['c'][1] + mry + 20, 240), mfn, k=5, kind=6)
    def bezel(X, Y, Z):
        q = np.sqrt(((X - mk['c'][0]) / mrx) ** 2 + ((Y - mk['c'][1]) / mry) ** 2); return np.sqrt(((q - 0.985) * mrx) ** 2 + (Z - (mcz + 3)) ** 2) - 5.5
    f.add_fn((mk['c'][0] - mrx - 20, mk['c'][1] - mry - 20, 0), (mk['c'][0] + mrx + 20, mk['c'][1] + mry + 20, 240), bezel, k=3, kind=6)
    fsd = mask_features(mk); fl = mcz + dzm - 11.0
    f.carve((mk['c'][0] - mrx, mk['c'][1] - mry, fl - 2), (mk['c'][0] + mrx, mk['c'][1] + mry, 300), lambda X, Y, Z: np.maximum(fsd(X, Y), fl - Z))
    # ---- maw: dark almond recess, sloped walls
    ad = almond(mcx, mcy, mw['w'], mw['h'], tilt=mw.get('tilt', 0.0), seed=S.get('seed', 0)); ZR, SL, FLOOR = 110.0, 0.35, 12.0
    f.carve((mcx - mww / 2 - 20, mcy - mhh / 2 - 20, 0), (mcx + mww / 2 + 20, mcy + mhh / 2 + 20, 260), lambda X, Y, Z: np.maximum(ad(X, Y) + SL * np.clip(ZR - Z, 0, None), FLOOR - Z))
    F = f.finish(); sil = (F < 0).any(axis=2)
    v, fc, _, _ = measure.marching_cubes(F, 0.0, spacing=(RES,) * 3); v = v + np.array([XS[0], YS[0], ZS[0]])
    x, y, z = v[:, 0], v[:, 1], v[:, 2]
    ii = np.clip(((v - np.array([XS[0], YS[0], ZS[0]])) / RES).round().astype(int), 0, [NX - 1, NY - 1, NZ - 1])
    kind = f.K[ii[:, 0], ii[:, 1], ii[:, 2]]
    mk_v = mfn(x, y, z); dm = ad(x, y) + SL * np.clip(ZR - z, 0, None); fv = np.maximum(fsd(x, y), fl + 1.5 - z)
    meta.update(mask=dict(c=mk['c'], D=D, aspect=1.0), maw=dict(c=mw['c'], w=mw['w'], h=mw['h'], orient='v'), spine=dict(pts=[list(p) for p in sp.tolist()], zs=zsb), gesture=S['gesture'])
    os.makedirs(OUT, exist_ok=True); sid = S['id']
    np.savez_compressed(f'{OUT}/{sid}.npz', v=v.astype(np.float32), f=fc.astype(np.int32), mk=mk_v.astype(np.float32), dm=dm.astype(np.float32), fv=fv.astype(np.float32), kind=kind)
    np.save(f'{OUT}/{sid}_sil.npy', sil); np.save(f'{OUT}/{sid}_solid.npy', F < 0)
    ins = F < 0; top = NZ - 1 - np.argmax(ins[:, :, ::-1], axis=2); np.save(f'{OUT}/{sid}_zmax.npy', np.where(ins.any(2), ZS[top], 0).astype(np.float32))
    def stamp(cc, rr):
        im = Image.new('L', (NX, NY), 0); d = ImageDraw.Draw(im)
        for (px, py, _), q in zip(cc[::2], rr[::2]):
            i, j = (px - XS[0]) / RES, (py - YS[0]) / RES; q = q / RES; d.ellipse([i - q, j - q, i + q, j + q], fill=255)
        return np.asarray(im).T > 0
    bp = f.parts['body']; body = stamp(bp['c'], bp['r']); Xg, Yg = np.meshgrid(XS, YS, indexing='ij')
    body |= (((Xg - mcx) / (mww / 2 + 40)) ** 2 + ((Yg - mcy) / (mhh / 2 + 40)) ** 2) < 1
    np.save(f'{OUT}/{sid}_body.npy', body)
    np.savez_compressed(f'{OUT}/{sid}_limbs.npz', **{L['name']: stamp(f.parts[L['name']]['c'], f.parts[L['name']]['r']) for L in meta['limbs']})
    json.dump(meta, open(f'{OUT}/{sid}_meta.json', 'w')); print(sid, 'tris', len(fc), 'sil px', int(sil.sum()))
    inside = F < 0; zm = np.where(inside.any(2), ZS[inside.shape[2] - 1 - np.argmax(inside[:, :, ::-1], axis=2)], 0)
    gx, gy = np.gradient(zm, RES); sh = np.clip(0.6 + (gx * -0.6 + gy * 0.8) * 0.9, 0.1, 1.2)
    col = np.where(inside.any(2), 40 + 130 * sh * np.clip(0.5 + zm / 250, 0.4, 1), 12)
    Image.fromarray(np.clip(col, 0, 255).astype(np.uint8).T[::-1]).resize((468, 468)).save(f'{OUT}/{sid}_prev.png')

if __name__ == '__main__':
    sys.path.insert(0, HERE); build(importlib.import_module('studies').STUDIES[sys.argv[1]])
