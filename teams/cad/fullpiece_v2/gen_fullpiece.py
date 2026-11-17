#!/usr/bin/env python3
"""FULL-PIECE V2 composition sculpt (914 x 914 mm, relief <= 300 mm), 2.0 mm voxel.  Implements round-05 verdicts.

v2 vs v1 (fullpiece/): classic-smiley mask executed as weathered carved stone; gaping maw with asymmetric teeth;
muscular tapered tentacles (swells, overlaps, root fillets) incl. the buttress; eyes over the body; one masquerade device;
smooth muscle bellies between textured web zones; hard bbox clip; seat embed 28 mm; staggered shelf fans (headroom carve).
LOCKED from r05: shelf arrangement A + placement + flat tops, radial sprawl, Gate-2 texture (helpers from ../gate2/gen_patch.py).

World frame (mm): wall plane z = 0 (flat back), +z leaves the wall, +y up, piece centre (0, 0).
Usage: python3 gen_fullpiece.py --variant hero --out DIR [--vox 2.0]
"""
import sys, os, json, time, argparse
import numpy as np
from scipy import ndimage as ndi, sparse
from scipy.spatial import cKDTree
from scipy.interpolate import CubicSpline, PchipInterpolator

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'gate2'))
import gen_patch as gp                                     # locked vocabulary helpers

# ------------------------------- KNOBS (mm) --------------------------------
HALF = 457.0                  # domain half-size -> 914 mm
Z_MAX = 300.0
CLIP_XY = 454.0               # field hard clip (grain + vertex clamp finish at 457)
BODY = [((-95.0, 45.0), (235.0, 275.0), -18.0), ((120.0, -135.0), (175.0, 125.0), 14.0)]   # (centre, semi-axes, deg)
RELIEF = (16.0, 120.0)
MASK_C, MASK_R = (-105.0, 165.0), 92.0                 # circular emoticon face, radius
MAW_C, MAW_AB, MAW_DEG = (-95.0, -78.0), (118.0, 82.0), 6.0
BAYS = [((70.0, 95.0), (68.0, 40.0), 30.0), ((-20.0, -235.0), (60.0, 36.0), 50.0), ((125.0, -80.0), (50.0, 32.0), 20.0)]
# smooth muscle bellies: (centre, semi, deg, peak height)
BELLIES = [((-105.0, 165.0), (150.0, 150.0), 0.0, 64.0), ((45.0, 235.0), (95.0, 60.0), 20.0, 58.0),
           ((75.0, 20.0), (120.0, 62.0), 25.0, 80.0), ((150.0, -150.0), (140.0, 65.0), -22.0, 74.0),
           ((-200.0, -15.0), (52.0, 82.0), 80.0, 66.0), ((-80.0, -218.0), (125.0, 50.0), -8.0, 70.0),
           ((-215.0, 118.0), (50.0, 72.0), 15.0, 60.0)]
SEEDS_R = (34.0, 64.0)
RIB_W = (9.0, 14.0)
RIB_TAIL = 8.0
WARP = (22.0, 260.0)
OPEN_P = (0.15, 0.50)
SKIN_T = 16.0
SL_COUNT = 70
SHELF_W, PLATE_T = 190.0, 10.0
SEAT_DEPTH = 28.0
SHELF_ARR = {
    'A': [dict(side='L', ys=344.5, xc=-345.0, p=250.0), dict(side='R', ys=170.5, xc=345.0, p=200.0), dict(side='L', ys=-109.5, xc=-345.0, p=290.0)],
}
VARIANTS = {   # each differs from hero by ONE axis
    'hero':            dict(masq='fingers', eyes=26, maw_scale=1.0, teeth='mixed', weather=0.55, shelves='A', seed=7, whips=list(range(8)), whip_scale=1.0),
    'v1_liftedge':     dict(masq='lift', eyes=26, maw_scale=1.0, teeth='mixed', weather=0.55, shelves='A', seed=7, whips=list(range(8)), whip_scale=1.0),
    'v2_eyes_heavy':   dict(masq='fingers', eyes=40, maw_scale=1.0, teeth='mixed', weather=0.55, shelves='A', seed=7, whips=list(range(8)), whip_scale=1.0),
    'v3_maw_big':      dict(masq='fingers', eyes=26, maw_scale=1.28, teeth='fangs', weather=0.55, shelves='A', seed=7, whips=list(range(8)), whip_scale=1.0),
    'v4_weathered':    dict(masq='fingers', eyes=26, maw_scale=1.0, teeth='mixed', weather=1.0, shelves='A', seed=7, whips=list(range(8)), whip_scale=1.0),
    'v5_tentacles5':   dict(masq='fingers', eyes=26, maw_scale=1.0, teeth='mixed', weather=0.55, shelves='A', seed=7, whips=[0, 2, 4, 5, 7], whip_scale=1.3),
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


class DLimb:
    """One tapering limb with a D section: round front half (centre height zc), vertical flanks below it, flat back on the wall."""
    def __init__(self, pts3, r):
        self.xy = pts3[:, :2]; self.zc = np.append(pts3[:, 2], 0.0); self.r = np.append(r, 0.0)
        self.tree = cKDTree(self.xy); self.rmax = float(r.max())

    def field(self, P3):
        d, idx = self.tree.query(P3[:, :2], k=3, distance_upper_bound=self.rmax + 0.3, workers=4)
        dz = np.maximum(P3[:, 2:3] - self.zc[idx], 0.0)
        val = self.r[idx] - np.sqrt(np.where(np.isfinite(d), d, 0.0) ** 2 + dz ** 2)
        return np.where(np.isfinite(d), val, -9.0).max(axis=1)


def lse(a, b, k):
    return np.maximum(a, b) + k * np.log1p(np.exp(-np.abs(a - b) / k))


def bend_curve(P, n_per_mm=0.5):
    P = np.asarray(P, float)
    s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
    sp = CubicSpline(s, P)
    S = np.arange(0, s[-1], 1.0 / n_per_mm * 0.5)
    return sp(S), S / s[-1]


def tentacle(rng, start, ang, L, bend, r0, rtip, zoff, nsw, bendfrac=1.0):
    """Muscular tapering limb: peristaltic swells, centre z = zoff + 0.62 r (half-embedded on the wall)."""
    th = np.deg2rad(ang); pts = [np.array(start, float)]
    for i in range(6):
        th += bend * 0.55 * np.sin(i * 0.9 + rng.uniform(0, 3)) + bend * 0.20 * bendfrac
        pts.append(pts[-1] + np.array([np.cos(th), np.sin(th)]) * L / 6)
    P = np.clip(np.array(pts), -440, 440)
    xy, t = bend_curve(P)
    ph = rng.uniform(0, 6.28)
    r = ((r0 - rtip) * (1 - t) ** 0.8 + rtip) * (1 + 0.20 * np.sin(2 * np.pi * nsw * t + ph) * (0.4 + 0.6 * (1 - t)))
    return np.column_stack([xy, zoff + 0.30 * r]), r, xy, t


def build_limbs(pr, rng, shelves):
    """arms (to shelves) + radial whips as muscular tentacles. Returns curves, lines2d (mass), root bulbs, meta."""
    curves, lines2d, roots, meta = [], [], [], dict(arms=[], whips=[])
    c0 = np.array([-60.0, 10.0])
    for k, sh in enumerate(shelves):
        sgn = 1.0 if sh['side'] == 'L' else -1.0                       # direction toward the body
        inner = sh['xc'] + sgn * SHELF_W / 2                           # shelf footprint edge on the body side
        R = np.array([inner + sgn * 48.0, sh['ys'] - 62.0])            # arm ends under the seat zone, outside the headroom box
        A = np.array([(-90.0 if sh['side'] == 'L' else 130.0), 0.55 * sh['ys'] + 15.0])
        d = R - A; nrm = np.array([-d[1], d[0]]) / np.linalg.norm(d)
        bulge = 60.0 * (1 if k % 2 == 0 else -1)
        P = np.array([A, A + 0.35 * d + nrm * bulge, A + 0.72 * d + nrm * bulge * 0.35, R])
        xy, t = bend_curve(P)
        r = (42.0 - 16.0 * t) * (1 + 0.16 * np.sin(2 * np.pi * 1.5 * t + 0.6 * k))
        curves.append((np.column_stack([xy, 0.30 * r]), r)); lines2d.append((xy, r * 1.1 + 16.0 * (1 - t) ** 2))
        meta['arms'].append(dict(shelf=k, root=[float(R[0]), float(R[1])]))
    specs = [(212, 520, 0.9, 44, 0), (246, 380, -0.8, 40, 14), (272, 500, 0.7, 46, 6), (306, 420, -0.9, 40, 20),
             (334, 560, 0.7, 44, 0), (38, 330, 0.9, 36, 10), (74, 220, -0.7, 30, 4), (112, 170, 0.8, 26, 0)]
    for wi, (ang, L, bend, r0, zoff) in enumerate(specs):
        if wi not in pr['whips']: continue
        r0 = r0 * 0.9 * pr['whip_scale']; L = L * 1.2
        a = np.deg2rad(ang + rng.uniform(-6, 6)); d0 = np.array([np.cos(a), np.sin(a)])
        start = c0 + d0 * rng.uniform(95, 140) + (np.array([100.0, -60.0]) if 200 < ang < 330 else 0)
        pts3, r, xy, t = tentacle(rng, start, ang, L, bend, r0, 7.5, zoff, rng.uniform(2.6, 3.8))
        curves.append((pts3, r)); lines2d.append((xy, r * 1.1 + 18.0 * (1 - t) ** 2))
        roots.append((start - d0 * 0.2 * r0, r0)); meta['whips'].append(dict(angle=ang, length=L, r_root=r0))
    return curves, lines2d, roots, meta


def shelf_fibres_full(rng, sh, n_f=20, n_l=14):
    """Fan from the plate rim to the body root. Routing keeps every fibre within ~35 mm under the plate until it reaches
    the body-side footprint edge, so the fan does not hang into the headroom of a lower shelf at the same x."""
    xs0, xs1 = sh['xc'] - SHELF_W / 2, sh['xc'] + SHELF_W / 2
    ys0 = sh['ys'] - 4.0; p = sh['p']
    sgn = 1.0 if sh['side'] == 'L' else -1.0
    inner_edge = sh['xc'] + sgn * SHELF_W / 2
    tot = (p - 40) + SHELF_W + (p - 40); curves, paths = [], []
    for i in range(n_f):
        q = (i + rng.uniform(0.15, 0.85)) / n_f * tot
        if q < p - 40: xR, zR = xs0 + 8, 40 + q
        elif q < p - 40 + SHELF_W: xR, zR = xs0 + 8 + (q - (p - 40)), p - 8
        else: xR, zR = xs1 - 8, p - 8 - (q - (p - 40) - SHELF_W)
        xT = inner_edge + sgn * rng.uniform(6, 54); zT = rng.uniform(8, 28); yT = sh['ys'] - rng.uniform(85, 175)
        P0 = np.array([xR, ys0, zR])
        W1 = np.array([inner_edge - sgn * 4.0, sh['ys'] - rng.uniform(21, 30), zT + 0.35 * (zR - zT)])
        M = 0.5 * (P0 + W1) + np.array([0.0, -rng.uniform(-2, 5), 0.0])
        P3 = np.array([xT, yT, zT])
        Q = np.array([P0, M, W1, 0.5 * (W1 + P3) + np.array([sgn * 6.0, 0, 0]), P3])
        s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(Q, axis=0), axis=1))]
        pc = PchipInterpolator(s, Q, axis=0); n = int(s[-1] / 1.2) + 20
        pts = pc(np.linspace(0, s[-1], n)); t = np.linspace(0, 1, n)
        r0 = rng.uniform(3.4, 4.8); r1 = rng.uniform(5.5, 9.0) * (1.4 if rng.random() < 0.22 else 1.0)
        r = r0 + (r1 - r0) * sstep(t); curves.append((pts, r)); paths.append((pts, r))
    for _ in range(n_l):
        a = rng.integers(0, n_f - 1); b = min(n_f - 1, a + rng.integers(1, 3))
        ta = rng.uniform(0.3, 0.85); tb = float(np.clip(ta + rng.uniform(-0.15, 0.15), 0.2, 0.9))
        A = paths[a][0][int(ta * (len(paths[a][0]) - 1))]; B = paths[b][0][int(tb * (len(paths[b][0]) - 1))]
        mid = 0.5 * (A + B) + np.array([0, -rng.uniform(0.05, 0.12) * np.linalg.norm(B - A), 0])
        n = int(np.linalg.norm(B - A) / 1.2) + 12; t = np.linspace(0, 1, n)[:, None]
        pts = (1 - t) ** 2 * A + 2 * (1 - t) * t * mid + t ** 2 * B
        curves.append((pts, np.full(n, rng.uniform(3.2, 4.2))))
    return curves


