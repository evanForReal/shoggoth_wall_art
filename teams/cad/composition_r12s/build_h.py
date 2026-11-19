#!/usr/bin/env python3
"""Build one r08 study: python3 build.py ID -> build/<id>.npz (mesh + labels), _meta.json, _sil/_solid/_body/_limbs, preview."""
import sys, os, json, importlib
import numpy as np
from scipy import ndimage as ndi
from skimage import measure
from PIL import Image, ImageDraw
from engine import *
import heldmask as hm
import trimesh

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

def sphere_fn(c, r):
    return lambda X, Y, Z: np.sqrt((X - c[0]) ** 2 + (Y - c[1]) ** 2 + (Z - c[2]) ** 2) - r

def add_eye(f, e, rng):
    """lidded eye in a flesh socket: collar mound, globe (kind 7), lid (ring / hood / turret), pupil recess when G >= 45."""
    x, y, G = e['x'], e['y'], e['G']; r = G / 2; zb = float(f.surface_z(np.array([x]), np.array([y]))[0]) if e.get('z') is None else e['z']
    if zb < 10: zb = 40.0
    zc = zb + (0.12 + e.get('pop', 0.0)) * r; lo = (x - 2.2 * r, y - 2.2 * r, 0); hi = (x + 2.2 * r, y + 2.2 * r, zc + 2.5 * r)
    f.add_fn(lo, hi, ellipsoid((x, y), 1.55 * r, 1.45 * r, (zb - 0.1 * r, 0.80 * r)), k=0.5 * r, kind=1)                # socket mound
    lid = e.get('lid', 'ring'); tilt = np.radians(e.get('tilt', 0.0)); ct, st = np.cos(tilt), np.sin(tilt)
    if lid == 'ring':
        def ringf(X, Y, Z):
            dx, dy, dz = X - x, Y - y, Z - zc; q = np.sqrt(dx ** 2 + dy ** 2); return np.sqrt((q - 1.08 * r) ** 2 + (dz - 0.05 * r) ** 2) - 0.24 * r * e.get('swell', 1.0)
        f.add_fn(lo, hi, ringf, k=0.2 * r, kind=1)
    elif lid == 'hood':
        def hoodf(X, Y, Z):
            dx, dy, dz = X - x, Y - y, Z - zc; u = ct * dx + st * dy; v_ = -st * dx + ct * dy; d = np.sqrt(dx ** 2 + dy ** 2 + dz ** 2)
            shell = np.abs(d - 1.10 * r) - 0.13 * r * e.get('swell', 1.0); cut = -(v_ - 0.05 * r); return np.maximum(shell, cut)
        f.add_fn(lo, hi, hoodf, k=0.15 * r, kind=1)
    elif lid == 'turret':
        f.add_fn(lo, hi, ellipsoid((x, y), 1.25 * r, 1.25 * r, (zb + 0.25 * r, 1.0 * r)), k=0.35 * r, kind=1)
    f.add_fn(lo, hi, sphere_fn((x, y, zc), r), k=1.0, kind=7)
    if e.get('pupil') in ('slit', 'round') and G >= 45:
        iris = 0.42 * G; ox, oy = e.get('gaze', (0, 0)); px_, py_ = x + ox * r, y + oy * r
        if e['pupil'] == 'slit': a_, b_ = 0.09 * iris, 0.62 * iris / 2 * 1.5
        else: a_ = b_ = 0.32 * iris
        def pit(X, Y, Z):
            ell = (np.sqrt(((X - px_) / a_) ** 2 + ((Y - py_) / b_) ** 2) - 1) * a_; dd = np.sqrt((X - x) ** 2 + (Y - y) ** 2); zf = zc + np.sqrt(np.clip(r * r - dd * dd, 0, None))
            return np.maximum(ell, (zf - 3.0) - Z)
        f.carve((x - r, y - r, zc - 2), (x + r, y + r, zc + r + 4), pit)

