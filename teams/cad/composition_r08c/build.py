#!/usr/bin/env python3
"""Build one r08 study: python3 build.py ID -> build/<id>.npz (mesh + labels), _meta.json, _sil/_solid/_body/_limbs, preview."""
import sys, os, json, importlib
import numpy as np
from scipy import ndimage as ndi
from skimage import measure
from PIL import Image, ImageDraw
from engine import *

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'build')
TH, RR = 34.0, 16.0

def plate_fn(cx, top, cz, a, b, seed):
    ph = np.random.default_rng(seed).uniform(0, 6.28, 4); cy = top - TH / 2
    def fn(X, Y, Z):
        dx, dz = X - cx, Z - cz; th = np.arctan2(dz, dx)
        sc = 1 + 0.09 * np.sin(2 * th + ph[0]) + 0.07 * np.sin(3 * th + ph[1]) + 0.04 * np.sin(5 * th + ph[2]) + 0.03 * np.sin(8 * th + ph[3])
        q = (np.abs(dx) / (a * sc)) ** 2.4 + (np.abs(dz) / (b * sc)) ** 2.4
        d2 = (q ** (1 / 2.4) - 1) * min(a, b) * 0.95 + RR; qn = np.clip(q ** (1 / 2.4), 0, 1)
        belly = 30.0 * (1 - qn ** 2) ** 0.8; dy = np.abs(Y - (cy - belly)) - (TH / 2 + belly)
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


def plate_rho(P, th):
    """planform radius of the plate boundary at angle th (matches plate_fn)."""
    ph = np.random.default_rng(P.get('seed', 1)).uniform(0, 6.28, 4); sc = 1 + 0.09 * np.sin(2 * th + ph[0]) + 0.07 * np.sin(3 * th + ph[1]) + 0.04 * np.sin(5 * th + ph[2]) + 0.03 * np.sin(8 * th + ph[3])
    a, b = P['a'], P['b']; return sc / ((np.abs(np.cos(th)) / a) ** 2.4 + (np.abs(np.sin(th)) / b) ** 2.4) ** (1 / 2.4)

