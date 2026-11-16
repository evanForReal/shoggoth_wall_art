#!/usr/bin/env python3
"""Full-piece COMPOSITION sculpt (914 x 914 mm, relief <= 300 mm). Composition-first, coarse voxel (default 2.0 mm).

Uses the locked Gate-2 vocabulary (Voronoi ribs + membranes + streamline ribs + sagged fibres + crevice shading +
flow-aligned grain) from ../gate2/gen_patch.py, scaled up ~4-5x. One parameter set -> every variant.

World frame (mm): wall plane z = 0 (flat back), +z leaves the wall, +y up, piece centre (0, 0).
Usage: python3 gen_fullpiece.py --variant hero --out DIR [--vox 2.0]
Variants: hero, v1_smiley, v2_nomaw, v3_diagonal, v4_shelvesB  (see VARIANTS)
Outputs: DIR/<variant>.npz (v, f after smoothing + grain), DIR/<variant>_meta.json (mask/shelf/engineering checks)
"""
import sys, os, json, time, argparse
import numpy as np
from scipy import ndimage as ndi, sparse
from scipy.spatial import cKDTree
from scipy.interpolate import CubicSpline

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'gate2'))
import gen_patch as gp                                     # locked vocabulary helpers

# ------------------------------- KNOBS (mm) --------------------------------
HALF = 457.0                  # domain half-size -> 914 mm
Z_MAX = 300.0
BODY = [((-95.0, 45.0), (235.0, 275.0), -18.0), ((120.0, -135.0), (175.0, 125.0), 14.0)]   # (centre, semi-axes, deg)
RELIEF = (16.0, 120.0)        # body relief height range (bas -> mid)
MASK_C, MASK_AB, MASK_DEG = (-105.0, 150.0), (70.0, 95.0), 10.0   # mask ellipse (centre, semi axes, rotation)
MAW_C, MAW_AB, MAW_DEG = (-92.0, -55.0), (92.0, 64.0), 6.0
BODY_DIAG = [((-70.0, 25.0), (330.0, 160.0), 38.0), ((150.0, -95.0), (210.0, 110.0), 30.0)]
BAYS = [((70.0, 95.0), (68.0, 40.0), 30.0), ((-165.0, -70.0), (58.0, 36.0), 50.0), ((125.0, -80.0), (50.0, 32.0), 20.0)]
SEEDS_R = (34.0, 64.0)        # Voronoi spacing radius range (hole-size gradient)
RIB_W = (9.0, 14.0)           # rib full width range before tail (mm)
RIB_TAIL = 8.0
WARP = (22.0, 260.0)
OPEN_P = (0.15, 0.50)
SKIN_T = 16.0
SL_COUNT = 70                 # streamline seeds
SHELF_W, PLATE_T = 190.0, 10.0
SHELF_ARR = {
    'A': [dict(side='L', ys=250.5, xc=-345.0, p=250.0), dict(side='R', ys=170.5, xc=345.0, p=200.0), dict(side='L', ys=-89.5, xc=-345.0, p=290.0)],
    'B': [dict(side='L', ys=120.5, xc=-345.0, p=210.0), dict(side='R', ys=290.5, xc=345.0, p=240.0), dict(side='R', ys=-129.5, xc=345.0, p=280.0)],
}
VARIANTS = {
    'hero':        dict(mask='serene', maw=True, layout='radial', shelves='A', seed=7),
    'v1_smiley':   dict(mask='smiley', maw=True, layout='radial', shelves='A', seed=7),
    'v2_nomaw':    dict(mask='serene', maw=False, layout='radial', shelves='A', seed=7),
    'v3_diagonal': dict(mask='serene', maw=True, layout='diagonal', shelves='A', seed=7),
    'v4_shelvesB': dict(mask='serene', maw=True, layout='radial', shelves='B', seed=7),
}
sstep = gp.smoothstep


def rot(x, y, c, deg):
    t = np.deg2rad(deg); dx, dy = x - c[0], y - c[1]
    return dx * np.cos(t) + dy * np.sin(t), -dx * np.sin(t) + dy * np.cos(t)


def ell_sd(x, y, c, ab, deg):
    u, v = rot(x, y, c, deg); a, b = ab
    q = np.sqrt((u / a) ** 2 + (v / b) ** 2) + 1e-9
    g = np.sqrt((u / a ** 2) ** 2 + (v / b ** 2) ** 2) / q + 1e-9
    return (q - 1) / g, q


def bend_curve(P, n_per_mm=0.5):
    P = np.asarray(P, float)
    s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
    sp = CubicSpline(s, P)
    S = np.arange(0, s[-1], 1.0 / n_per_mm * 0.5)
    return sp(S), S / s[-1]