def maw_teeth(rng, c, ab, deg, style):
    """Asymmetric snaggled teeth: varied length/thickness/angle, clumps and gaps, some broken. Roots sit in the lip crest."""
    curves, info = [], []
    t_ = np.deg2rad(deg); ct, st = np.cos(t_), np.sin(t_)
    def bp(angd, s=1.0):
        a = np.deg2rad(angd); u, v = ab[0] * s * np.cos(a), ab[1] * s * np.sin(a)
        return np.array([c[0] + u * ct - v * st, c[1] + u * st + v * ct])
    fangs = style == 'fangs'
    rows = [(np.linspace(18, 162, 12 if not fangs else 8), 'up'), (np.linspace(198, 342, 11 if not fangs else 7), 'lo')]
    plan = []
    for angs, nm in rows:
        a_ = angs + rng.uniform(-7, 7, len(angs))
        keep = rng.random(len(a_)) > 0.18                           # gaps
        plan += [(x, nm) for x, k in zip(a_, keep) if k]
    plan += [(rng.uniform(172, 188), 'side'), (rng.uniform(-6, 8), 'side')]        # corner tusks (asymmetric)
    plan += [(rng.uniform(60, 120), 'up'), (rng.uniform(240, 300), 'lo')] * (2 if not fangs else 1)  # second-rank snags
    ctr = np.array(c)
    for angd, nm in plan:
        base = bp(angd, 1.03); toc = ctr - base; dist = np.linalg.norm(toc)
        ya = np.deg2rad(rng.uniform(-38, 38)); R2 = np.array([[np.cos(ya), -np.sin(ya)], [np.sin(ya), np.cos(ya)]])
        u = R2 @ (toc / dist)
        if fangs: frac = rng.choice([rng.uniform(0.45, 0.80), rng.uniform(0.18, 0.35)], p=[0.55, 0.45])
        else: frac = rng.choice([rng.uniform(0.40, 0.62), rng.uniform(0.18, 0.38), rng.uniform(0.10, 0.20)], p=[0.35, 0.45, 0.20])
        L = frac * dist
        r0 = (7.5 + 0.13 * L + rng.uniform(0, 4.0)) * (1.25 if fangs else 1.0)
        L = min(L, 6.0 * r0)                                           # height <= 3 x base width (fab rule)
        z0 = 74.0 + rng.uniform(-6, 8); z1 = z0 - rng.uniform(0.10, 0.65) * L
        perp = np.array([-u[1], u[0]]) * rng.uniform(-0.28, 0.28) * L
        P0 = np.array([base[0], base[1], z0]); P2 = np.array([base[0] + u[0] * L, base[1] + u[1] * L, z1])
        Cc = 0.5 * (P0 + P2) + np.array([perp[0], perp[1], rng.uniform(-3, 8)])
        n = int(L / 1.2) + 10; tt = np.linspace(0, 1, n)[:, None]
        pts = (1 - tt) ** 2 * P0 + 2 * (1 - tt) * tt * Cc + tt ** 2 * P2
        broken = rng.random() < 0.30
        rtip = 2.8
        r = r0 * (1 - tt[:, 0]) ** 0.9 + rtip
        if broken:
            kcut = int(n * rng.uniform(0.50, 0.72)); pts, r = pts[:kcut], np.maximum(r[:kcut], 5.0)
        curves.append((pts, r)); info.append(dict(ang=float(angd), row=nm, length=float(L), r_base=float(r0), broken=bool(broken)))
    # sagging strands in the throat
    for _ in range(4):
        a1 = rng.uniform(50, 130); a2 = rng.uniform(230, 310)
        A_ = bp(a1, 0.9); B_ = bp(a2, 0.9); n = int(np.linalg.norm(A_ - B_) / 1.2) + 10; tt = np.linspace(0, 1, n)[:, None]
        A3 = np.array([A_[0], A_[1], 40.0]); B3 = np.array([B_[0], B_[1], 36.0]); mid = 0.5 * (A3 + B3) + np.array([rng.uniform(-18, 18), 0, 14.0])
        curves.append(((1 - tt) ** 2 * A3 + 2 * (1 - tt) * tt * mid + tt ** 2 * B3, np.full(n, 3.0)))
    return curves, info