def build(S):
    f = Field(); meta = dict(id=S['id'], name=S['name'], limbs=[], plates=[], webs=len(S['webs']), crown=0)
    sp4 = S['spine4']; rf, sp = spine_rfun(sp4); zsb = S.get('body_zs', 2.0)
    c, t, r, L = f.add_sweep('body', sp, rf, k=34, zs=zsb, kind=1)
    mw = S['maw']; mcx, mcy, mww, mhh = mw['c'][0], mw['c'][1], mw['w'], mw['h']
    sw = ellipsoid((mcx, mcy), mww / 2 + 44, mhh / 2 + 40, (30, 58))
    f.add_fn((mcx - mww / 2 - 120, mcy - mhh / 2 - 120, 0), (mcx + mww / 2 + 120, mcy + mhh / 2 + 120, 160), sw, k=40, kind=1)
    f.web_stats = []
    for T_ in S.get('tears', []): f.carve_tears(T_['poly'], T_['anchors'], holes=T_['holes'], hlen=T_['hlen'], asp=T_['asp'], rim=T_['rim'], seed=T_['seed'], minlig=T_['minlig'])
    # ---- strands: arms (shelf limbs), hanging cascade, crown
    zfix = {}
    for it in S['items']:
        nm = it['name']
        c, t, R, ln = f.add_bundle2(nm, it['pts'], it['R0'], n=it.get('n', 1), p=it.get('p', 0.75), r_tip=it.get('r_tip', 6.0), lump=it.get('lump', 0.14), twist=it.get('twist', 1.1), seed=it.get('seed', 0.0),
                                    nodes=it.get('nodes', 3), k=3.5 if it.get('n', 1) > 1 else 10.0, rngseed=sum(map(ord, nm)) % 997, spread=0.68, rs=0.35)
        if it.get('limb'):
            meta['limbs'].append(dict(name=nm, shelf=bool(it.get('shelf')), length=float(ln), r0=it['R0'], c=c[::8].tolist(), r=R[::8].tolist(), t=t[::8].tolist()))
        else: meta['crown'] += 1
        if it.get('shelf'):
            P = it['shelf']; fn = plate_fn(P['cx'], P['top'], P['cz'], P['a'], P['b'], P.get('seed', 1))
            lo = (P['cx'] - P['a'] * 1.3 - 30, P['top'] - TH - 60, 0); hi = (P['cx'] + P['a'] * 1.3 + 30, P['top'] + 20, P['cz'] + P['b'] * 1.3 + 30)
            f.add_fn(lo, hi, fn, k=22, kind=5)
            fa, fb = P['a'] * 1.4, P['b'] * 1.4
            f.carve((P['cx'] - fa, P['top'] - 0.0, P['cz'] - fb), (P['cx'] + fa, P['top'] + 60, P['cz'] + fb), lambda X, Y, Z, P_=P: -(Y - P_['top']))
            meta['plates'].append(dict(limb=nm, **{k_: P[k_] for k_ in ('cx', 'top', 'cz', 'a', 'b')}))
            # root fingers: grow from under the plate, grip the rim from outside (hugging the side wall), hook <= 6 mm over the top lip
            rng = np.random.default_rng(P.get('seed', 1) * 31 + 7); nf = it.get('fingers', 6)
            for j in range(nf):
                if j < nf - 2: th = np.radians(np.linspace(25, 155, nf - 2)[j] + rng.uniform(-9, 9))
                else: th = np.radians((180 if P['cx'] < 0 else 0) + rng.uniform(-38, 38))
                rho = plate_rho(P, th); ux, uz = np.cos(th), np.sin(th); ytop = P['top']; hgt = rng.uniform(0.55, 0.95)
                def pp(rr, yy): return (P['cx'] + rr * ux, yy, max(P['cz'] + rr * uz, 6.0))
                cl = [pp(0.55 * rho, ytop - TH - 34), pp(0.88 * rho, ytop - TH - 16), pp(rho + 5, ytop - TH * 0.7), pp(rho + 6, ytop - TH * (1 - hgt) - 4)]
                if hgt > 0.8: cl += [pp(rho - 3, ytop - 6.5), pp(rho - 16, ytop - 7.0)]
                cc, tt, _ = curve(cl, 1.5); f.sweep(f"{nm}.fing{j}", cc, 7.6 - 3.2 * tt, 4.0, store=False, kind=2)
    # ---- webs
    for i, W in enumerate(S['webs']):
        f.add_web2(W['poly'], W['anchors'], holes=W['holes'], hlen=W['hlen'], asp=W['asp'], th=W['th'], rim=W['rim'], seed=W['seed'], sag=0.2, minlig=11.0)
    # ---- vertical strand ribbing over the trunk (bark/sinew), flowing around the maw into the cascade
    for i, xy in enumerate(S.get('hair', [])): f.add_rib2(f'hair{i}', xy, n=1, amp=0.0, r0=(7.6 if i % 2 == 0 else 5.8), r1=4.8, lift=3.0, freq=1.0, seed=10 + i)
    # ---- jagged bone-edged maw rim: one continuous outer rib on the left, a broken one on the right, and splayed rib stubs (all ride the surface)
    ad0 = maw_sd(mw, S.get('seed', 0)); ths = np.linspace(-np.pi, np.pi, 90, endpoint=False); rim = []
    for th in ths:
        lo_, hi_ = 10.0, 260.0
        for _ in range(30):
            m_ = 0.5 * (lo_ + hi_); x_ = mcx + m_ * np.cos(th); y_ = mcy + m_ * np.sin(th)
            if ad0(np.array([x_]), np.array([y_]))[0] < 0: lo_ = m_
            else: hi_ = m_
        rim.append(lo_)
    rim = np.array(rim)
    def rim_pts(a0, a1, off, n=24):
        out = []
        for th in np.radians(np.linspace(a0, a1, n)):
            r_ = np.interp(th, ths, rim, period=2 * np.pi) + off; out.append((mcx + r_ * np.cos(th), mcy + r_ * np.sin(th)))
        return out
    f.add_rib2('maw_rib_L', rim_pts(280, 80 + 360 if False else 440, 15), n=1, amp=0.0, r0=9.0, r1=5.2, lift=3.0, freq=1.0) if False else None
    f.add_rib('maw_rib_L', rim_pts(-100, -260, 14), r0=9.0, r1=5.2, lift=3.0)
    f.add_rib('maw_rib_R', rim_pts(70, -30, 12), r0=8.0, r1=5.0, lift=3.0)
    rng_ = np.random.default_rng(S.get('seed', 0) + 41)
    for q, th in enumerate(np.radians(np.sort(rng_.uniform(-180, 180, 7)))):
        r_ = np.interp(th, ths, rim, period=2 * np.pi); tg_ = np.array([-np.sin(th), np.cos(th)]) * rng_.choice([-1, 1]); L_ = rng_.uniform(34, 72)
        p0 = np.array([mcx + (r_ + 6) * np.cos(th), mcy + (r_ + 6) * np.sin(th)]); p1 = p0 + (np.array([np.cos(th), np.sin(th)]) * 0.55 + tg_ * 0.8) * L_ * 0.5; p2 = p0 + (np.array([np.cos(th), np.sin(th)]) * 0.7 + tg_ * 0.7) * L_
        f.add_rib(f'maw_stub{q}', [tuple(p0), tuple(p1), tuple(p2)], r0=6.0, r1=3.2, lift=2.0, k=4.0)
    # ---- mask: seated disc + bezel, carved smiley
    mk = S['mask']; D = mk['D']; mrx = mry = D / 2; mcz = mk['z']; dzm = mk.get('dz', 26)
    def mfn(X, Y, Z):
        q = np.sqrt(((X - mk['c'][0]) / mrx) ** 2 + ((Y - mk['c'][1]) / mry) ** 2); h = 9.0 + (dzm - 9.0) * np.sqrt(np.clip(1 - q * q, 0, 1))
        return np.maximum((q - 1) * mrx, np.abs(Z - mcz) - h) * 0.9
    f.add_fn((mk['c'][0] - mrx - 20, mk['c'][1] - mry - 20, 0), (mk['c'][0] + mrx + 20, mk['c'][1] + mry + 20, 240), mfn, k=6, kind=6)
    # ---- flesh/root collar overlapping the mask rim (lower arc + sides); the crown tines swallow the top edge
    rngc = np.random.default_rng(S.get('seed', 0) + 77); angs = np.radians(np.linspace(-12, 192, 60)[::-1] * -1 + 0) if False else np.radians(np.linspace(192, 348, 60))
    rr = 97.0 + 3.0 * np.sin(5 * angs + 1.0) + 2.0 * np.sin(11 * angs); cc = np.stack([mk['c'][0] + rr * np.cos(angs), mk['c'][1] + rr * np.sin(angs), np.full(len(angs), mcz + 12.0) + 3 * np.sin(7 * angs)], 1)
    rc = 11.5 + 2.5 * np.sin(3 * angs + 0.5) + 1.5 * np.sin(9 * angs); tt = np.linspace(0, 1, len(angs)); rc = rc * (0.55 + 0.45 * np.sin(np.pi * tt) ** 0.6)
    f.sweep('collar', cc, np.maximum(rc, 4.5), 8.0, store=False, kind=2)
    fsd = mask_features(mk); fl = mcz + dzm - 11.0
    f.carve((mk['c'][0] - mrx, mk['c'][1] - mry, fl - 2), (mk['c'][0] + mrx, mk['c'][1] + mry, 300), lambda X, Y, Z: np.maximum(fsd(X, Y), fl - Z))
    # ---- maw: dark almond recess
    ad = maw_sd(mw, S.get('seed', 0)); ZR, SL, FLOOR = 110.0, 0.35, 12.0
    f.carve((mcx - mww / 2 - 20, mcy - mhh / 2 - 20, 0), (mcx + mww / 2 + 20, mcy + mhh / 2 + 20, 260), lambda X, Y, Z: np.maximum(ad(X, Y) + SL * np.clip(ZR - Z, 0, None), FLOOR - Z))
    F = f.finish(); sil = (F < 0).any(axis=2)
    v, fc, _, _ = measure.marching_cubes(F, 0.0, spacing=(RES,) * 3); v = v + np.array([XS[0], YS[0], ZS[0]])
    x, y, z = v[:, 0], v[:, 1], v[:, 2]
    ii = np.clip(((v - np.array([XS[0], YS[0], ZS[0]])) / RES).round().astype(int), 0, [NX - 1, NY - 1, NZ - 1])
    kind = f.K[ii[:, 0], ii[:, 1], ii[:, 2]]
    mk_v = mfn(x, y, z); dm = ad(x, y) + SL * np.clip(ZR - z, 0, None); fv = np.maximum(fsd(x, y), fl + 1.5 - z)
    meta.update(mask=dict(c=mk['c'], D=D, aspect=1.0), maw=dict(c=mw['c'], w=mw['w'], h=mw['h'], orient='v'), spine=dict(pts=[list(p) for p in sp.tolist()], zs=zsb), gesture=S['gesture'], web_stats=f.web_stats)
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