def build_curves(pr, rng, shelves):
    """Return (curves list for FibreSet, polyline list for 2D mass, meta). curve = (pts3, radii)."""
    curves, lines2d, meta = [], [], dict(arms=[], whips=[])
    c0 = np.array([-60.0, 10.0])
    # arms to the shelves
    for k, sh in enumerate(shelves):
        sgn = -1.0 if sh['side'] == 'L' else 1.0
        inner = sh['xc'] + (95.0 if sh['side'] == 'L' else -95.0)
        R = np.array([inner + (14.0 if sh['side'] == 'L' else -14.0), sh['ys'] - 55.0])
        A = np.array([(-90.0 if sh['side'] == 'L' else 130.0), 0.55 * sh['ys'] + 15.0])
        d = R - A; nrm = np.array([-d[1], d[0]]) / np.linalg.norm(d)
        bulge = (60.0 if pr['layout'] == 'radial' else 35.0) * (1 if k % 2 == 0 else -1)
        P = np.array([A, A + 0.35 * d + nrm * bulge, A + 0.72 * d + nrm * bulge * 0.35, R])
        xy, t = bend_curve(P)
        r = 30.0 - 12.0 * t
        pts = np.column_stack([xy, 0.8 * r])
        curves.append((pts, r)); lines2d.append((xy, r * 1.0 + 38.0)); meta['arms'].append(dict(shelf=k, root=[float(R[0]), float(R[1])]))
    # whips
    if pr['layout'] == 'radial':
        specs = [(212, 520, 0.9), (246, 380, -0.8), (272, 500, 0.7), (306, 420, -0.9), (334, 560, 0.7), (38, 330, 0.9), (74, 220, -0.7), (112, 170, 0.8)]
    else:
        specs = [(30, 520, 0.9), (20, 470, -0.9), (46, 380, 0.8), (212, 540, -0.9), (226, 470, 0.9), (196, 400, -0.8), (60, 240, 0.7)]
    for (ang, L, bend) in specs:
        a = np.deg2rad(ang + rng.uniform(-6, 6))
        d0 = np.array([np.cos(a), np.sin(a)])
        start = c0 + d0 * rng.uniform(95, 140) + (np.array([100.0, -60.0]) if ang > 200 and ang < 330 else 0)
        n = 6; pts = [start]; th = a
        for i in range(n):
            th += bend * 0.55 * np.sin(i * 0.9 + rng.uniform(0, 3)) + bend * 0.20
            pts.append(pts[-1] + np.array([np.cos(th), np.sin(th)]) * L / n)
        P = np.array(pts)
        P[:, 0] = np.clip(P[:, 0], -425, 425); P[:, 1] = np.clip(P[:, 1], -425, 425)
        xy, t = bend_curve(P)
        r = 22.0 * (1 - t) ** 0.7 + 7.0
        pts3 = np.column_stack([xy, 0.8 * r])
        curves.append((pts3, r)); lines2d.append((xy, r * 1.8 + 22.0)); meta['whips'].append(dict(angle=ang, length=L))
    return curves, lines2d, meta


def shelf_fibres_full(rng, sh, n_f=20, n_l=14):
    """Fan of fibres from the plate rim back to the body root (scaled-up p07 root grip)."""
    xs0, xs1 = sh['xc'] - SHELF_W / 2, sh['xc'] + SHELF_W / 2
    ys0 = sh['ys'] - 4.0; p = sh['p']
    inner = sh['xc'] + (SHELF_W / 2 - 8 if sh['side'] == 'L' else -SHELF_W / 2 + 8)
    tot = (p - 40) + SHELF_W + (p - 40); curves, paths = [], []
    for i in range(n_f):
        q = (i + rng.uniform(0.15, 0.85)) / n_f * tot
        if q < p - 40: xR, zR = xs0 + 8, 40 + q
        elif q < p - 40 + SHELF_W: xR, zR = xs0 + 8 + (q - (p - 40)), p - 8
        else: xR, zR = xs1 - 8, p - 8 - (q - (p - 40) - SHELF_W)
        xT = inner + rng.uniform(-40, 40); zT = rng.uniform(8, 24); yT = sh['ys'] - rng.uniform(70, 175)
        P0 = np.array([xR, ys0, zR]); P3 = np.array([xT, yT, zT])
        C1 = np.array([xR + (xT - xR) * 0.12, ys0 - rng.uniform(30, 110), zR - (zR - zT) * 0.35])
        C2 = np.array([xT + rng.uniform(-25, 25), yT + rng.uniform(15, 55), zT + (zR - zT) * 0.40])
        n = int(np.linalg.norm(P3 - P0) / 1.2) + 20
        pts = gp.bez(P0, C1, C2, P3, n); t = np.linspace(0, 1, n)
        r0 = rng.uniform(3.4, 4.8); r1 = rng.uniform(5.5, 9.5) * (1.5 if rng.random() < 0.22 else 1.0)
        r = r0 + (r1 - r0) * sstep(t); curves.append((pts, r)); paths.append((pts, r))
    for _ in range(n_l):
        a = rng.integers(0, n_f - 1); b = min(n_f - 1, a + rng.integers(1, 3))
        ta = rng.uniform(0.3, 0.85); tb = float(np.clip(ta + rng.uniform(-0.15, 0.15), 0.2, 0.9))
        A = paths[a][0][int(ta * (len(paths[a][0]) - 1))]; B = paths[b][0][int(tb * (len(paths[b][0]) - 1))]
        mid = 0.5 * (A + B) + np.array([0, -rng.uniform(0.1, 0.25) * np.linalg.norm(B - A), 0])
        n = int(np.linalg.norm(B - A) / 1.2) + 12; t = np.linspace(0, 1, n)[:, None]
        pts = (1 - t) ** 2 * A + 2 * (1 - t) * t * mid + t ** 2 * B
        curves.append((pts, np.full(n, rng.uniform(3.2, 4.2))))
    return curves