def mask_top(Xg, Yg, N, W, masq, th0):
    """Classic smiley on a domed disc, carved & weathered. u,v in face radii. Returns top height map."""
    u = (Xg - MASK_C[0]) / MASK_R; v = (Yg - MASK_C[1]) / MASK_R
    q = np.hypot(u, v); th = np.arctan2(v, u)
    er1 = N['rel'](Xg, Yg, 5.0); er2 = N['hf'](Xg, Yg, 5.0); er3 = N['hfine'](Xg, Yg, 7.0)
    zf = 64.0 + 20.0 * (1 - np.minimum(q, 1.2) ** 2) + 4.0 * np.exp(-((u / 0.8) ** 2 + ((v - 0.35) / 0.25) ** 2))
    zf -= W * (3.5 * er1 + 1.6 * er2 + 1.2 * er3)                                   # erosion: sag + pitting
    zf -= W * 9.0 * sstep((-v - 0.10) / 0.8) * (0.6 + 0.4 * er3) * (1 + 0.5 * (u < 0))  # gravity slump, asymmetric (left worse)
    # crack (hairline, 5 mm wide) running from the lower-left rim up toward (but not into) the left eye
    cd = np.abs(0.62 * (u + 0.70) - 0.78 * (v + 0.50)) / 1.0 + 0.03 * er2
    zf -= W * 7.0 * (1 - sstep(cd / 0.030)) * ((u < -0.30) & (v < -0.18) & (q < 1.0)) * sstep((0.9 - q) / 0.05)
    for sx in (-1, 1):                                                              # counter-sunk vertical-oval eyes
        e = ((u - sx * 0.32) / 0.095) ** 2 + ((v - 0.20) / 0.19) ** 2
        zf -= 8.0 * sstep((1.9 - e) / 0.9) + 24.0 * sstep((1.0 - e) / 0.30)
    cy, rs = 0.14, 0.60                                                             # smile: true circular arc, V groove
    ang = np.arctan2(v - cy, u); a0, a1 = np.deg2rad(-152), np.deg2rad(-28)
    ac = np.clip(ang, a0, a1); d = np.hypot(u - rs * np.cos(ac), v - cy - rs * np.sin(ac))
    s = (ac - a0) / (a1 - a0)
    w = 0.115 * (0.70 + 0.30 * np.sin(np.pi * s) ** 0.7)                           # half-width 0.115 R = 10.6 mm
    zf -= 10.5 * (w / 0.115) * np.clip(1 - d / w, 0, 1)                             # true V, ~91 deg open (print rule), depth <= 3x width
    if masq == 'lift':                                                              # masquerade A: lower-right edge lifts off
        dth = np.abs(((th - th0 + np.pi) % (2 * np.pi)) - np.pi)
        lw = sstep(1 - dth / 0.85)
        zf += 17.0 * lw * sstep((q - 0.45) / 0.5)
    else: lw = np.zeros_like(q)
    edge = 0.96 + 0.015 * er3 * W
    crown = 106.0 - W * 16.0 * sstep(0.9 * er2 + 0.25) - W * 8.0 * sstep(er1)     # chipped bezel
    wall = sstep((q - edge) / 0.14)
    top_in = zf * (1 - wall) + crown * wall
    fall = sstep((q - 1.12) / 0.45)
    top = np.where(q < 1.12, top_in, crown * (1 - fall) + 68.0 * fall)
    return top, q, lw, th