def add_tooth(f, base_pt, direc, L, bw, kind_broken, zdrop, curl, rng):
    """blade/needle tooth: tapered sweep from a root buried in the wall, leaning inward along `direc` (xy unit), tip drops by zdrop; base width bw >= 4, tip r >= 0.75, L <= 3 bw."""
    p0 = np.array([base_pt[0], base_pt[1], base_pt[2]]); d = np.array([direc[0], direc[1], 0.0]); nrm = np.array([-d[1], d[0], 0.0])
    pts = [p0 - d * 0.0, p0 + d * L * 0.35 + nrm * curl * 0.3 + [0, 0, -zdrop * 0.3], p0 + d * L * 0.7 + nrm * curl * 0.75 + [0, 0, -zdrop * 0.7], p0 + d * L + nrm * curl + [0, 0, -zdrop]]
    cc, tt, _ = curve([tuple(q) for q in pts], 1.2); tipr = 0.75 if not kind_broken else 0.28 * bw
    rr = (bw / 2) * (1 - tt) ** 0.9 + tipr * tt; rr = np.maximum(rr, tipr)
    if kind_broken: keep = tt <= 0.62; cc, rr = cc[keep], np.maximum(rr[keep], 0.30 * bw)
    f.sweep('tooth', cc, rr, 1.5, store=False, kind=8)

def add_hook_tooth(f, p0, inw, L, bw, rng, broken=False):
    """lamprey tooth: small cone rooted in the maw wall, pointing inward then hooking toward the throat floor; base width bw, tip r 0.75, L <= 3 bw."""
    d = np.array([inw[0], inw[1], 0.0]); p0 = np.array(p0, float) - d * 2.0
    pts = [p0, p0 + d * 0.45 * L + [0, 0, 0.06 * L], p0 + d * 0.85 * L + [0, 0, -0.18 * L], p0 + d * 1.0 * L + [0, 0, -0.55 * L]]
    cc, tt, _ = curve([tuple(q) for q in pts], 1.0); rr = np.maximum((bw / 2) * (1 - tt) ** 0.9 + 0.75 * tt, 0.75)
    if broken: keep = tt <= 0.6; cc, rr = cc[keep], np.maximum(rr[keep], 0.3 * bw)
    f.sweep('tooth', cc, rr, 1.2, store=False, kind=8)