def maw_teeth(rng, c, ab, deg):
    curves = []
    for k in range(22):
        up = k % 2 == 0
        ang = np.deg2rad(rng.uniform(25, 155) if up else rng.uniform(205, 335))
        u, v = ab[0] * 0.98 * np.cos(ang), ab[1] * 0.98 * np.sin(ang)
        t = np.deg2rad(deg); base = np.array([c[0] + u * np.cos(t) - v * np.sin(t), c[1] + u * np.sin(t) + v * np.cos(t)])
        tip = np.array(c) + (-np.sign(v)) * np.array([0, 1.0]) * rng.uniform(0.2, 0.6) * ab[1] + rng.uniform(-18, 18, 2) * [1, 0.2]
        mid = 0.5 * (base + tip) + rng.uniform(-8, 8, 2)
        P0 = np.array([base[0], base[1], 34.0]); P3 = np.array([tip[0], tip[1], 26.0 + rng.uniform(0, 14)])
        C = np.array([mid[0], mid[1], 20.0])
        n = int(np.linalg.norm(P3 - P0) / 1.2) + 10; tt = np.linspace(0, 1, n)[:, None]
        pts = (1 - tt) ** 2 * P0 + 2 * (1 - tt) * tt * C + tt ** 2 * P3
        r = 7.5 * (1 - tt[:, 0]) + 2.0
        curves.append((pts, r))
    return curves