def run(vname, vox, outdir):
    t0 = time.time()
    pr = dict(VARIANTS[vname]); rng = np.random.default_rng(pr['seed'])
    shelves = SHELF_ARR[pr['shelves']]; W = pr['weather']
    gp.W_HALF_CAP = 20.0
    xs = np.arange(-HALF, HALF + 1e-6, vox); ys = np.arange(-HALF, HALF + 1e-6, vox); zs = np.arange(0, Z_MAX + 12, vox) + vox / 2
    nx, ny, nz = len(xs), len(ys), len(zs)
    print(vname, 'grid', nx, ny, nz, round(nx * ny * nz / 1e6, 1), 'M voxels', flush=True)
    X, Y = np.meshgrid(xs, ys, indexing='ij'); PTS = np.stack([X.ravel(), Y.ravel()], 1)
    N = {k: gp.Noise(rng, lam, lo=(-520, -520, -20), hi=(520, 520, 330)) for k, lam in
         dict(big_x=WARP[1], big_y=WARP[1], sm_x=110.0, sm_y=110.0, wob=45.0, hsel=300.0, hfine=110.0, sil=230.0, sil2=80.0,
              flow=420.0, rr=330.0, ovn=150.0, hf=24.0, rel=70.0, grn=60.0).items()}
    meta = dict()
    # ---------------- limbs ----------------
    curves, lines2d, roots, meta0 = build_limbs(pr, rng, shelves); meta.update(meta0)
    # fingers (masquerade B): tendrils over the bezel from behind, tips pressed on the face rim
    fing = []
    if pr['masq'] == 'fingers':
        for angd in (22, 62, 112, 148, -22):
            a = np.deg2rad(angd + rng.uniform(-5, 5)); dvec = np.array([np.cos(a), np.sin(a)])
            Rm = MASK_R
            P0 = np.array(MASK_C) + dvec * Rm * 1.75; P3 = np.array(MASK_C) + dvec * Rm * 0.86
            Pm = np.array(MASK_C) + dvec * Rm * 1.30
            perp = np.array([-dvec[1], dvec[0]]) * rng.uniform(-20, 20)
            P = np.array([[P0[0], P0[1], 66.0], [Pm[0] + perp[0] * 1.5, Pm[1] + perp[1] * 1.5, 114.0],
                          [0.5 * (Pm + P3)[0] + perp[0] * 0.6, 0.5 * (Pm + P3)[1] + perp[1] * 0.6, 112.0], [P3[0], P3[1], 80.0]])
            s_ = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
            pts = PchipInterpolator(s_, P, axis=0)(np.linspace(0, s_[-1], int(s_[-1] / 1.2) + 10)); t = np.linspace(0, 1, len(pts))
            r = 13.0 * (1 - t) ** 0.7 + 5.5 + 2.0 * np.sin(2 * np.pi * 1.5 * t + angd)
            fing.append((pts, r)); roots.append((P0[:2], 13.0))
        meta['fingers'] = len(fing)
    # buttress: muscular limb from under the longest shelf to the wall foot pad
    ls = max(shelves, key=lambda s: s['p']); drop = min(300.0, ls['ys'] + 429.0); sg = 1.0 if ls['side'] == 'L' else -1.0
    tip = np.array([ls['xc'], ls['ys'] - 46.0, ls['p'] - 24.0]); foot = np.array([ls['xc'] - sg * 40.0, ls['ys'] - drop, 14.0])
    nS = int(np.linalg.norm(tip - foot) / 1.2) + 20; tS = np.linspace(0, 1, nS)
    off = np.stack([5.0 * np.sin(2 * np.pi * 1.5 * tS + 0.7) * np.sin(np.pi * tS) ** 0.5, 2.0 * np.sin(2 * np.pi * 1.0 * tS), 3.0 * np.sin(2 * np.pi * 1.2 * tS)], 1)
    strut = foot + (tip - foot) * tS[:, None] + off                   # limb centreline: straight core axis +- 5 mm sinuous
    s_r = 23.0 * (1 + 0.15 * np.sin(2 * np.pi * 2.5 * tS + 0.8)) + 9.0 * (1 - sstep(tS / 0.12)) + 11.0 * sstep((tS - 0.84) / 0.16)
    CORE_R = 11.0                                                      # embedded straight solid core, 22 mm (structural spec)
    PAD_HX, PAD_HY = 42.0, 33.0
    meta['strut'] = dict(shelf_p=ls['p'], tip=tip.tolist(), foot=foot.tolist(), drop_mm=float(drop), base_radius=23.0, core_dia_mm=2 * CORE_R, foot_pad_mm=[2 * PAD_HX, 2 * PAD_HY])
    teeth, tinfo = maw_teeth(rng, MAW_C, tuple(a * pr['maw_scale'] for a in MAW_AB), MAW_DEG, pr['teeth'])
    meta['teeth'] = tinfo
    limbs = [DLimb(c_[0], c_[1]) for c_ in curves]; fingset = gp.FibreSet(fing); strutset = gp.FibreSet([(strut, s_r)]); teethset = gp.FibreSet(teeth)
    sh_fib = [gp.FibreSet(shelf_fibres_full(np.random.default_rng(pr['seed'] + 200 + i), s)) for i, s in enumerate(shelves)]
    # 2D lines: web skirt + limb footprint (calm) + root bulbs
    LP = np.concatenate([l[0] for l in lines2d]); LR = np.concatenate([l[1] for l in lines2d]); ltree = cKDTree(LP)
    TP = np.concatenate([c[0][:, :2] for c in curves]); TR = np.concatenate([c[1] for c in curves]); ttree = cKDTree(TP)
    maw_ab = tuple(a * pr['maw_scale'] for a in MAW_AB)
    bodies = BODY
    mass_ells = [(c, ab, deg) for c, ab, deg in BODY] + [(c, ab, deg) for c, ab, deg, _ in BELLIES]
    mass_ells += [(tuple(rt[0]), (1.5 * rt[1], 1.2 * rt[1]), 0.0) for rt in roots]

    def mass_sd(x, y):
        out = np.full(np.shape(x), 1e3)
        for c, ab, deg in mass_ells: out = np.minimum(out, ell_sd(x, y, c, ab, deg)[0])
        d, idx = ltree.query(np.stack([np.ravel(x), np.ravel(y)], 1), workers=4)
        out = np.minimum(out, (d - LR[idx]).reshape(np.shape(x)))
        return out + 22 * N['sil'](x, y, 0) + 9 * N['sil2'](x, y, 0) - 4
    M = mass_sd(X, Y)
    body_sd = np.min([ell_sd(X, Y, c, ab, deg)[0] for c, ab, deg in bodies], axis=0)
    flow_th = lambda x, y: np.arctan2(np.asarray(y) - 10.0, np.asarray(x) + 60.0) + np.deg2rad(32) + np.deg2rad(14) * N['flow'](x, y, 0)
    h = RELIEF[0] + (RELIEF[1] - RELIEF[0]) * sstep(-body_sd / 150.0) * (0.75 + 0.25 * (0.5 + 0.5 * N['hsel'](X, Y, 0)))
    h = np.maximum(h, 18 + 10 * (0.5 + 0.5 * N['hfine'](X, Y, 0)))
    # muscle bellies (smooth solid) + limb calm
    Xw = X + 16 * N['ovn'](X, Y, 0); Yw = Y + 16 * N['hfine'](X, Y, 0)
    Hm = np.zeros(X.shape); calm = np.zeros(X.shape)
    for c, ab, deg, pk in BELLIES:
        uu, vv = rot(Xw, Yw, c, deg); qq = np.sqrt((uu / ab[0]) ** 2 + (vv / ab[1]) ** 2)
        Hm = np.maximum(Hm, pk * sstep((1 - qq) / 0.9)); calm = np.maximum(calm, sstep((1 - qq) / 0.45))
    Hm *= (0.92 + 0.08 * N['hsel'](X, Y, 0)) * 0.74
    for (rc, rr_) in roots:                                                       # root bulbs: tentacle roots fuse into the mass
        uu, vv = X - rc[0], Y - rc[1]; qq = np.sqrt(uu ** 2 + vv ** 2) / (1.5 * rr_)
        Hm = np.maximum(Hm, 0.95 * rr_ * sstep((1 - qq) / 0.85)); calm = np.maximum(calm, sstep((1 - qq) / 0.5))
    dT, iT = ttree.query(PTS, workers=4); dT = dT.reshape(X.shape); rT = TR[iT.reshape(X.shape)]
    calm_l = 1 - sstep((dT - 0.6 * rT) / (0.6 * rT)); calm = np.maximum(calm, calm_l)
    # maw 2D (irregular lip), floor
    ms = ell_sd(X, Y, MAW_C, maw_ab, MAW_DEG)[0] + 10 * N['ovn'](X, Y, 0) + 4.0 * N['hf'](X, Y, 0) + 5 * N['hfine'](X, Y, 0)
    Hc = 90.0 + 12 * N['hsel'](X, Y, 0) + 8.0 * sstep((MAW_C[1] - Y) / 60.0)       # lower lip heavier / sagging
    zr = Hc * np.sqrt(np.clip(1 - ((ms - 9.0) / 32.0) ** 2, 0, 1)); zr = np.where(ms < 41, zr, 0.0)
    zfloor = 9.0 + 10.0 * sstep((ms + 70.0) / 70.0) + 3 * N['hf'](X, Y, 0)
    calm = np.maximum(calm, np.where(ms > -8, sstep((58 - ms) / 40.0), 0.0))
    # bays
    ov = np.full(X.shape, 1e3)
    for c, ab, deg in BAYS: ov = np.minimum(ov, ell_sd(X, Y, c, ab, deg)[0])
    ov = ov + 12 * N['ovn'](X, Y, 0) + 5 * N['hfine'](X, Y, 0)
    # mask
    top_xy, mq, lw_xy, th_xy = mask_top(X, Y, N, W, pr['masq'], np.deg2rad(-50.0))
    meta['mask'] = dict(kind='classic_smiley', masquerade=pr['masq'], weather=W, centre=MASK_C, semi=(MASK_R, MASK_R), deg=0.0)
    meta['maw'] = dict(present=True, centre=MAW_C, semi=maw_ab, deg=MAW_DEG, floor_z_mm=[9.0, 19.0])
    # ---------------- web layer machinery (unchanged vocabulary) ----------------
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
            Wd = w0 * env
            for gl in rng.dirichlet(np.ones(3)) * 0.25 * Sg[-1]:
                g0 = rng.uniform(0, Sg[-1] - gl); Wd[(Sg >= g0) & (Sg <= g0 + gl)] = 0
            Wd[mass_sd(Q[:, 0], Q[:, 1]) > 0] = 0
            k = Wd > 0
            if k.sum() > 20: P_all.append(Q[k]); W_all.append(Wd[k])
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
        dv = np.stack([qx, qy], -1) - s1[i1p]; ct, st = np.cos(th1[i1p]), np.sin(th1[i1p])
        al = (dv[..., 0] * ct + dv[..., 1] * st) / 1.5; pe = -dv[..., 0] * st + dv[..., 1] * ct
        dh = np.hypot(al, pe); dist_h = dh - hole_R[i1p]
        band = 1 - sstep(np.maximum(ov, 0) / 70.0)
        zsk = SKIN_T + 0.42 * h + 8 * N['wob'](X * 0.3, Y * 0.3, 0) + 30 * band ** 1.5
        lip = 8.0 + (zsk - 8.0) * sstep(dist_h / 8.0)
        f_sk = np.minimum(dist_h + wob + 3.0 * hf, lip - z)
        f_sk = np.where(open1[i1p] & (ov > 70.0), -9.0, f_sk)
        front = np.maximum(front, f_sk)
        front = np.minimum(front, -M)
        front = np.minimum(front, ov)
        hr = 45 + 14 * N['hfine'](X, Y, 0)
        rimw = 7.0 * np.clip(0.55 + 1.0 * N['hfine'](X * 0.7, Y * 0.7, 3.0), 0, 1.6); rimw = np.where(rimw < 3.2, 0.0, rimw)
        rim = -rib_sd(np.abs(ov) + 0.5 * hf, rimw, np.maximum(z - (hr - 7.0), 0), fl)
        rim = np.minimum(rim, -M)
        f = np.maximum(front, rim)
        return np.minimum(f, 40.0 * (0.5 - calm))                                 # web only OUTSIDE the calm muscle zones

    def base_f(z, k):
        """web (gated) + belly mounds + muscular limbs with root fillets."""
        f = np.maximum(web_f(z), np.where(Hm > 0.5, Hm - z, -9.0))
        if k < zlim_limb:
            P3 = np.concatenate([PTS, np.full((len(PTS), 1), z)], 1)
            lf = np.max([L_.field(P3) for L_ in limbs], axis=0).reshape(X.shape)
            lf = lf + 4.0 * N['rel'](X, Y, z) * (lf > -6)
            near = (lf > -6) & (f > -6)
            f = np.where(near, lse(f, lf, 11.0), np.maximum(f, lf))
        return f

    zlim_web = int(np.searchsorted(zs, 128.0)); zlim_limb = int(np.searchsorted(zs, 120.0))
    # ---------------- fibres across the big voids ----------------
    gp.FIB_L = (70.0, 210.0); gp.FIB_R = (2.6, 3.6); gp.FIB_MIN_AREA = 2600.0; gp.FIB_AREA_PER = 6500.0
    gp.FIB_ZEND = (14.0, 26.0); gp.FIB_ZMIN = 6.0; gp.FIB_SAG = 0.07
    f0 = base_f(14.0, 0)
    sil_ok = (M < -6) & (mq > 1.7) & (ms > 14)
    fib = gp.FibreSet(gp.web_fibres(np.random.default_rng(pr['seed'] + 101), f0, X, Y, vox, sil_ok, flow_th))
    print('web fibres', fib.n, round(time.time() - t0, 1), flush=True)

    # slot behind lifted edge (masquerade A)
    slot_xy = None
    if pr['masq'] == 'lift':
        slot_xy = (lw_xy > 0.18) & (mq > 0.93) & (mq < 1.10)
        slot_under = (lw_xy > 0.18) & (mq > 0.85) & (mq <= 0.93)
        lift_fib = []
        for angd in (-62, -48, -34):
            a = np.deg2rad(angd); dv_ = np.array([np.cos(a), np.sin(a)])
            A_ = np.array(MASK_C) + dv_ * MASK_R * 1.18; B_ = np.array(MASK_C) + dv_ * MASK_R * 0.97
            n = 40; tt = np.linspace(0, 1, n)[:, None]
            P3 = np.concatenate([A_ * (1 - tt) + B_ * tt, 30.0 + 22.0 * tt], 1); lift_fib.append((P3, np.full(n, 3.4)))
        liftset = gp.FibreSet(lift_fib)

    # ---------------- assemble ----------------
    F = np.full((nx, ny, nz), -1.0, np.float32)
    outside = (np.abs(X) > CLIP_XY) | (np.abs(Y) > CLIP_XY)
    for k in range(zlim_web):
        z = zs[k]; f = base_f(z, k)
        P3 = None
        if z < 36 and fib.n:
            P3 = np.concatenate([PTS, np.full((len(PTS), 1), z)], 1); f = np.maximum(f, fib.field(P3).reshape(X.shape))
        # maw: lip ridge, void, floor, teeth
        f = np.maximum(f, zr - z)
        f = np.minimum(f, ms)
        f = np.maximum(f, np.minimum(zfloor - z, 4.0 - ms))
        if teethset.n and z < 100:
            P3 = np.concatenate([PTS, np.full((len(PTS), 1), z)], 1); f = np.maximum(f, teethset.field(P3).reshape(X.shape))
        # mask skin replaces the web inside the mask zone
        sk = np.minimum(top_xy - z, (1.62 - mq) * 60.0 * MASK_R / 100.0 * 1.0)
        f = np.where(mq < 1.62, np.where(mq > 1.45, np.maximum(f, sk), sk), f)
        if slot_xy is not None:
            carve = (slot_xy & (z > 18.0)) | (slot_under & (z > 18.0) & (z < 52.0))
            f = np.where(carve, -4.0, f)
            P3 = np.concatenate([PTS, np.full((len(PTS), 1), z)], 1); f = np.maximum(f, np.where(carve | (slot_xy & (z > 18.0)), liftset.field(P3).reshape(X.shape), -9.0))
        if fingset.n and z < 135:
            P3 = np.concatenate([PTS, np.full((len(PTS), 1), z)], 1); f = np.maximum(f, fingset.field(P3).reshape(X.shape))
        f = np.where(outside, -1.0, f)
        F[:, :, k] = f
        if k % 15 == 0: print(' layer', k, round(z, 1), round(time.time() - t0, 1), flush=True)
    # ---------------- headroom: 300 mm keep-out above each shelf footprint ----------------
    for sh in shelves:
        i0 = int(np.searchsorted(xs, sh['xc'] - SHELF_W / 2 - 4.0)); i1 = int(np.searchsorted(xs, sh['xc'] + SHELF_W / 2 + 4.0, side='right'))
        j0 = int(np.searchsorted(ys, sh['ys'])); j1 = int(np.searchsorted(ys, sh['ys'] + 304.0, side='right'))
        F[i0:i1, j0:j1, :] = -1.0
    # ---------------- eyes ----------------
    eyes = place_and_apply_eyes(rng, F, xs, ys, zs, vox, pr['eyes'], X, Y, mq, ms, shelves, vox, curves[:len(shelves)])
    meta['eyes'] = [{k_: (round(float(v_), 1) if not isinstance(v_, str) else v_) for k_, v_ in e.items()} for e in eyes]
    print('eyes', len(eyes), round(time.time() - t0, 1), flush=True)
    # ---------------- shelves ----------------
    shelf_meta = []
    for si, sh in enumerate(shelves):
        xs0, xs1 = sh['xc'] - SHELF_W / 2, sh['xc'] + SHELF_W / 2
        ix0 = int(np.searchsorted(xs, xs0 - 40)); ix1 = int(np.searchsorted(xs, xs1 + 40))
        sx, sz = np.meshgrid(xs[ix0:ix1], zs, indexing='ij')
        bump = np.clip(8 + 10 * N['wob'](sx, 0, sz), 0, 18)
        sdo = np.maximum.reduce([sx - xs1 - bump * 0.5, xs0 - bump * 0.5 - sx, sz - sh['p'] - bump * 0.5])
        cx_seat = sh['xc'] + (50.0 if sh['side'] == 'L' else -50.0)
        j0 = int(np.searchsorted(ys, sh['ys'] - 330)); j1 = int(np.searchsorted(ys, sh['ys'] + 3))
        shf = sh_fib[si]
        for j in range(j0, j1):
            y = ys[j]; t = sh['ys'] - y
            fy = PLATE_T / 2 - np.abs(y - (sh['ys'] - PLATE_T / 2))
            f = np.minimum(fy, -sdo)
            if t >= 0:
                if t < 150.0:
                    seat = np.minimum.reduce([80.0 - np.abs(sx - cx_seat), np.full(sx.shape, 150.0 - t), SEAT_DEPTH - sz, -sdo + 60])
                    f = np.maximum(f, seat)
                P3 = np.stack([sx.ravel(), np.full(sx.size, y), sz.ravel()], 1)
                f = np.maximum(f, np.minimum(shf.field(P3).reshape(sx.shape), -sdo + 10))
            F[ix0:ix1, j, :] = np.maximum(F[ix0:ix1, j, :], f.astype(np.float32))
        shelf_meta.append(dict(index=si, side=sh['side'], top_y=sh['ys'], p=sh['p'], width=SHELF_W, x_range=[xs0, xs1],
                               seat_zone=dict(centre_x=cx_seat, width=160.0, height=150.0, depth=SEAT_DEPTH, y_range=[sh['ys'] - 150.0, sh['ys']])))
    meta['shelves'] = shelf_meta
    # ---------------- buttress limb + foot pad ----------------
    sx0 = float(strut[:, 0].min()) - 45; sx1 = float(strut[:, 0].max()) + 45; sy0 = float(strut[:, 1].min()) - 45; sy1 = float(strut[:, 1].max()) + 45
    i0, i1 = int(np.searchsorted(xs, sx0)), int(np.searchsorted(xs, sx1)); j0_, j1_ = int(np.searchsorted(ys, sy0)), int(np.searchsorted(ys, sy1))
    gx_, gy_ = np.meshgrid(xs[i0:i1], ys[j0_:j1_], indexing='ij'); pp = np.stack([gx_.ravel(), gy_.ravel()], 1)
    for k in range(nz):
        z = zs[k]
        if z > float(strut[:, 2].max()) + 30: break
        lf = strutset.field(np.concatenate([pp, np.full((len(pp), 1), z)], 1)).reshape(gx_.shape)
        lf = lf + 1.5 * N['rel'](gx_, gy_, z) * (lf > -5)
        qx_, qy_ = np.abs(gx_ - foot[0]) - (PAD_HX - 8.0), np.abs(gy_ - foot[1]) - (PAD_HY - 8.0)
        sdp = np.hypot(np.maximum(qx_, 0), np.maximum(qy_, 0)) + np.minimum(np.maximum(qx_, qy_), 0) - 8.0
        padf = np.minimum(-sdp, 12.0 - z)
        lf = lse(lf, padf, 6.0) if z < 30 else lf
        ab_ = tip - foot; tt_ = np.clip(((gx_ - foot[0]) * ab_[0] + (gy_ - foot[1]) * ab_[1] + (z - foot[2]) * ab_[2]) / (ab_ @ ab_), 0, 1)
        dcore = np.sqrt((gx_ - foot[0] - tt_ * ab_[0]) ** 2 + (gy_ - foot[1] - tt_ * ab_[1]) ** 2 + (z - foot[2] - tt_ * ab_[2]) ** 2)
        lf = np.maximum(lf, CORE_R - dcore)
        F[i0:i1, j0_:j1_, k] = np.maximum(F[i0:i1, j0_:j1_, k], lf.astype(np.float32))
        print('field done', round(time.time() - t0, 1), flush=True)
    np.save(os.path.join(outdir, vname + '_flow.npy'), flow_th(X, Y).astype(np.float32))
    aux = dict(calm=calm.astype(np.float32), maw_sd=ms.astype(np.float32), mq=mq.astype(np.float32))
    return F, xs, ys, zs, meta, t0, aux, eyes, teethset, (strut, s_r), curves