def build(S):
    f = Field(); meta = dict(id=S['id'], name=S['name'], limbs=[], plates=[], webs=len(S['webs']), crown=0, eyes=[], teeth=0)
    sp4 = S['spine4']; rf, sp = spine_rfun(sp4); zsb = S.get('body_zs', 2.0)
    c, t, r, L = f.add_sweep('body', sp, rf, k=34, zs=zsb, kind=1)
    mw = S['maw']; mcx, mcy, mww, mhh = mw['c'][0], mw['c'][1], mw['w'], mw['h']
    sw = ellipsoid((mcx, mcy), mww / 2 + 44, mhh / 2 + 40, (30, 58))
    f.add_fn((mcx - mww / 2 - 120, mcy - mhh / 2 - 120, 0), (mcx + mww / 2 + 120, mcy + mhh / 2 + 120, 160), sw, k=40, kind=1)
    for B_ in S.get('bulges', []):         # flesh swellings (eye hosts / mask cradle)
        f.add_fn((B_['c'][0] - B_['a'] - 40, B_['c'][1] - B_['b'] - 40, 0), (B_['c'][0] + B_['a'] + 40, B_['c'][1] + B_['b'] + 40, 200), ellipsoid(B_['c'], B_['a'], B_['b'], (B_.get('z', 40), B_.get('h', 46))), k=34, kind=1)
    P_ = S['patch']; pc = P_['c']; prng = np.random.default_rng(S.get('seed', 0) + 555)      # r11: swollen diseased flesh patch where the mask used to sit (kind 10) + irregular lumps
    f.add_fn((pc[0] - P_['a'] - 40, pc[1] - P_['b'] - 40, 0), (pc[0] + P_['a'] + 40, pc[1] + P_['b'] + 40, 220), ellipsoid(pc, P_['a'], P_['b'], (P_['z'], P_['h'])), k=34, kind=10)
    for q_ in range(7):
        a_ = prng.uniform(0, 6.28); r_ = prng.uniform(25, 85); lx, ly = pc[0] + r_ * np.cos(a_), pc[1] + r_ * np.sin(a_); la = prng.uniform(16, 32)
        f.add_fn((lx - la - 30, ly - la - 30, 0), (lx + la + 30, ly + la + 30, 220), ellipsoid((lx, ly), la, la * prng.uniform(0.8, 1.2), (P_['z'] + 24, 26)), k=14, kind=10)
    f.web_stats = []
    for T_ in S.get('tears', []): f.carve_tears(T_['poly'], T_['anchors'], holes=T_['holes'], hlen=T_['hlen'], asp=T_['asp'], rim=T_['rim'], seed=T_['seed'], minlig=T_['minlig'])
    # ---- strands: arms (shelf limbs), hanging cascade, crown
    zfix = {}
    for it in S['items']:
        nm = it['name']
        if it.get('smooth'):      # single smooth tapering tentacle sweep (r09 style): T1 arms, T2 whip
            c, t, ln = curve(it['pts'], 1.5); R = tent_r(t, it['R0'], it.get('r_tip', 6.0), it.get('p', 0.6)); R = R * (1 + 0.035 * np.sin(7 * t + it.get('seed', 0)) + 0.02 * np.sin(19 * t)); R = np.maximum(R, it.get('r_tip', 6.0))
            f.sweep(nm, c, R, it.get('k', 16.0), kind=2); f.parts[nm] = dict(c=c, r=R)
        else:
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
    # ---- maw: dark almond recess
    ad = maw_sd(mw, S.get('seed', 0)); ZR, SL, FLOOR = 110.0, 0.35, 12.0
    f.carve((mcx - mww / 2 - 20, mcy - mhh / 2 - 20, 0), (mcx + mww / 2 + 20, mcy + mhh / 2 + 20, 260), lambda X, Y, Z: np.maximum(ad(X, Y) + SL * np.clip(ZR - Z, 0, None), FLOOR - Z))
    # ---- teeth (M1 / M2) and eyes (E1 / E2), added after the maw carve so surface z is known
    ths2 = np.linspace(-np.pi, np.pi, 120, endpoint=False); rim2 = []
    for th in ths2:
        lo_, hi_ = 10.0, 260.0
        for _ in range(30):
            m_ = 0.5 * (lo_ + hi_)
            if ad(np.array([mcx + m_ * np.cos(th)]), np.array([mcy + m_ * np.sin(th)]))[0] < 0: lo_ = m_
            else: hi_ = m_
        rim2.append(lo_)
    rim2 = np.array(rim2); rimr = lambda th: np.interp(th, ths2, rim2, period=2 * np.pi); trng = np.random.default_rng(S.get('seed', 1) + 900)
    tc = S.get('teeth_cfg'); lp = S.get('lamprey'); fang_lines = []
    if tc:      # M1: r09 S5/S6 fang set (34 front + 18 back, 5 long fangs 40-46 mm, ~15% broken), angled inward and down into the throat
        ntot = 0; nf, nb = tc['front'], tc['back']; fang_set = set(tc['fangs'])
        for row, n_ in ((0, nf), (1, nb)):
            angs_t = np.linspace(-180, 180, n_, endpoint=False) + trng.uniform(-3.5, 3.5, n_)
            for k_, a_deg in enumerate(angs_t):
                if tc.get('fangs_only') and not (row == 0 and k_ in fang_set): continue
                th = np.radians(a_deg); rr0 = rimr(th) - (11 if tc.get('fangs_only') else (6 if row == 0 else 30)); bx, by = mcx + rr0 * np.cos(th), mcy + rr0 * np.sin(th); is_f = row == 0 and k_ in fang_set
                if is_f: bw = trng.uniform(13, 15.5); Lt = min(3 * bw, trng.uniform(40, 46))
                else:
                    bw = trng.uniform(9, 14) * (0.8 if row else 1.0); Lt = min(bw * trng.uniform(2.0, 3.0), 3 * bw)
                    if abs(np.cos(th)) < 0.3: Lt *= 0.6
                dirv = -np.array([np.cos(th), np.sin(th)]) * 0.9 + np.array([-np.sin(th), np.cos(th)]) * trng.uniform(-0.3, 0.3); dirv /= np.linalg.norm(dirv)
                z0 = (66.0 if tc.get('fangs_only') else (70.0 if row == 0 else 54.0)) + trng.uniform(-3, 3)
                if is_f: fang_lines.append((np.array([bx, by]), np.array([bx, by]) + dirv * Lt))
                add_tooth(f, (bx, by, z0), dirv, Lt, bw, bool((not is_f) and trng.random() < 0.15), 0.5 * Lt + (6 if row else 0), trng.uniform(-6, 6), trng); ntot += 1
        meta['teeth'] = ntot
    if lp:      # M2: lamprey rings: concentric rows lining the whole rim, small hooked teeth rooted on the sloped wall (row z from the wall slope), pointing inward, tips hooked to the throat
        ntot = 0; thf = np.linspace(-np.pi, np.pi, 720, endpoint=False)
        for row, (ins, spc) in enumerate(zip(lp['inset'], lp['spacing'])):
            P_ = np.stack([mcx + (rimr(thf) - ins) * np.cos(thf), mcy + (rimr(thf) - ins) * np.sin(thf)], 1); seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(np.vstack([P_, P_[:1]]), axis=0), axis=1))]
            n_ = int(seg[-1] / spc); tg_ = (np.arange(n_) + 0.5 * (row % 2)) * seg[-1] / n_ + trng.uniform(-1.5, 1.5, n_); thk = np.interp(np.mod(tg_, seg[-1]), seg, np.r_[thf, np.pi])
            z0 = max(110.0 - 0.9 * ins / 0.35, 16.0)
            for th in thk:
                r_ = rimr(th) - ins; p0 = (mcx + r_ * np.cos(th), mcy + r_ * np.sin(th), z0); inw = -np.array([np.cos(th), np.sin(th)]) + np.array([-np.sin(th), np.cos(th)]) * trng.uniform(-0.25, 0.25); inw /= np.linalg.norm(inw)
                bw = trng.uniform(6.0, 8.0) * (1.0 - 0.07 * row); Lt = min(trng.uniform(10.0, 14.5) * (1.0 - 0.06 * row), 3 * bw)
                if any(np.linalg.norm(np.array(p0[:2]) - (a0 + np.clip(np.dot(np.array(p0[:2]) - a0, b0 - a0) / np.dot(b0 - a0, b0 - a0), 0, 1) * (b0 - a0))) < 11.0 for a0, b0 in fang_lines): continue
                add_hook_tooth(f, p0, inw, Lt, bw, trng, bool(trng.random() < 0.06)); ntot += 1
        meta['teeth'] = ntot
    for e in S.get('eyes', []):
        add_eye(f, e, trng); meta['eyes'].append(dict(x=e['x'], y=e['y'], G=e['G'], lid=e.get('lid', 'ring'), pupil=e.get('pupil', 'none'), clouded=bool(e.get('clouded')), gaze=e.get('gaze', (0, 0)), veiny=False, grp='e2'))
    # ================= r11 =================
    G = hm.geometry(f, S); vrng = np.random.default_rng(S.get('seed', 0) + 4242); veins = []; allg = []
    # ---- eye patch (6-12 eyes 15-50 mm) on the swollen flesh behind the mask
    pe = S['patch']['eyes']
    for e in pe:
        add_eye(f, e, trng); meta['eyes'].append(dict(x=e['x'], y=e['y'], G=e['G'], lid=e['lid'], pupil=e['pupil'], clouded=bool(e['clouded']), gaze=e['gaze'], veiny=True, grp='patch')); allg.append((e['x'], e['y'], e['G'], 'patch'))
    # ---- arm eyes (replace suckers): single row, inner face, 10-30 mm
    arm_eyes = []
    for it in S['items']:
        if not it.get('eyerow'): continue
        c, R = f.parts[it['name']]['c'], f.parts[it['name']]['r']; tg = np.gradient(c[:, :2], axis=0); tg /= np.linalg.norm(tg, axis=1)[:, None] + 1e-9; nr = np.stack([-tg[:, 1], tg[:, 0]], 1)
        cr = np.cross(np.r_[tg[len(tg) // 2], 0], np.r_[tg[min(len(tg) // 2 + 60, len(tg) - 1)], 0])[2]; side = 1 if cr > 0 else -1; ii_ = int(0.14 * (len(c) - 1)); iend = int(0.82 * (len(c) - 1)); placed = []
        while ii_ < iend and len(placed) < it['eyerow']:
            Ri = R[ii_]; Gd = float(np.clip(0.52 * Ri * vrng.uniform(0.8, 1.2), 10.0, 30.0)); xe, ye = c[ii_, :2] + nr[ii_] * side * 0.40 * Ri
            skip = it.get('shelf') and abs(xe - it['shelf']['cx']) < it['shelf']['a'] + 14 and it['shelf']['top'] - 80 < ye < it['shelf']['top'] + 10
            if Ri >= 14 and not skip:
                e = dict(x=float(xe), y=float(ye), G=round(Gd, 1), lid=['ring', 'hood', 'turret'][len(placed) % 3], pupil=['slit', 'round', 'none'][len(placed) % 3], clouded=bool(len(placed) % 4 == 3), tilt=float(vrng.uniform(-30, 30)),
                         gaze=(float(vrng.uniform(-.3, .3)), float(vrng.uniform(-.3, .3))), swell=float(vrng.uniform(1.2, 1.6)), pop=float(vrng.uniform(0.25, 0.45)), veiny=True)
                add_eye(f, e, trng); placed.append(e); meta['eyes'].append(dict(x=e['x'], y=e['y'], G=e['G'], lid=e['lid'], pupil=e['pupil'], clouded=e['clouded'], gaze=e['gaze'], veiny=True, grp='arm:' + it['name'])); allg.append((e['x'], e['y'], e['G'], 'arm'))
                ii_ += int(max(Gd * 1.05, 10) / 1.5)
            else: ii_ += int(10 / 1.5)
        arm_eyes.append(dict(arm=it['name'], n=len(placed), sizes=[e['G'] for e in placed], paths=(c, R)))
        for a_, b_ in zip(placed[:-1], placed[1:]): veins.append([(a_['x'], a_['y']), ((a_['x'] + b_['x']) / 2 + vrng.uniform(-3, 3), (a_['y'] + b_['y']) / 2 + vrng.uniform(-3, 3)), (b_['x'], b_['y'])])
    # ---- veins: shallow raised ridges (kind 9 = dark in render) radiating from each patch eye and linking neighbours
    pcen = np.array(S['patch']['c'])
    for (ex, ey, Gd, grp) in [g for g in allg if g[3] == 'patch']:
        for q in range(int(vrng.integers(3, 5))):
            ang = vrng.uniform(0, 6.283); p = np.array([ex, ey]) + (0.62 * Gd + 6) * np.array([np.cos(ang), np.sin(ang)]); pts = [tuple(p)]
            for st_ in range(int(vrng.integers(5, 9))):
                ang += vrng.normal(0, 0.28); p = p + 7.0 * np.array([np.cos(ang), np.sin(ang)])
                if np.linalg.norm(p - pcen) > 108 or any(np.hypot(p[0] - gx, p[1] - gy) < 0.62 * gG + 4 for gx, gy, gG, _ in allg if (gx, gy) != (ex, ey)): break
                pts.append(tuple(p))
            if len(pts) >= 4: veins.append(pts)
    pg = [g for g in allg if g[3] == 'patch']
    for i1 in range(len(pg)):
        for i2 in range(i1 + 1, len(pg)):
            a_, b_ = pg[i1], pg[i2]; dd = np.hypot(a_[0] - b_[0], a_[1] - b_[1])
            if dd < 0.5 * (a_[2] + b_[2]) * 1.35 + 14:
                u_ = np.array([b_[0] - a_[0], b_[1] - a_[1]]) / dd; nn = np.array([-u_[1], u_[0]]) * vrng.uniform(-5, 5)
                p0 = np.array(a_[:2]) + u_ * (0.62 * a_[2] + 3); p1 = np.array(b_[:2]) - u_ * (0.62 * b_[2] + 3)
                if np.linalg.norm(p1 - p0) > 6: veins.append([tuple(p0), tuple((p0 + p1) / 2 + nn), tuple(p1)])
    nv = 0; vh = []
    for k_, pts in enumerate(veins):
        if len(pts) == 3: pts = [pts[0], tuple(0.5 * (np.array(pts[0]) + pts[1])), pts[1], tuple(0.5 * (np.array(pts[1]) + pts[2])), pts[2]]
        if len(pts) < 4: continue
        cv_ = curve([(x_, y_, 0.0) for x_, y_ in pts], 2.0)[0]; z0_ = f.surface_z(cv_[:, 0], cv_[:, 1])
        f.add_rib(f'vein{k_}', pts, r0=3.2, r1=2.2, lift=1.8, k=2.5, kind=9, sig=3); nv += 1; vh.append(float(np.median(f.surface_z(cv_[:, 0], cv_[:, 1]) - z0_)))
    meta['veins'] = dict(n=nv, r0=3.2, r1=2.2, raised_mm_min=float(np.min(vh)), raised_mm_median=float(np.median(vh)), raised_mm_p10=float(np.percentile(vh, 10)))
    # ---- the held mask: rod-cored holding tentacle, root tendrils, pad, fingers, separate mask part
    mkc = dict(c=tuple(G['mc']), D=S['held']['D']); fsd0 = mask_features(mkc); _ct, _st = G['ct'], G['st']; _cx, _cy = G['mc']
    fsd = lambda X, Y: fsd0(_cx + _ct * (X - _cx) + _st * (Y - _cy), _cy - _st * (X - _cx) + _ct * (Y - _cy)); fl = G['zm'] + G['dz'] - 11.0
    mfn = hm.mask_sdf_fn(G); D = S['held']['D']; mk = dict(c=tuple(G['mc']), D=D)
    for j_, ang in enumerate((205, 250, 295, 340, 20, 160)):      # root tendrils: grip the trunk round the arm exit (visual), ride the surface
        th = np.radians(ang); p0 = np.array(G['Rx'][:2]) + 26 * np.array([np.cos(th), np.sin(th)]); L_ = vrng.uniform(60, 95); pts = [tuple(p0 + L_ * u * np.array([np.cos(th + 0.5 * np.sin(3 * u + j_)), np.sin(th + 0.5 * np.sin(3 * u + j_))])) for u in np.linspace(0, 1, 6)]
        f.add_rib(f'rtend{j_}', pts, r0=11.0, r1=4.5, lift=3.0, k=10.0, kind=2)
    Frest = f.F.copy(); Krest = f.K.copy() if False else None
    hm.add_arm(f, G, 'main'); fing = hm.add_mask(f, G, fsd, fl, 'main')
    hm.carve_bore(f, G, G['s_rod'])
    arm_c, arm_R, arm_sw = hm.sheath(G); f.parts['M_arm'] = dict(c=arm_c, r=arm_R)
    meta['limbs'].append(dict(name='M_arm', shelf=False, length=float(G['s_T'] - G['s_exit']), r0=float(arm_R.max()), c=arm_c[::8].tolist(), r=arm_R[::8].tolist(), t=np.linspace(0, 1, len(arm_c))[::8].tolist()))
    # isolated parts for export / review: arm part (arm + root block + column + plate + spigot) and mask part (disc + pad + fingers + socket + bore)
    fa = Field(); hm.add_arm(fa, G, 'arm'); hm.carve_bore(fa, G, G['s_T'] + hm.SPIG_L); Fa = fa.finish(); del fa
    fm = Field(); hm.add_mask(fm, G, fsd, fl, 'mask'); Fm = fm.finish(); del fm
    F = f.finish(); sil = (F < 0).any(axis=2)
    v, fc, _, _ = measure.marching_cubes(F, 0.0, spacing=(RES,) * 3); v = v + np.array([XS[0], YS[0], ZS[0]])
    x, y, z = v[:, 0], v[:, 1], v[:, 2]
    ii = np.clip(((v - np.array([XS[0], YS[0], ZS[0]])) / RES).round().astype(int), 0, [NX - 1, NY - 1, NZ - 1])
    kind = f.K[ii[:, 0], ii[:, 1], ii[:, 2]]
    mk_v = mfn(x, y, z); dm = ad(x, y) + SL * np.clip(ZR - z, 0, None); fv = np.maximum(fsd(x, y), fl + 1.5 - z)
    meta.update(mask=dict(c=list(mk['c']), D=D, aspect=1.0), held_geo={k_: (v_.tolist() if hasattr(v_, 'tolist') else v_) for k_, v_ in G.items() if k_ != 'H'}, held_in=S['held'], fingers=fing, arm_eyes=[{k_: v_ for k_, v_ in a_.items() if k_ != 'paths'} for a_ in arm_eyes], maw=dict(c=mw['c'], w=mw['w'], h=mw['h'], orient='v'), spine=dict(pts=[list(p) for p in sp.tolist()], zs=zsb), gesture=S['gesture'], web_stats=f.web_stats)
    os.makedirs(OUT, exist_ok=True); sid = S['id']
    np.savez_compressed(f'{OUT}/{sid}.npz', v=v.astype(np.float32), f=fc.astype(np.int32), mk=mk_v.astype(np.float32), dm=dm.astype(np.float32), fv=fv.astype(np.float32), kind=kind)
    np.save(f'{OUT}/{sid}_sil.npy', sil); np.save(f'{OUT}/{sid}_solid.npy', F < 0); np.save(f'{OUT}/{sid}_rest.npy', np.maximum(Frest, -ZS[None, None, :] + 1e-3) < 0); np.save(f'{OUT}/{sid}_armpart.npy', Fa < 0); np.save(f'{OUT}/{sid}_maskpart.npy', Fm < 0)
    for nm_, F_ in (('armpart', Fa), ('maskpart', Fm)):
        v_, f_, _, _ = measure.marching_cubes(F_, 0.0, spacing=(RES,) * 3); v_ = v_ + np.array([XS[0], YS[0], ZS[0]]); M_ = trimesh.Trimesh(v_, f_); bodies = [b_ for b_ in M_.split(only_watertight=False) if abs(b_.volume) > 1000.0]; M_ = trimesh.util.concatenate(bodies); M_.export(f'{OUT}/{sid}_{nm_}.stl'); meta.setdefault('stl', {})[nm_] = dict(bodies=len(bodies), watertight=bool(all(b_.is_watertight for b_ in bodies)), volume_cm3=round(sum(b_.volume for b_ in bodies) / 1e3, 1))
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
    json.dump(meta, open(f'{OUT}/{sid}_meta.json', 'w')); json.dump(meta['eyes'], open(f'{OUT}/{sid}_eyes.json', 'w')); print(sid, 'tris', len(fc), 'sil px', int(sil.sum()))
    inside = F < 0; zm = np.where(inside.any(2), ZS[inside.shape[2] - 1 - np.argmax(inside[:, :, ::-1], axis=2)], 0)
    gx, gy = np.gradient(zm, RES); sh = np.clip(0.6 + (gx * -0.6 + gy * 0.8) * 0.9, 0.1, 1.2)
    col = np.where(inside.any(2), 40 + 130 * sh * np.clip(0.5 + zm / 250, 0.4, 1), 12)
    Image.fromarray(np.clip(col, 0, 255).astype(np.uint8).T[::-1]).resize((468, 468)).save(f'{OUT}/{sid}_prev.png')

if __name__ == '__main__':
    sys.path.insert(0, HERE); build(importlib.import_module('studies').STUDIES[sys.argv[1]])