def run(vname, vox, outdir):
    t0 = time.time()
    pr = dict(VARIANTS[vname]); rng = np.random.default_rng(pr['seed'])
    shelves = SHELF_ARR[pr['shelves']]
    gp.W_HALF_CAP = 20.0
    xs = np.arange(-HALF, HALF + 1e-6, vox); ys = np.arange(-HALF, HALF + 1e-6, vox); zs = np.arange(0, Z_MAX + 12, vox) + vox / 2
    nx, ny, nz = len(xs), len(ys), len(zs)
    print(vname, 'grid', nx, ny, nz, round(nx * ny * nz / 1e6, 1), 'M voxels', flush=True)
    X, Y = np.meshgrid(xs, ys, indexing='ij'); PTS = np.stack([X.ravel(), Y.ravel()], 1)
    N = {k: gp.Noise(rng, lam, lo=(-520, -520, -20), hi=(520, 520, 330)) for k, lam in
         dict(big_x=WARP[1], big_y=WARP[1], sm_x=110.0, sm_y=110.0, wob=45.0, hsel=300.0, hfine=110.0, sil=230.0, sil2=80.0,
              flow=420.0, rr=330.0, ovn=150.0, hf=24.0, rel=70.0, grn=60.0).items()}

    # ---------------- curves (arms, whips, strut, teeth) ----------------
    curves, lines2d, meta = build_curves(pr, rng, shelves)
    # buttress under the longest shelf
    ls = max(shelves, key=lambda s: s['p']); drop = min(300.0, ls['ys'] + 429.0)
    tip = np.array([ls['xc'], ls['ys'] - 12.0, ls['p'] - 18.0]); foot = np.array([ls['xc'] + (-40.0 if ls['side'] == 'L' else 40.0), ls['ys'] - drop, 14.0])
    mid = 0.5 * (tip + foot) + np.array([35.0 if ls['side'] == 'L' else -35.0, 0, 20.0])
    nS = int(np.linalg.norm(tip - foot) / 1.2) + 20
    strut = gp.bez(foot, foot + (mid - foot) * 0.8, tip + (mid - tip) * 0.8, tip, nS)
    meta['strut'] = dict(shelf_p=ls['p'], tip=tip.tolist(), foot=foot.tolist(), drop_mm=float(drop), radius=15.0)
    teeth = maw_teeth(rng, MAW_C, MAW_AB, MAW_DEG) if pr['maw'] else []
    limbs = gp.FibreSet(curves); strutset = gp.FibreSet([(strut, np.full(nS, 15.0))]); teethset = gp.FibreSet(teeth)
    sh_fib = [gp.FibreSet(shelf_fibres_full(np.random.default_rng(pr['seed'] + 200 + i), s)) for i, s in enumerate(shelves)]
    # 2D mass lines
    LP = np.concatenate([l[0] for l in lines2d]); LR = np.concatenate([np.full(len(l[0]), 0.0) + l[1] for l in lines2d])
    ltree = cKDTree(LP)

    bodies = BODY_DIAG if pr['layout'] == 'diagonal' else BODY

    def mass_sd(x, y):
        out = np.full(np.shape(x), 1e3)
        for c, ab, deg in bodies: out = np.minimum(out, ell_sd(x, y, c, ab, deg)[0])
        d, idx = ltree.query(np.stack([np.ravel(x), np.ravel(y)], 1), workers=4)
        out = np.minimum(out, (d - LR[idx]).reshape(np.shape(x)))
        return out + 22 * N['sil'](x, y, 0) + 9 * N['sil2'](x, y, 0) - 4
    M = mass_sd(X, Y)
    body_sd = np.min([ell_sd(X, Y, c, ab, deg)[0] for c, ab, deg in bodies], axis=0)
    # flow field
    if pr['layout'] == 'radial':
        flow_th = lambda x, y: np.arctan2(np.asarray(y) - 10.0, np.asarray(x) + 60.0) + np.deg2rad(32) + np.deg2rad(14) * N['flow'](x, y, 0)
    else:
        flow_th = lambda x, y: np.deg2rad(34 + 20 * sstep((np.asarray(y) + 300) / 600.0) - 10 * sstep((np.asarray(x) + 200) / 500.0) + 8 * N['flow'](x, y, 0))
    # relief
    h = RELIEF[0] + (RELIEF[1] - RELIEF[0]) * sstep(-body_sd / 150.0) * (0.75 + 0.25 * (0.5 + 0.5 * N['hsel'](X, Y, 0)))
    dl = ltree.query(PTS, workers=4)[0].reshape(X.shape)
    h = np.maximum(h, 18 + 10 * (0.5 + 0.5 * N['hfine'](X, Y, 0)))
    # bays
    bays = [(c, ab, deg, False) for c, ab, deg in BAYS]
    if pr['maw']: bays.append((MAW_C, MAW_AB, MAW_DEG, True))
    ov = np.full(X.shape, 1e3); ring = np.full(X.shape, 1e3)
    for c, ab, deg, is_maw in bays:
        s_, _ = ell_sd(X, Y, c, ab, deg); ov = np.minimum(ov, s_)
    ov = ov + 12 * N['ovn'](X, Y, 0) + 5 * N['hfine'](X, Y, 0)
    # mask ellipse
    mu, mv = rot(X, Y, MASK_C, MASK_DEG); mq = np.sqrt((mu / MASK_AB[0]) ** 2 + (mv / MASK_AB[1]) ** 2)
    meta['mask'] = dict(kind=pr['mask'], centre=MASK_C, semi=MASK_AB, deg=MASK_DEG)
    meta['maw'] = dict(present=bool(pr['maw']), centre=MAW_C, semi=MAW_AB, deg=MAW_DEG)

    # ---------------- web layer machinery ----------------
    s1 = gp.dart_seeds(rng, (-560, -560), (560, 560), lambda x, y: SEEDS_R[0] + (SEEDS_R[1] - SEEDS_R[0]) * sstep(0.5 + 0.4 * N['rr'](x, y, 0) + 0.25 * (x * 0.6 + y * 0.8) / 400.0),
                       flow_th, 1.3, ncand=60000)
    t1 = cKDTree(s1); nn1 = t1.query(s1, k=2)[0][:, 1]
    idx_ = np.arange(len(s1))
    hole_R = np.minimum(np.maximum(nn1 * (0.30 + 0.14 * gp.hash01(idx_, idx_, 31)), 12.0), 0.46 * nn1)
    th1 = flow_th(s1[:, 0], s1[:, 1])
    gseed = np.clip(0.5 + 0.4 * N['rr'](s1[:, 0], s1[:, 1], 0) + 0.25 * (s1[:, 0] * 0.6 + s1[:, 1] * 0.8) / 400.0, 0, 1)
    open1 = gp.hash01(idx_, idx_, 77) < (OPEN_P[0] + (OPEN_P[1] - OPEN_P[0]) * sstep(gseed))
    print('seeds', len(s1), round(time.time() - t0, 1), flush=True)

    keep1 = lambda x, y: mass_sd(x, y) < 0
    w1f = lambda a, b: gp.pair_attrs(s1, a, b, 1, RIB_W[0], RIB_W[1], 0.5, keep1, lambda x, y: 1.0, open1, RIB_TAIL)
    # streamlines
    def streamlines():
        P_all, W_all = [], []
        cand = np.column_stack([rng.uniform(-420, 420, 600), rng.uniform(-420, 420, 600)])
        cand = cand[mass_sd(cand[:, 0], cand[:, 1]) < -10][:SL_COUNT]
        for p0 in cand:
            for sgn in (1, -1):
                p = p0.copy(); pts = [p.copy()]
                for _ in range(90):
                    k1 = flow_th(p[0], p[1]); m = p + sgn * 2.0 * np.array([np.cos(k1), np.sin(k1)])
                    k2 = flow_th(m[0], m[1]); p = p + sgn * 4.0 * np.array([np.cos(k2), np.sin(k2)]); pts.append(p.copy())
                    if abs(p[0]) > 450 or abs(p[1]) > 450: break
                if sgn == 1: fwd = pts
                else: bwd = pts
            P = np.array(bwd[::-1] + fwd[1:])
            S_ = np.r_[0, np.cumsum(np.hypot(*np.diff(P, axis=0).T))]
            Sg = np.arange(0, S_[-1], 1.5)
            Q = np.column_stack([np.interp(Sg, S_, P[:, 0]), np.interp(Sg, S_, P[:, 1])])
            u = rng.random(); w0 = 3.8 + 6.5 * u ** 3
            env = 0.5 + 0.5 * np.sin(np.pi * np.clip(Sg / Sg[-1], 0, 1)) ** 0.5
            W = w0 * env
            for gl in rng.dirichlet(np.ones(3)) * 0.25 * Sg[-1]:
                g0 = rng.uniform(0, Sg[-1] - gl); W[(Sg >= g0) & (Sg <= g0 + gl)] = 0
            W[mass_sd(Q[:, 0], Q[:, 1]) > 0] = 0
            k = W > 0
            if k.sum() > 20: P_all.append(Q[k]); W_all.append(W[k])
        return np.concatenate(P_all), np.concatenate(W_all)
    SLP, SLW = streamlines(); sl = gp.StreamSet(SLP, SLW)
    print('streamline samples', len(SLP), round(time.time() - t0, 1), flush=True)

    def rib_sd(lat, w, ez, fl):
        sd = 0.4 * np.hypot(np.maximum(lat, 0), ez) + 0.6 * np.maximum(lat, ez) - w * fl
        return np.where(w > 0, sd, 9.0)

    def web_f(z):
        qx = X + WARP[0] * N['big_x'](X, Y, z * 0.3) + 6 * N['sm_x'](X, Y, z * 0.5)
        qy = Y + WARP[0] * N['big_y'](X, Y, z * 0.3) + 6 * N['sm_y'](X, Y, z * 0.5)
        wob = 1.4 * N['wob'](X, Y, z); hf = N['hf'](X, Y, z)
        fl = 1 + 0.18 * np.exp(-z / 20.0)
        prs = gp.net_layer(t1, s1, qx, qy, 0, w1f); d1p, i1p = gp.net_layer.last
        g = gp.grad_norm(prs[0][0], vox)
        front = np.full(X.shape, -9.0)
        for bis, w, kk in prs:
            w = w * (1 + 0.4 * N['wob'](X * 0.45, Y * 0.45, z * 0.3 + 40)); w = np.where(w > 0, np.maximum(w, 4.5), 0.0)
            lat = bis / g + wob + 0.5 * hf
            ez = np.maximum(z - (0.8 * h - w), 0)
            front = np.maximum(front, -rib_sd(lat, w, ez, fl))
        dS, wS = sl.field(PTS); dS = dS.reshape(X.shape); wS = np.where(wS.reshape(X.shape) > 0, wS.reshape(X.shape), 0.0)
        ezS = np.maximum(z - (h - wS), 0)
        front = np.maximum(front, -rib_sd(dS + wob + 0.5 * hf, wS, ezS, fl))
        # membrane skin
        dv = np.stack([qx, qy], -1) - s1[i1p]; ct, st = np.cos(th1[i1p]), np.sin(th1[i1p])
        al = (dv[..., 0] * ct + dv[..., 1] * st) / 1.5; pe = -dv[..., 0] * st + dv[..., 1] * ct
        dh = np.hypot(al, pe); dist_h = dh - hole_R[i1p]
        band = 1 - sstep(np.maximum(ov, 0) / 70.0)
        zsk = SKIN_T + 0.42 * h + 8 * N['wob'](X * 0.3, Y * 0.3, 0) + 30 * band ** 1.5
        lip = 8.0 + (zsk - 8.0) * sstep(dist_h / 8.0)
        f_sk = np.minimum(dist_h + wob + 3.0 * hf, lip - z)
        f_sk = np.where(open1[i1p] & (ov > 70.0), -9.0, f_sk)
        front = np.maximum(front, f_sk)
        front = np.minimum(front, -M)                      # confined to the mass
        front = np.minimum(front, ov)                      # bays carved
        # bay rims (broken)
        hr = 45 + 14 * N['hfine'](X, Y, 0)
        rimw = 7.0 * np.clip(0.55 + 1.0 * N['hfine'](X * 0.7, Y * 0.7, 3.0), 0, 1.6); rimw = np.where(rimw < 3.2, 0.0, rimw)
        rim = -rib_sd(np.abs(ov) + 0.5 * hf, rimw, np.maximum(z - (hr - 7.0), 0), fl)
        rim = np.minimum(rim, -M)
        return np.maximum(front, rim)

    # ---------------- fibres across the big voids ----------------
    gp.FIB_L = (70.0, 210.0); gp.FIB_R = (2.6, 3.6); gp.FIB_MIN_AREA = 2600.0; gp.FIB_AREA_PER = 6500.0
    gp.FIB_ZEND = (14.0, 26.0); gp.FIB_ZMIN = 6.0; gp.FIB_SAG = 0.07
    f0 = web_f(14.0)
    sil_ok = (M < -6) & (mq > 1.7)
    fib = gp.FibreSet(gp.web_fibres(np.random.default_rng(pr['seed'] + 101), f0, X, Y, vox, sil_ok, flow_th))
    print('web fibres', fib.n, round(time.time() - t0, 1), flush=True)

    # ---------------- mask skin (carved into the mass) ----------------
    def mask_top(Xg, Yg):
        u, v = rot(Xg, Yg, MASK_C, MASK_DEG); q = np.sqrt((u / MASK_AB[0]) ** 2 + (v / MASK_AB[1]) ** 2)
        un, vn = u / MASK_AB[0], v / MASK_AB[1]
        if pr['mask'] == 'serene':
            zf = 86.0 - 26.0 * q ** 2
            for sx in (-1, 1):                                    # closed eyes: shallow lidded hollows + brow
                e = ((un - sx * 0.40) / 0.30) ** 2 + ((vn - 0.20) / 0.13) ** 2
                zf -= 15.0 * np.exp(-e * 1.4)
                zf += 9.0 * np.exp(-(((un - sx * 0.42) / 0.36) ** 2 + ((vn - 0.38) / 0.07) ** 2))
            zf += 22.0 * np.exp(-((un / 0.10) ** 2 + ((vn + 0.10) / 0.42) ** 2))   # nose ridge
            zf -= 11.0 * np.exp(-((un / 0.30) ** 2 + ((vn + 0.58 + 0.12 * un ** 2) / 0.05) ** 2))   # mouth line (soft smile)
            zf += 3.0 * np.exp(-((un / 0.34) ** 2 + ((vn + 0.68) / 0.10) ** 2))
        else:
            zf = np.full(q.shape, 74.0)                            # flat graphic disc
            for sx in (-1, 1): zf -= 9.0 * (((un - sx * 0.36) / 0.10) ** 2 + ((vn - 0.22) / 0.075) ** 2 < 1)
            sm = np.abs(vn + 0.34 - 0.62 * (un / 0.62) ** 2) < 0.055   # smile: corners curve UP
            zf -= 9.0 * (sm & (np.abs(un) < 0.62))
        bez_ = 100.0 - 18.0 * sstep((q - 1.0) / 0.5)              # raised bezel ring around the recess
        top = np.where(q <= 1.0, zf, np.where(q <= 1.5, zf * 0 + (zf + (bez_ - zf) * sstep((q - 1.0) / 0.22)) * 1.0, bez_))
        top = np.where(q > 1.5, 0.0, top)
        f_mask = np.minimum(top, (1.62 - q) * 60.0)
        return top, f_mask
    top_xy, _ = mask_top(X, Y)

    # ---------------- assemble ----------------
    F = np.full((nx, ny, nz), -1.0, np.float32)
    zlim_web = int(np.searchsorted(zs, 128.0))
    zlim_limb = int(np.searchsorted(zs, 80.0))
    for k in range(zlim_web):
        z = zs[k]; f = web_f(z)
        if z < 36 and fib.n:
            P3 = np.concatenate([PTS, np.full((len(PTS), 1), z)], 1); f = np.maximum(f, fib.field(P3).reshape(X.shape))
        if teethset.n and z < 60:
            P3 = np.concatenate([PTS, np.full((len(PTS), 1), z)], 1); f = np.maximum(f, teethset.field(P3).reshape(X.shape))
        # limbs: arms, whips, strut (3D tubes with relief)
        if k < zlim_limb:
            P3 = np.concatenate([PTS, np.full((len(PTS), 1), z)], 1)
            lf = limbs.field(P3).reshape(X.shape)
            lf = lf + 3.5 * N['rel'](X, Y, z) * (lf > -6)
            f = np.maximum(f, lf)
        # mask skin: replace web inside the mask zone with solid face
        sk = np.minimum(top_xy - z, (1.62 - mq) * 60.0)
        f = np.where(mq < 1.62, np.where(mq > 1.45, np.maximum(f, sk), sk), f)
        F[:, :, k] = f
        if k % 15 == 0: print(' layer', k, round(z, 1), round(time.time() - t0, 1), flush=True)
    # ---------------- shelves ----------------
    shelf_meta = []
    for si, sh in enumerate(shelves):
        xs0, xs1 = sh['xc'] - SHELF_W / 2, sh['xc'] + SHELF_W / 2
        ix0 = int(np.searchsorted(xs, xs0 - 40)); ix1 = int(np.searchsorted(xs, xs1 + 40))
        sx, sz = np.meshgrid(xs[ix0:ix1], zs, indexing='ij')
        bump = np.clip(8 + 10 * N['wob'](sx, 0, sz), 0, 18)
        sdo = np.maximum.reduce([sx - xs1 - bump * 0.5, xs0 - bump * 0.5 - sx, sz - sh['p'] - bump * 0.5])
        # solid root block (cleat seat zone: 160 x 150, z 0..30), under the plate on the body side
        cx_seat = sh['xc'] + (50.0 if sh['side'] == 'L' else -50.0)
        j0 = int(np.searchsorted(ys, sh['ys'] - 330)); j1 = int(np.searchsorted(ys, sh['ys'] + 3))
        shf = sh_fib[si]
        for j in range(j0, j1):
            y = ys[j]; t = sh['ys'] - y
            fy = PLATE_T / 2 - np.abs(y - (sh['ys'] - PLATE_T / 2))
            f = np.minimum(fy, -sdo)
            if t >= 0:
                if t < 150.0:
                    seat = np.minimum.reduce([80.0 - np.abs(sx - cx_seat), np.full(sx.shape, 150.0 - t), 16.0 - sz, -sdo + 60])
                    f = np.maximum(f, seat)
                P3 = np.stack([sx.ravel(), np.full(sx.size, y), sz.ravel()], 1)
                f = np.maximum(f, np.minimum(shf.field(P3).reshape(sx.shape), -sdo + 10))
            F[ix0:ix1, j, :] = np.maximum(F[ix0:ix1, j, :], f.astype(np.float32))
        shelf_meta.append(dict(index=si, side=sh['side'], top_y=sh['ys'], p=sh['p'], width=SHELF_W, x_range=[xs0, xs1],
                               seat_zone=dict(centre_x=cx_seat, width=160.0, height=150.0, depth=16.0, y_range=[sh['ys'] - 150.0, sh['ys']])))
    meta['shelves'] = shelf_meta
    # buttress strut (all z) in a sub-window
    sx0 = float(strut[:, 0].min()) - 25; sx1 = float(strut[:, 0].max()) + 25; sy0 = float(strut[:, 1].min()) - 25; sy1 = float(strut[:, 1].max()) + 25
    i0, i1 = int(np.searchsorted(xs, sx0)), int(np.searchsorted(xs, sx1)); j0_, j1_ = int(np.searchsorted(ys, sy0)), int(np.searchsorted(ys, sy1))
    gx_, gy_ = np.meshgrid(xs[i0:i1], ys[j0_:j1_], indexing='ij'); pp = np.stack([gx_.ravel(), gy_.ravel()], 1)
    for k in range(nz):
        z = zs[k]
        if z > float(strut[:, 2].max()) + 20: break
        lf = strutset.field(np.concatenate([pp, np.full((len(pp), 1), z)], 1)).reshape(gx_.shape)
        lf = lf + 2.5 * N['rel'](gx_, gy_, z) * (lf > -5)
        F[i0:i1, j0_:j1_, k] = np.maximum(F[i0:i1, j0_:j1_, k], lf.astype(np.float32))
    # strut foot pad (50+ mm flat pad at wall datum)
    fx, fy_ = foot[0], foot[1]
    ix = (xs > fx - 32) & (xs < fx + 32); iy = (ys > fy_ - 32) & (ys < fy_ + 32)
    pad = np.minimum(np.minimum(32 - np.abs(xs[ix][:, None] - fx), 32 - np.abs(ys[iy][None, :] - fy_))[:, :, None], 12.0 - zs[None, None, :])
    sub = F[np.ix_(np.flatnonzero(ix), np.flatnonzero(iy), np.arange(nz))]
    F[np.ix_(np.flatnonzero(ix), np.flatnonzero(iy), np.arange(nz))] = np.maximum(sub, pad.astype(np.float32))
    meta['strut']['foot_pad_mm'] = 64.0
    print('field done', round(time.time() - t0, 1), flush=True)
    np.save(os.path.join(outdir, vname + '_flow.npy'), flow_th(X, Y).astype(np.float32))
    return F, xs, ys, zs, meta, t0