def place_and_apply_eyes(rng, F, xs, ys, zs, vox, n_eyes, X, Y, mq, ms, shelves, v_, arm_curves=()):
    solid = F > 0
    fe = np.argmin(solid, axis=2); fe = np.where(solid.all(axis=2), solid.shape[2], fe); fe = np.where(solid[:, :, 0], fe, 0)
    ztop = fe * vox; del solid
    slope = np.hypot(*np.gradient(ndi.gaussian_filter(ztop, 1.2), vox))      # eyes only on faces within ~45 deg of facing out
    ok = (mq > 2.4) & (ms > 55.0) & (np.abs(X) < 430) & (np.abs(Y) < 430)
    for sh in shelves:
        cxs = sh['xc'] + (50.0 if sh['side'] == 'L' else -50.0)       # no eyes in seat block + 100 mm, or on the plate
        ok &= ~((np.abs(X - cxs) < 180.0) & (Y > sh['ys'] - 250) & (Y < sh['ys'] + 310))
        ok &= ~((np.abs(X - sh['xc']) < SHELF_W / 2 + 20) & (Y > sh['ys'] - 340) & (Y < sh['ys'] + 310))
    for c_ in arm_curves:                                              # no eyes on shelf-arm roots (+30 mm)
        dd_, _ = cKDTree(c_[0][:, :2]).query(np.stack([X.ravel(), Y.ravel()], 1)); ok &= ~(dd_.reshape(X.shape) < c_[1].max() + 30.0)
    cand = ok & (ztop >= 26) & (ztop <= 118)
    ci = np.argwhere(cand)
    print('eye candidates', len(ci), flush=True)
    if len(ci) == 0: return []
    placed = []
    def try_place(i, j, R, sp=1.15, smax=1.0, zmin=20.0):
        pad = int(1.25 * R / vox) + 1
        i0, i1, j0, j1 = max(i - pad, 0), min(i + pad + 1, ztop.shape[0]), max(j - pad, 0), min(j + pad + 1, ztop.shape[1])
        gi, gj = np.meshgrid(np.arange(i0, i1), np.arange(j0, j1), indexing='ij')
        dm = np.hypot((gi - i) * vox, (gj - j) * vox) <= 1.25 * R
        sub = ztop[i0:i1, j0:j1][dm]
        if sub.min() < zmin or (sub.max() - sub.min()) > 0.9 * R + 12 or slope[i0:i1, j0:j1][dm].max() > smax or not ok[i0:i1, j0:j1][dm].all(): return False
        x, y = xs[i], ys[j]
        for e in placed:
            if np.hypot(e['x'] - x, e['y'] - y) < sp * (e['R'] + R) + 2: return False
        zb = float(np.median(sub))
        placed.append(dict(x=float(x), y=float(y), R=float(R), zb=zb, lid_ang=float(rng.uniform(55, 125) if rng.random() < 0.7 else rng.uniform(-40, 220)),
                           cover=float(rng.choice([0.0, 0.0, 0.28, 0.45, 0.62, 0.78])), bag=float(rng.uniform(0.0, 0.32)),
                           gaze=float(rng.uniform(-0.8, 0.8)), phi=float(rng.uniform(0.12, 0.38))))
        return True
    n_cl = max(2, n_eyes // 6); n_in_clusters = int(0.68 * n_eyes)
    for c in range(n_cl):
        for _ in range(200):
            i, j = ci[rng.integers(len(ci))]
            if try_place(i, j, rng.uniform(15.0, 22.5)): break
        else: continue
        cx, cy = placed[-1]['x'], placed[-1]['y']; want = int(n_in_clusters / n_cl) - 1
        got = 0
        for _ in range(300):
            if got >= want: break
            px, py = cx + rng.normal(0, 46), cy + rng.normal(0, 46)
            i, j = int(round((px + HALF) / vox)), int(round((py + HALF) / vox))
            if 0 <= i < ztop.shape[0] and 0 <= j < ztop.shape[1] and cand[i, j] and try_place(i, j, rng.uniform(9.0, 16.0)): got += 1
    for _ in range(20000):
        if len(placed) >= n_eyes: break
        i, j = ci[rng.integers(len(ci))]
        try_place(i, j, rng.uniform(10.0, 19.0))
    for _ in range(40000):                                             # dense fill (heavy variants): smaller eyes, tighter packing, still on out-facing faces (slope <= 1.0)
        if len(placed) >= n_eyes: break
        i, j = ci[rng.integers(len(ci))]
        try_place(i, j, rng.uniform(9.0, 13.0), sp=0.95, smax=1.0, zmin=18.0)
    for e in placed: apply_eye(F, xs, ys, zs, vox, e)
    return placed


def apply_eye(F, xs, ys, zs, vox, e):
    """Lidded hemispherical bulge with iris recess; upper lid covers `cover` of the ball, lower bag; centre slightly below surface."""
    R = e['R']; Rb = 1.12 * R; zc = e['zb'] - 0.22 * R; ext = 1.5 * Rb + 4
    i0, i1 = int(np.searchsorted(xs, e['x'] - ext)), int(np.searchsorted(xs, e['x'] + ext))
    j0, j1 = int(np.searchsorted(ys, e['y'] - ext)), int(np.searchsorted(ys, e['y'] + ext))
    k0 = max(0, int((e['zb'] - 0.6 * R) / vox)); k1 = min(len(zs), int((zc + Rb + 8) / vox) + 1)
    gx, gy, gz = np.meshgrid(xs[i0:i1], ys[j0:j1], zs[k0:k1], indexing='ij')
    px, py, pz = gx - e['x'], gy - e['y'], gz - zc
    dist = np.sqrt(px ** 2 + py ** 2 + pz ** 2)
    ball = Rb - dist
    la = np.deg2rad(e['lid_ang']); ud = (np.cos(la), np.sin(la)); proj = px * ud[0] + py * ud[1]
    ga = la + np.pi + e['gaze']; phi = e['phi']; dg = np.array([np.sin(phi) * np.cos(ga), np.sin(phi) * np.sin(ga), np.cos(phi)])
    Ri = 0.5 * R; cp = np.array([e['x'], e['y'], zc]) + dg * (Rb + 0.35 * Ri)
    pit = np.sqrt((gx - cp[0]) ** 2 + (gy - cp[1]) ** 2 + (gz - cp[2]) ** 2) - Ri
    ball_ir = np.minimum(ball, pit)
    t0_ = Rb * (1 - 2 * e['cover']); lid = np.minimum((Rb + 3.2) - dist, proj - t0_)
    t1_ = Rb * (1 - 2 * e['bag']); low = np.minimum((Rb + 2.4) - dist, -proj - t1_)
    rxy = np.sqrt(px ** 2 + py ** 2); gw = 0.2 * R; gd = 0.16 * R         # V socket: half-width 0.2R, depth 0.16R -> ~102 deg open
    gdep = gd * np.clip(1 - np.abs(rxy - 1.35 * R) / gw, 0, 1)
    sock = (gdep > 0) & (gz > e['zb'] - gdep)
    sub = F[i0:i1, j0:j1, k0:k1]; sub[sock] = np.minimum(sub[sock], -1.0)
    fe = np.maximum(ball_ir, np.maximum(lid, low))
    F[i0:i1, j0:j1, k0:k1] = np.maximum(F[i0:i1, j0:j1, k0:k1], fe.astype(np.float32))


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


def grid_sample(G, x, y, vox):
    return ndi.map_coordinates(G.astype(np.float64), [np.clip((x + HALF) / vox, 0, G.shape[0] - 1), np.clip((y + HALF) / vox, 0, G.shape[1] - 1)], order=1)


def grain_pass(v, f, flow_grid, aux, eyes, teethset, vox, shelves, seed, W):
    """Taubin smoothing + coarse flow-aligned ridged displacement (outward only). Calm bellies/eyes/teeth get less; the mask less still."""
    nv = len(v)
    e = np.concatenate([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]]); e = np.concatenate([e, e[:, ::-1]])
    A = sparse.csr_matrix((np.ones(len(e), np.float32), (e[:, 0], e[:, 1])), shape=(nv, nv)); A.data[:] = 1
    dg = np.asarray(A.sum(1)).ravel(); dg[dg == 0] = 1
    vn0 = vnormals(v, f)
    pin = v[:, 2] < 1.6
    for sh in shelves: pin |= (np.abs(v[:, 1] - sh['ys']) < 1.0) & (vn0[:, 1] > 0.9)
    v1 = taubin(v, A, dg, ~pin, 6)
    n1 = vnormals(v1, f)
    th = grid_sample(flow_grid, v1[:, 0], v1[:, 1], vox)
    U = v1[:, 0] * np.cos(th) + v1[:, 1] * np.sin(th); Wc = -v1[:, 0] * np.sin(th) + v1[:, 1] * np.cos(th)
    rng = np.random.default_rng(seed + 5)
    a_ = ndi.gaussian_filter(rng.standard_normal((160, 160, 48)), 1.0, mode='wrap'); a_ /= a_.std()
    a_ = ndi.spline_filter(a_, order=3, mode='grid-wrap')
    ridge = np.zeros(nv); ws = 0
    for lu, lv, lz, wt in ((90.0, 12.0, 30.0, 0.8), (50.0, 6.5, 20.0, 1.0)):
        c = np.stack([U * 5 / lu + 40, Wc * 5 / lv + 70, v1[:, 2] * 5 / lz])
        nz_ = np.empty(nv)
        for s in range(0, nv, 1_000_000):
            nz_[s:s + 1_000_000] = ndi.map_coordinates(a_, c[:, s:s + 1_000_000], order=3, prefilter=False, mode='grid-wrap')
        ridge += wt * (1 - np.abs(np.clip(nz_ / 2.2, -1, 1))) ** 2; ws += wt
    ridge /= ws
    wr = sstep((v1[:, 2] - 22.0) / 25.0)
    amp = (1.1 + 1.9 * wr) * (~pin)
    calm_v = grid_sample(aux['calm'], v1[:, 0], v1[:, 1], vox)
    amp = amp * (1.0 - 0.55 * np.clip(calm_v, 0, 1))                               # calm muscle bellies: fine grain only
    mqv = grid_sample(aux['mq'], v1[:, 0], v1[:, 1], vox)
    amp = amp * (1.0 - (1.0 - (0.18 + 0.25 * W) * 1.0) * (1 - sstep((mqv - 1.0) / 0.25)))   # mask: clean (weathering is in the field)
    if eyes:
        et = cKDTree(np.array([[q['x'], q['y']] for q in eyes])); er = np.array([q['R'] for q in eyes])
        d, ix = et.query(v1[:, :2]); amp = amp * (1 - 0.65 * (d < 1.3 * er[ix]))
    if teethset.tree is not None:
        d, _ = teethset.tree.query(v1, workers=4); amp = amp * (1 - 0.5 * (d < 20.0))
    return v1 + n1 * (amp * ridge)[:, None], dict(disp_mean=float((amp * ridge).mean()), disp_max=float((amp * ridge).max()))


def tags(v, aux_grids, eyes, teethset, vox):
    """Per-vertex aux for the renderer: calm, maw_sd, eye tag (1 sclera/lid, 2 iris pit region), teeth tag."""
    calm = grid_sample(aux_grids['calm'], v[:, 0], v[:, 1], vox); msd = grid_sample(aux_grids['maw_sd'], v[:, 0], v[:, 1], vox)
    eye = np.zeros(len(v)); teeth = np.zeros(len(v))
    if eyes:
        et = cKDTree(np.array([[q['x'], q['y']] for q in eyes])); er = np.array([q['R'] for q in eyes]); ez = np.array([q['zb'] for q in eyes])
        d, ix = et.query(v[:, :2]); eye = ((d < 1.12 * er[ix]) & (v[:, 2] > ez[ix] - 2)).astype(float)
    if teethset.tree is not None:
        d, idx = teethset.tree.query(v, workers=4); teeth = (d < teethset.r[idx] + 2.5).astype(float)
    return np.stack([calm, msd, eye, teeth], 1).astype(np.float32)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--variant', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--vox', type=float, default=2.0)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    F, xs, ys, zs, meta, t0, aux, eyes, teethset, (strut, s_r), curves = run(a.variant, a.vox, a.out)
    v, f = gp.mesh_from_field(F, xs, ys, zs, a.vox)
    print('mc', v.shape, f.shape, round(time.time() - t0, 1), flush=True)
    vol = np.einsum('ij,ij->i', v[f[:, 0]], np.cross(v[f[:, 1]], v[f[:, 2]])).sum() / 6.0
    if vol < 0: f = f[:, [0, 2, 1]]
    del F
    pr = VARIANTS[a.variant]; shelves = SHELF_ARR[pr['shelves']]
    flow = np.load(os.path.join(a.out, a.variant + '_flow.npy'))
    v2, gi = grain_pass(v.astype(np.float64), f.astype(np.int64), flow, aux, eyes, teethset, a.vox, shelves, pr['seed'], pr['weather'])
    meta['grain'] = gi
    # HARD CLIP to the envelope (vertex clamp; grain is outward-only so this only trims <= ~3 mm of grain)
    v2[:, 0] = np.clip(v2[:, 0], -HALF, HALF); v2[:, 1] = np.clip(v2[:, 1], -HALF, HALF); v2[:, 2] = np.clip(v2[:, 2], 0.0, Z_MAX)
    vol = np.einsum('ij,ij->i', v2[f[:, 0]], np.cross(v2[f[:, 1]], v2[f[:, 2]])).sum() / 6.0
    meta['volume_cm3_solid'] = round(abs(float(vol)) / 1000, 1); meta['mass_g_PETG_solid_upper_bound'] = round(abs(float(vol)) / 1000 * 1.27, 0)
    eng = {}
    eng['verts'] = int(len(v2)); eng['tris'] = int(len(f))
    eng['bbox_min_mm'] = [round(float(x), 1) for x in v2.min(0)]; eng['bbox_max_mm'] = [round(float(x), 1) for x in v2.max(0)]
    eng['bbox_size_mm'] = [round(float(x), 1) for x in (v2.max(0) - v2.min(0))]
    eng['bbox_within_914x914x300'] = bool(all(s <= lim + 1e-6 for s, lim in zip(eng['bbox_size_mm'], (914.0, 914.0, 300.0))))
    back = v2[v2[:, 2] < 3.0, 2]; eng['back_plane_z_range_mm'] = [round(float(back.min()), 2), round(float(back.max()), 2)]
    fi = f.astype(np.int64); fc = v2[fi].mean(1)
    fnt = np.cross(v2[fi[:, 1]] - v2[fi[:, 0]], v2[fi[:, 2]] - v2[fi[:, 0]]); area = 0.5 * np.linalg.norm(fnt, axis=1); nrm = fnt / (np.linalg.norm(fnt, axis=1)[:, None] + 1e-12)
    eng['shelf_flats'] = []
    for sh in shelves:
        sel = (nrm[:, 1] > 0.999) & (np.abs(fc[:, 1] - sh['ys']) < 0.8) & (fc[:, 0] > sh['xc'] - 95) & (fc[:, 0] < sh['xc'] + 95)
        pts = v2[np.unique(fi[sel].ravel())] if sel.any() else np.zeros((0, 3))
        eng['shelf_flats'].append(dict(top_y=sh['ys'], p_mm=sh['p'], flat_area_cm2=round(float(area[sel].sum()) / 100, 1),
                                       flat_spread_mm=round(float(np.ptp(pts[:, 1])), 3) if len(pts) else None,
                                       footprint_nominal_mm=[SHELF_W, sh['p']], extent_z_mm=round(float(pts[:, 2].max()), 1) if len(pts) else None))
    # headroom: vertices above the plate (beyond the 10 mm rim-lip allowance) inside the footprint x z-range
    eng['headroom'] = []
    for sh in shelves:
        inb = (v2[:, 0] > sh['xc'] - SHELF_W / 2 + 2.5) & (v2[:, 0] < sh['xc'] + SHELF_W / 2 - 2.5) & (v2[:, 2] < sh['p']) & (v2[:, 1] > sh['ys'] + 12.0) & (v2[:, 1] < sh['ys'] + 300.0)
        clear = (float(v2[inb, 1].min() - sh['ys']) if inb.any() else None)
        eng['headroom'].append(dict(top_y=sh['ys'], intruding_verts_above_12mm_lip=int(inb.sum()), clear_height_mm=clear if clear is not None else '>= 300 (none)'))
    # seat embed
    eng['seat_embed_depth_mm'] = SEAT_DEPTH
    # relief distribution (max z per 4 mm cell, cells with relief > 5 mm, excl. shelf plates region x<-250|x>250 above y of plates not separated)
    G = np.zeros((229, 229)); gi_ = np.clip(((v2[:, 0] + HALF) / 4.0).astype(int), 0, 228); gj_ = np.clip(((v2[:, 1] + HALF) / 4.0).astype(int), 0, 228)
    np.maximum.at(G, (gi_, gj_), v2[:, 2])
    cov = G > 5; body = cov.copy()
    gxx, gyy = np.meshgrid(np.arange(229) * 4.0 - HALF, np.arange(229) * 4.0 - HALF, indexing='ij')
    for sh in shelves: body &= ~((np.abs(gxx - sh['xc']) < SHELF_W / 2 + 6) & (gyy > sh['ys'] - 160) & (gyy < sh['ys'] + 12))
    Gb = G[body]
    eng['relief_mm'] = dict(mean=round(float(Gb.mean()), 1), p10=round(float(np.percentile(Gb, 10)), 1), p50=round(float(np.percentile(Gb, 50)), 1),
                            p90=round(float(np.percentile(Gb, 90)), 1), std=round(float(Gb.std()), 1), max=round(float(Gb.max()), 1), covered_cells=int(body.sum()))
    # buttress core: min in-plane inscribed diameter at stations along the path (t 0.15..0.80)
    vt = cKDTree(v2); mind = []
    for ii in np.linspace(0.15, 0.80, 40):
        kk = int(ii * (len(strut) - 1)); tan = strut[min(kk + 3, len(strut) - 1)] - strut[max(kk - 3, 0)]; tan /= np.linalg.norm(tan)
        cand = vt.query_ball_point(strut[kk], 60.0); P_ = v2[cand] - strut[kk]; ax = P_ @ tan
        sl_ = np.abs(ax) < 3.0
        if sl_.any(): mind.append(float(np.linalg.norm(P_[sl_] - np.outer(ax[sl_], tan), axis=1).min()))
    eng['buttress'] = dict(min_core_diameter_mm=round(2 * min(mind), 1), median_diameter_mm=round(2 * float(np.median(mind)), 1),
                           drop_mm=meta['strut']['drop_mm'], foot_pad_mm=meta['strut']['foot_pad_mm'], core_dia_mm=meta['strut']['core_dia_mm'], foot=meta['strut']['foot'])
    eng['eyes'] = dict(count=len(eyes), dia_mm_min=round(2 * min(e['R'] for e in eyes), 1) if eyes else None, dia_mm_max=round(2 * max(e['R'] for e in eyes), 1) if eyes else None,
                       iris_pit_dia_mm_min=round(min(e['R'] for e in eyes), 1) if eyes else None)
    eng['teeth'] = dict(count=len(meta['teeth']), broken=int(sum(t['broken'] for t in meta['teeth'])),
                        length_mm_min=round(min(t['length'] for t in meta['teeth']), 1), length_mm_max=round(max(t['length'] for t in meta['teeth']), 1))
    meta['engineering'] = eng
    meta['variant'] = a.variant; meta['params'] = pr; meta['vox_mm'] = a.vox
    tg = tags(v2, aux, eyes, teethset, a.vox)
    np.savez(os.path.join(a.out, a.variant + '.npz'), v=v2.astype(np.float32), f=f.astype(np.uint32), aux=tg)
    json.dump(meta, open(os.path.join(a.out, a.variant + '_meta.json'), 'w'), indent=1, default=lambda o: o.tolist() if hasattr(o, 'tolist') else str(o))
    print(json.dumps(eng, indent=1)); print('done', round(time.time() - t0, 1))