def taubin(v, A, dg, free, iters, lam=0.5, mu=-0.53):
    v = v.copy()
    for _ in range(iters):
        for k in (lam, mu):
            lap = (A @ v) / dg[:, None] - v; v[free] += k * lap[free]
    return v


def vnormals(v, f):
    fn = np.cross(v[f[:, 1]] - v[f[:, 0]], v[f[:, 2]] - v[f[:, 0]]); vn = np.zeros_like(v)
    for c in range(3):
        for k in range(3): vn[:, c] += np.bincount(f[:, k], weights=fn[:, c], minlength=len(v))
    return vn / (np.linalg.norm(vn, axis=1)[:, None] + 1e-12)


def grain_pass(v, f, flow_grid, xs0, vox, shelves, seed, mask=None):
    """Taubin smoothing + coarse flow-aligned ridged displacement (outward only); composition-scale stand-in for sculpt.py."""
    nv = len(v)
    e = np.concatenate([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]]); e = np.concatenate([e, e[:, ::-1]])
    A = sparse.csr_matrix((np.ones(len(e), np.float32), (e[:, 0], e[:, 1])), shape=(nv, nv)); A.data[:] = 1
    dg = np.asarray(A.sum(1)).ravel(); dg[dg == 0] = 1
    vn0 = vnormals(v, f)
    pin = v[:, 2] < 1.6
    for sh in shelves: pin |= (np.abs(v[:, 1] - sh['ys']) < 1.0) & (vn0[:, 1] > 0.9)
    v1 = taubin(v, A, dg, ~pin, 6)
    n1 = vnormals(v1, f)
    fx = (v1[:, 0] + HALF) / vox; fy = (v1[:, 1] + HALF) / vox
    th = ndi.map_coordinates(flow_grid.astype(np.float64), [np.clip(fx, 0, flow_grid.shape[0] - 1), np.clip(fy, 0, flow_grid.shape[1] - 1)], order=1)
    U = v1[:, 0] * np.cos(th) + v1[:, 1] * np.sin(th); W = -v1[:, 0] * np.sin(th) + v1[:, 1] * np.cos(th)
    rng = np.random.default_rng(seed + 5)
    a_ = ndi.gaussian_filter(rng.standard_normal((160, 160, 48)), 1.0, mode='wrap'); a_ /= a_.std()
    a_ = ndi.spline_filter(a_, order=3, mode='grid-wrap')
    ridge = np.zeros(nv); ws = 0
    for lu, lv, lz, wt in ((90.0, 12.0, 30.0, 0.8), (50.0, 6.5, 20.0, 1.0)):
        c = np.stack([U * 5 / lu + 40, W * 5 / lv + 70, v1[:, 2] * 5 / lz])
        nz_ = np.empty(nv)
        for s in range(0, nv, 1_000_000):
            nz_[s:s + 1_000_000] = ndi.map_coordinates(a_, c[:, s:s + 1_000_000], order=3, prefilter=False, mode='grid-wrap')
        ridge += wt * (1 - np.abs(np.clip(nz_ / 2.2, -1, 1))) ** 2; ws += wt
    ridge /= ws
    wr = sstep((v1[:, 2] - 22.0) / 25.0)
    amp = (1.1 + 1.9 * wr) * (~pin)
    if mask is not None:                                   # the carved mask is the one clean element: no grain, extra smoothing
        u_, w_ = rot(v1[:, 0], v1[:, 1], mask['centre'], mask['deg']); mqv = np.sqrt((u_ / mask['semi'][0]) ** 2 + (w_ / mask['semi'][1]) ** 2)
        amp = amp * sstep((mqv - 1.05) / 0.25)
    return v1 + n1 * (amp * ridge)[:, None], dict(disp_mean=float((amp * ridge).mean()), disp_max=float((amp * ridge).max()))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--variant', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--vox', type=float, default=2.0)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    F, xs, ys, zs, meta, t0 = run(a.variant, a.vox, a.out)
    v, f = gp.mesh_from_field(F, xs, ys, zs, a.vox)
    print('mc', v.shape, f.shape, round(time.time() - t0, 1), flush=True)
    vol = np.einsum('ij,ij->i', v[f[:, 0]], np.cross(v[f[:, 1]], v[f[:, 2]])).sum() / 6.0
    if vol < 0: f = f[:, [0, 2, 1]]          # outward-facing winding
    meta['volume_cm3_solid'] = round(abs(float(vol)) / 1000, 1); meta['mass_g_PETG_solid_upper_bound'] = round(abs(float(vol)) / 1000 * 1.27, 0)
    # engineering checks on the field/mesh
    shelves = SHELF_ARR[VARIANTS[a.variant]['shelves']]
    eng = {}
    flow = np.load(os.path.join(a.out, a.variant + '_flow.npy'))
    del F
    v2, gi = grain_pass(v.astype(np.float64), f.astype(np.int64), flow, xs[0], a.vox, shelves, VARIANTS[a.variant]['seed'], meta['mask'])
    meta['grain'] = gi
    eng['verts'] = int(len(v2)); eng['tris'] = int(len(f))
    eng['bbox_min_mm'] = [round(float(x), 1) for x in v2.min(0)]; eng['bbox_max_mm'] = [round(float(x), 1) for x in v2.max(0)]
    eng['bbox_size_mm'] = [round(float(x), 1) for x in (v2.max(0) - v2.min(0))]
    eng['bbox_within_914x914x300'] = bool(all(s <= lim + 1e-6 for s, lim in zip(eng['bbox_size_mm'], (914.0, 914.0, 300.0))))
    back = v2[v2[:, 2] < 3.0, 2]; eng['back_plane_z_range_mm'] = [round(float(back.min()), 2), round(float(back.max()), 2)]
    fn = vnormals(v2, f.astype(np.int64)); fc = v2[f].mean(1)
    fnt = np.cross(v2[f[:, 1]] - v2[f[:, 0]], v2[f[:, 2]] - v2[f[:, 0]]); area = 0.5 * np.linalg.norm(fnt, axis=1); nrm = fnt / (np.linalg.norm(fnt, axis=1)[:, None] + 1e-12)
    eng['shelf_flats'] = []
    for sh in shelves:
        sel = (nrm[:, 1] > 0.999) & (np.abs(fc[:, 1] - sh['ys']) < 0.8) & (fc[:, 0] > sh['xc'] - 95) & (fc[:, 0] < sh['xc'] + 95)
        pts = v2[np.unique(f[sel].ravel())] if sel.any() else np.zeros((0, 3))
        eng['shelf_flats'].append(dict(top_y=sh['ys'], p_mm=sh['p'], flat_area_cm2=round(float(area[sel].sum()) / 100, 1),
                                       flat_spread_mm=round(float(np.ptp(pts[:, 1])), 3) if len(pts) else None,
                                       footprint_nominal_mm=[SHELF_W, sh['p']], extent_z_mm=round(float(pts[:, 2].max()), 1) if len(pts) else None))
    meta['engineering'] = eng
    meta['variant'] = a.variant; meta['params'] = VARIANTS[a.variant]; meta['vox_mm'] = a.vox
    np.savez(os.path.join(a.out, a.variant + '.npz'), v=v2.astype(np.float32), f=f.astype(np.uint32))
    json.dump(meta, open(os.path.join(a.out, a.variant + '_meta.json'), 'w'), indent=1, default=lambda o: o.tolist() if hasattr(o, 'tolist') else str(o))
    print(json.dumps(eng, indent=1)); print('done', round(time.time() - t0, 1))
