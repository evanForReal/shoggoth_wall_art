#!/usr/bin/env python3
"""Gate-2 field generator (Gate-1C field + irregular bays, broken rims, flow-dominant infill; flow grid exported
for the bpy character pass in sculpt.py)

Gate-1C test patch generator (hierarchy: large oval voids + ring membranes, global streamline flow,
recessed back membrane, bead-knob removal; derived from Gate 1B)

Gate-1B test patch generator: procedural SDF webbing + fibres + limb + shelf stub.

Gate 1B changes vs Gate 1: denser/smaller cells, heavy-tailed strand widths (2-8 mm), crisp torn membrane
edges + pores/grain, flow-traced sagged fibres across voids, fibre-fan shelf underside, F saved for min-wall pass.

World frame (mm): wall plane z=0 (flat back), +z leaves wall, +y is up.
Field F > 0 inside solid. Meshed once by marching cubes on a regular grid.

Usage: python3 gen_patch.py --vox 0.5 --out OUTDIR
Outputs: patch_full.npz (verts, faces, colors) and validation numbers (json).
"""
import argparse, json, time
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from scipy.interpolate import CubicSpline

# ----------------------------- KNOBS (mm) ----------------------------------
SEED = 7
X_RANGE = (-110.0, 110.0)      # domain
Y_RANGE = (-100.0, 100.0)
Z_MAX = 165.0
STRAND_W_MIN, STRAND_W_MAX = 2.1, 3.0   # full width of ordinary strands
LOAD_BOOST = 0.65              # extra width factor next to limb / shelf root (-> up to ~4.8 mm)
FLARE = 0.18                   # fillet flare of strand roots at back plane / shelf plate
EDGE_REMOVE_P = 0.17           # fraction of Voronoi edges deleted (merges holes)
HOLE_R_MIN, HOLE_R_MAX = 8.5, 16.0   # seed spacing radius field (hole-size gradient)
HOLE_STRETCH = 1.5             # membrane hole elongation along flow
STRAND_VAR = 0.45              # along-strand width modulation (+-)
FLOW_ANISO = 1.3               # seed spacing ratio along flow vs across (cell elongation)
WARP_BIG = (8.0, 170.0)       # amplitude, wavelength: large flow warp
WARP_SMALL = (3.0, 55.0)       # small wobble warp (also z-dependent => leaning walls)
EDGE_WOBBLE = 0.30             # strand-edge noise amplitude
H_MIN, H_MAX = 9.0, 30.0      # relief height range of primary web
SKIN_T = 3.0                   # membrane skin thickness (z) in non-open cells
OPEN_P = (0.20, 0.55)          # probability a cell is an open hole: low -> high along density gradient
EDGE_REMOVE_OO = 0.50          # open-open edges deleted (merged holes)
SEC_R = 9.5                    # secondary (low membrane) net spacing
SEC_W = 2.0                    # secondary strand full width
SIL_HALF = 100.0               # web silhouette half-size
LIMB_R = 13.0                  # limb outer radius (26 mm OD)
LIMB_WALL = 2.0
LIMB_Z0 = 11.0                 # limb axis height above back plane
LIMB_RELIEF = 3.4
LIMB_PTS = np.array([[40, -62, 11], [78, -48, 11], [92, -10, 12], [68, 28, 11],
                     [35, 52, 12], [45, 85, 11], [70, 112, 11]], float)
SHELF_X = (-95.0, 55.0)        # nominal shelf footprint 150 wide
SHELF_P = 150.0                # protrusion
SHELF_Y = -34.75               # flat top plane height
PLATE_T = 4.0
SHELF_D0, SHELF_DTIP = 55.0, 14.0   # underside web depth at root / tip
ROOT_DEPTH = 8.0              # solid root block depth (placeholder for cleat embed)
WIDTH_TAIL = 3.0               # heavy-tail extra half-width (mm) -> strands span ~2-8 mm
W_HALF_CAP = 4.5               # hard cap on strand half-width
CRISP = 0.6                    # 0 = round rib cross-section, 1 = square (crisp torn edges)
RIB_HF = 0.12                  # high-frequency edge noise on ribs
TORN_AMP = 1.2                 # hole-edge roughness of membranes
SKIN_LIP = 2.0                 # feathered membrane lip thickness at hole edges
LIP_RAMP = 1.5
PIT_DEPTH, PIT_T = 1.3, 0.8    # blind pores in membrane skin (non-through)
GRAIN_AMP = 0.7                # flow-aligned grain relief on skin
FIB_R = (1.1, 1.3)             # fibre radius -> 2.0-2.5 mm dia
FIB_L = (14.0, 48.0)           # fibre chord length range
FIB_MIN_AREA, FIB_AREA_PER = 90.0, 260.0   # void area (mm2) that gets fibres; area per fibre
FIB_ZEND, FIB_ZMIN, FIB_SAG = (4.0, 8.0), 1.3, 0.07
FIB_ZREF = 4.0
SH_FIBRES, SH_LINKS = 36, 26   # shelf underside fibre fan
# ---- Gate 1C: hierarchy / flow / layering
OVALS = [(-62, 50, 34, 19, 35), (-4, 62, 27, 15, 20), (-30, 3, 22, 13, 50), (22, -4, 18, 11, 60)]  # cx, cy, semi-a, semi-b, deg (long axis 36-68 mm)
OVAL_NOISE = 4.5               # mm, boundary roughness (low frequency, keeps ovals smooth)
RING_W = 16.0                  # membrane ring width around each oval
RIM_H, RIM_W = 17.0, 2.2       # smooth rim rib around each oval (height above back, half-width)
BACK_T, BACK_H = 2.6, 8.0      # recessed back membrane thickness / back-net rib height inside ovals
SL_SPACING = 10.5              # streamline seed spacing along the entry edges
SL_W_BASE, SL_W_TAIL = 1.4, 3.2   # streamline rib half-width = base + tail*u^3
SL_GAP_P = 0.25                # fraction of streamline length switched off (fibrous gaps)
SL_H = 1.05                    # streamline rib height as fraction of local relief
SL_WIGGLE = 2.5                # mm lateral wander
FILL_SLIVER_MM = 6.0           # projection voids with inscribed diameter below this get a 2.6 mm back plug
PETG_RHO = 1.27                # g/cm3


def hash01(a, b, salt):
    lo = np.minimum(a, b).astype(np.uint64)
    hi = np.maximum(a, b).astype(np.uint64)
    h = (lo * np.uint64(73856093)) ^ (hi * np.uint64(19349663)) ^ np.uint64(salt * 83492791)
    h ^= h >> np.uint64(13)
    h *= np.uint64(0x9E3779B1)
    h ^= h >> np.uint64(16)
    return (h % np.uint64(100003)).astype(np.float64) / 100003.0


class Noise:
    """Smooth unit-variance 3D noise sampled with cubic interpolation."""
    def __init__(self, rng, lam, lo=(-140, -130, -20), hi=(140, 130, 190), aniso=(1, 1, 1)):
        self.lo = np.array(lo, float)
        self.g = lam / 5.0 * np.array(aniso, float)
        n = np.ceil((np.array(hi) - self.lo) / self.g).astype(int) + 8
        a = ndi.gaussian_filter(rng.standard_normal(n), 1.0)
        a /= a.std()
        self.a = ndi.spline_filter(a, order=3)

    def __call__(self, x, y, z):
        x, y, z = np.broadcast_arrays(x, y, z)
        shp = x.shape
        x, y, z = x.ravel(), y.ravel(), z.ravel()
        c = np.stack([(x - self.lo[0]) / self.g[0] + 3, (y - self.lo[1]) / self.g[1] + 3,
                      (z - self.lo[2]) / self.g[2] + 3])
        return ndi.map_coordinates(self.a, c, order=3, prefilter=False, mode='nearest').reshape(shp)


def smoothstep(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def dart_seeds(rng, lo, hi, rfun, thfun, aniso, ncand=80000):
    cand = rng.uniform(lo, hi, size=(ncand, 2))
    acc = np.empty((0, 2))
    buf = np.zeros((4000, 2)); n = 0
    for c in cand:
        r = rfun(c[0], c[1])
        if n:
            d = buf[:n] - c
            th = thfun(c[0], c[1])
            ct, st = np.cos(th), np.sin(th)
            al = d[:, 0] * ct + d[:, 1] * st
            pe = -d[:, 0] * st + d[:, 1] * ct
            if np.any((al / (aniso * r)) ** 2 + (pe / r) ** 2 < 1.0):
                continue
        buf[n] = c; n += 1
    return buf[:n].copy()


def pair_attrs(seeds, i1, i2, salt, wmin, wmax, remove_p, keep_fn, boost_fn, openv=None, tail=0.0):
    """Half-width per Voronoi edge (i1,i2); 0 where deleted or outside keep mask."""
    u = hash01(i1, i2, salt)
    u2 = hash01(i1, i2, salt + 11)
    w = 0.5 * (wmin + (wmax - wmin) * u2) + tail * hash01(i1, i2, salt + 23) ** 3
    mid = 0.5 * (seeds[i1] + seeds[i2])
    if openv is not None:
        rm = (u < remove_p) & openv[i1] & openv[i2]
    else:
        rm = u < remove_p
    ok = (~rm) & keep_fn(mid[..., 0], mid[..., 1])
    return np.where(ok, np.minimum(w * boost_fn(mid[..., 0], mid[..., 1]), W_HALF_CAP), 0.0)


def net_layer(tree, seeds, Qx, Qy, gnorm_sz, wfun, ks=(1, 2)):
    """Return list of (lateral distance, half-width) for pairs (nearest, k-th) at query pts."""
    d, idx = tree.query(np.stack([Qx.ravel(), Qy.ravel()], 1), k=3, workers=4)
    out = []
    P1 = seeds[idx[:, 0]]
    X = np.stack([Qx.ravel(), Qy.ravel()], 1)
    d1 = d[:, 0]
    for k in ks:
        P2 = seeds[idx[:, k]]
        bis = (d[:, k] ** 2 - d1 ** 2) / (2 * np.linalg.norm(P2 - P1, axis=1) + 1e-9)
        w = wfun(idx[:, 0], idx[:, k])
        out.append((bis.reshape(Qx.shape), w.reshape(Qx.shape), k))
    net_layer.last = (d1.reshape(Qx.shape), idx[:, 0].reshape(Qx.shape))
    return out


def grad_norm(b, h):
    gx, gy = np.gradient(b, h, h)
    return np.clip(np.hypot(gx, gy), 0.55, 1.8)



def oval_sd(x, y):
    """Approx signed distance (mm) to the nearest oval; negative inside."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    out = np.full(x.shape, 1e3)
    for cx, cy, a, b, deg in OVALS:
        t = np.deg2rad(deg)
        u = (x - cx) * np.cos(t) + (y - cy) * np.sin(t); v = -(x - cx) * np.sin(t) + (y - cy) * np.cos(t)
        q = np.sqrt((u / a) ** 2 + (v / b) ** 2) + 1e-9
        g = np.sqrt((u / a ** 2) ** 2 + (v / b ** 2) ** 2) / q + 1e-9
        out = np.minimum(out, (q - 1) / g)
    return out


class StreamSet:
    def __init__(self, P, W):
        self.tree = cKDTree(P); self.W = np.append(W, 0.0); self.wmax = float(W.max())

    def field(self, pts):
        d, idx = self.tree.query(pts, k=3, distance_upper_bound=self.wmax + 0.5, workers=4)
        w = self.W[idx]
        val = np.where(np.isfinite(d), w - d, -9.0)
        j = np.argmax(val, axis=1)[:, None]
        d1 = np.take_along_axis(np.where(np.isfinite(d), d, 99.0), j, 1)[:, 0]
        w1 = np.take_along_axis(w, j, 1)[:, 0]
        return d1, w1


def make_streamlines(rng, flow_th, sil_fn, wob_fn, ds=1.0):
    """Streamlines of the global flow field, as fibrous rib centrelines with gaps and varying width."""
    seeds = [(x + rng.uniform(-4, 4), -106.0) for x in np.arange(-120, 100, SL_SPACING)]
    seeds += [(-118.0, y + rng.uniform(-4, 4)) for y in np.arange(-96, 100, SL_SPACING)]
    allP, allW = [], []
    for (x0, y0) in seeds:
        p = np.array([x0, y0]); pts = [p.copy()]
        for _ in range(420):
            k1 = flow_th(p[0], p[1]); m = p + 0.5 * ds * np.array([np.cos(k1), np.sin(k1)])
            k2 = flow_th(m[0], m[1]); p = p + ds * np.array([np.cos(k2), np.sin(k2)]); pts.append(p.copy())
            if abs(p[0]) > 118 or abs(p[1]) > 108: break
        P = np.array(pts)
        if len(P) < 30: continue
        sarc = np.r_[0, np.cumsum(np.hypot(*np.diff(P, axis=0).T))]
        S_ = np.arange(0, sarc[-1], 0.4)
        Q = np.column_stack([np.interp(S_, sarc, P[:, 0]), np.interp(S_, sarc, P[:, 1])])
        T = np.gradient(Q, axis=0); T /= np.linalg.norm(T, axis=1)[:, None] + 1e-9
        off = SL_WIGGLE * wob_fn(Q[:, 0] * 0.5 + 17 * len(allP), Q[:, 1] * 0.5, S_ * 0.05)
        Q = Q + np.column_stack([-T[:, 1], T[:, 0]]) * off[:, None]
        u = rng.random(); w0 = SL_W_BASE + SL_W_TAIL * u ** 3
        env = 0.55 + 0.45 * np.sin(np.pi * np.clip(S_ / S_[-1], 0, 1)) ** 0.5
        W = w0 * env * (1 + 0.3 * wob_fn(Q[:, 0] * 0.2, Q[:, 1] * 0.2, S_ * 0.1 + 9))
        W = np.maximum(W, 1.1)
        # gaps
        n_gap = rng.integers(2, 6); tot = SL_GAP_P * S_[-1]
        for gl in rng.dirichlet(np.ones(n_gap)) * tot:
            g0 = rng.uniform(0, S_[-1] - gl); W[(S_ >= g0) & (S_ <= g0 + gl)] = 0.0
        W[sil_fn(Q[:, 0], Q[:, 1]) > 0] = 0.0
        keep = W > 0
        if keep.sum() > 20: allP.append(Q[keep]); allW.append(W[keep])
    return np.concatenate(allP), np.concatenate(allW), len(allP)


class FibreSet:
    """Union of variable-radius tubes along polylines (dense samples + KDTree)."""
    def __init__(self, curves):
        self.n = len(curves)
        if not curves:
            self.tree = None; return
        P = np.concatenate([c[0] for c in curves]); r = np.concatenate([c[1] for c in curves])
        self.tree = cKDTree(P); self.r = np.append(r, 0.0); self.rmax = float(r.max())

    def field(self, P3):
        if self.tree is None:
            return np.full(len(P3), -9.0)
        d, idx = self.tree.query(P3, k=2, distance_upper_bound=self.rmax + 0.3, workers=4)
        v = self.r[idx] - d
        v = np.where(np.isfinite(d), v, -9.0)
        return v.max(axis=1)


def web_fibres(rng, f0, X, Y, vox, sil_ok, flow_th):
    """Flow-traced, sagged fibres across larger voids of the z=FIB_ZREF slice f0."""
    step = max(1, int(round(1.0 / vox)))
    E = ((f0 <= 0) & sil_ok)[::step, ::step]
    Xs, Ys = X[::step, ::step], Y[::step, ::step]
    h = step * vox
    lab, n = ndi.label(E)
    areas = ndi.sum(E, lab, index=np.arange(1, n + 1)) * h * h
    curves = []
    for ci in np.argsort(-areas):
        a = areas[ci]
        if a < FIB_MIN_AREA:
            break
        comp = lab == ci + 1
        if comp[0].any() or comp[-1].any() or comp[:, 0].any() or comp[:, -1].any():
            continue
        bd = comp & ~ndi.binary_erosion(comp)
        bi = np.argwhere(bd)
        P = np.stack([Xs[bi[:, 0], bi[:, 1]], Ys[bi[:, 0], bi[:, 1]]], 1)
        nf = int(np.clip(round(a / FIB_AREA_PER), 1, 4))
        for _ in range(nf):
            for _try in range(25):
                p0 = P[rng.integers(len(P))]
                d = P - p0; Ld = np.hypot(d[:, 0], d[:, 1])
                th = flow_th(p0[0], p0[1])
                ang = np.abs(((np.arctan2(d[:, 1], d[:, 0]) - th + np.pi / 2) % np.pi) - np.pi / 2)
                ok = (Ld >= FIB_L[0]) & (Ld <= FIB_L[1]) & (ang < np.deg2rad(50))
                if not ok.any():
                    continue
                p1 = P[rng.choice(np.flatnonzero(ok))]
                ch = p0 + (p1 - p0) * np.linspace(0, 1, 24)[:, None]
                ii = np.clip(np.round((ch[:, 0] - Xs[0, 0]) / h).astype(int), 0, E.shape[0] - 1)
                jj = np.clip(np.round((ch[:, 1] - Ys[0, 0]) / h).astype(int), 0, E.shape[1] - 1)
                if comp[ii, jj].mean() < 0.5:
                    continue
                Lc = float(np.linalg.norm(p1 - p0)); u = (p1 - p0) / Lc; v = np.array([-u[1], u[0]])
                ext = 1.8
                tt = np.linspace(-ext / Lc, 1 + ext / Lc, int(Lc / 0.3) + 8)
                lat = rng.uniform(0.03, 0.09) * Lc * np.sin(np.pi * tt) * rng.choice([-1, 1]) \
                    + 0.025 * Lc * np.sin(2 * np.pi * tt * rng.uniform(0.8, 1.6) + rng.uniform(0, 6.28))
                sag = FIB_SAG * Lc * 4 * tt * (1 - tt)
                xy = p0 + np.outer(tt * Lc, u) + np.outer(lat, v) + np.outer(sag, [0.0, -1.0])
                ze = rng.uniform(*FIB_ZEND); dz = rng.uniform(1.5, 4.0)
                zc = np.maximum(ze - dz * 4 * np.clip(tt, 0, 1) * (1 - np.clip(tt, 0, 1)), FIB_ZMIN)
                r = rng.uniform(*FIB_R) * (1 - 0.18 * np.sin(np.pi * np.clip(tt, 0, 1)))
                curves.append((np.column_stack([xy, zc]), r))
                break
    return curves


def bez(P0, C1, C2, P3, n):
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 3 * P0 + 3 * (1 - t) ** 2 * t * C1 + 3 * (1 - t) * t ** 2 * C2 + t ** 3 * P3


def shelf_fibres(rng):
    """Fibres fanning from the shelf rim (underside of plate) back to the body at the wall."""
    ys0 = SHELF_Y - 2.0
    xm = 0.5 * (SHELF_X[0] + SHELF_X[1])
    tot = 138.0 + 150.0 + 138.0
    curves, paths = [], []
    for i in range(SH_FIBRES):
        p = (i + rng.uniform(0.15, 0.85)) / SH_FIBRES * tot
        if p < 138: xR, zR = SHELF_X[0] + 3, 12 + p
        elif p < 288: xR, zR = SHELF_X[0] + 3 + (p - 138), SHELF_P - 3
        else: xR, zR = SHELF_X[1] - 3, SHELF_P - 3 - (p - 288)
        xT = xm + (xR - xm) * 0.55 + rng.uniform(-12, 12); zT = rng.uniform(2, 7); yT = SHELF_Y - rng.uniform(16, 54)
        P0 = np.array([xR, ys0, zR]); P3 = np.array([xT, yT, zT])
        C1 = np.array([xR + (xT - xR) * 0.12, ys0 - rng.uniform(8, 30), zR - (zR - zT) * 0.35])
        C2 = np.array([xT + rng.uniform(-6, 6), yT + rng.uniform(4, 14), zT + (zR - zT) * 0.40])
        n = int(np.linalg.norm(P3 - P0) / 0.3) + 20
        pts = bez(P0, C1, C2, P3, n)
        t = np.linspace(0, 1, n)
        r0 = rng.uniform(1.05, 1.4); r1 = rng.uniform(1.7, 3.0) * (1.5 if rng.random() < 0.22 else 1.0)
        r = r0 + (r1 - r0) * smoothstep(t)
        curves.append((pts, r)); paths.append((pts, r))
    for _ in range(SH_LINKS):
        a = rng.integers(0, SH_FIBRES - 1); b = min(SH_FIBRES - 1, a + rng.integers(1, 3))
        ta = rng.uniform(0.3, 0.85); tb = float(np.clip(ta + rng.uniform(-0.15, 0.15), 0.2, 0.9))
        A = paths[a][0][int(ta * (len(paths[a][0]) - 1))]; B = paths[b][0][int(tb * (len(paths[b][0]) - 1))]
        mid = 0.5 * (A + B) + np.array([0, -rng.uniform(0.1, 0.25) * np.linalg.norm(B - A), 0])
        n = int(np.linalg.norm(B - A) / 0.3) + 12
        t = np.linspace(0, 1, n)[:, None]
        pts = (1 - t) ** 2 * A + 2 * (1 - t) * t * mid + t ** 2 * B
        curves.append((pts, np.full(n, rng.uniform(1.0, 1.2))))
    return curves


def run(vox, outdir, zcap=None):
    t0 = time.time()
    rng = np.random.default_rng(SEED)
    xs = np.arange(X_RANGE[0], X_RANGE[1] + 1e-6, vox) + 0.0
    ys = np.arange(Y_RANGE[0], Y_RANGE[1] + 1e-6, vox)
    zs = np.arange(0, Z_MAX, vox) + vox / 2
    nx, ny, nz = len(xs), len(ys), len(zs)
    print('grid', nx, ny, nz, nx * ny * nz / 1e6, 'M voxels')
    X, Y = np.meshgrid(xs, ys, indexing='ij')

    N = {k: Noise(rng, lam) for k, lam in dict(big_x=WARP_BIG[1], big_y=WARP_BIG[1],
         sm_x=WARP_SMALL[1], sm_y=WARP_SMALL[1], wob=11.0, hsel=80.0, hfine=30.0, sil=70.0,
         sil2=25.0, flow=140.0, rr=90.0, sec=70.0, col1=60.0, col2=18.0, col3=120.0,
         sh_d=35.0, sh_o=30.0, shw=50.0).items()}
    N['ovn'] = Noise(rng, 35.0)
    zlim = (140, 130, 70)
    for k_, lam_ in (('hf', 6.0), ('grain', 14.0), ('pit', 5.5)):
        N[k_] = Noise(rng, lam_, hi=zlim)
    Nrel = Noise(rng, 14.0, aniso=(1, 1, 3.2))
    Nrel2 = Noise(rng, 6.0)

    # ---- limb centreline
    sp = CubicSpline(np.r_[0, np.cumsum(np.linalg.norm(np.diff(LIMB_PTS, axis=0), axis=1))], LIMB_PTS)
    L = sp.x[-1]
    S = np.arange(0, L, 0.4)
    C = sp(S); T = sp(S, 1); T /= np.linalg.norm(T, axis=1)[:, None]
    N1 = np.cross(T, [0, 0, 1.0]); N1 /= np.linalg.norm(N1, axis=1)[:, None]
    N2 = np.cross(T, N1)
    ltree = cKDTree(C)
    ltree2 = cKDTree(C[:, :2])

    # ---- 2D fields
    def sil_sd(x, y):
        q = np.stack([np.abs(x), np.abs(y)]) - (SIL_HALF - 35)
        sd = np.hypot(np.maximum(q[0], 0), np.maximum(q[1], 0)) + np.minimum(np.maximum(q[0], q[1]), 0) - 35
        return sd + 13 * N['sil'](x, y, 0) + 6 * N['sil2'](x, y, 0) - 2
    dL2 = ltree2.query(np.stack([X.ravel(), Y.ravel()], 1))[0].reshape(X.shape)
    near = np.clip(1 - (dL2 - LIMB_R) / 25.0, 0, 1)

    sx = smoothstep((X - (SHELF_X[0] - 6)) / 8) * (1 - smoothstep((X - (SHELF_X[1] + 12)) / 8))
    above = smoothstep((Y - SHELF_Y) / 45.0)
    shelf_mask = sx * (1 - above)    # 1 right near shelf plate zone
    S_h = smoothstep(0.5 + 0.38 * N['hsel'](X, Y, 0) + 0.17 * N['hfine'](X, Y, 0))
    h = H_MIN + (H_MAX - H_MIN) * S_h + 3 * np.exp(-np.maximum(dL2 - LIMB_R, 0) ** 2 / (2 * 16 ** 2))
    h = np.minimum(h, 38)
    h = np.minimum(h, 12 + 20 * smoothstep((dL2 - LIMB_R - 4) / 30.0))   # keep the limb proud of the web
    h = np.where(sx > 0, h * (1 - sx * (1 - above)) + sx * (1 - above) * np.minimum(h, 13) , h)
    h = np.maximum(h, 7.0)
    ov_grid = oval_sd(X, Y) + OVAL_NOISE * N['ovn'](X, Y, 0) + 2.2 * N['hfine'](X, Y, 0)   # irregular bays, not ellipses
    h = h + 5 * np.exp(-np.maximum(ov_grid, 0) ** 2 / (2 * 9.0 ** 2))   # relief rises toward oval rims
    h = np.minimum(h, 16 + 22 * smoothstep((dL2 - LIMB_R - 4) / 30.0))
    sec_mask = N['sec'](X, Y, 0)

    def boost(x, y):
        d = ltree2.query(np.stack([np.ravel(x), np.ravel(y)], 1))[0].reshape(np.shape(x))
        b = np.clip(1 - (d - LIMB_R) / 25.0, 0, 1)
        return 1 + LOAD_BOOST * b

    def keep1(x, y): return sil_sd(x, y) < 0
    def keep2(x, y): return (sil_sd(x, y) < 0) & ((N['sec'](x, y, 0) > -0.15) | (oval_sd(x, y) < 3.0))

    # ---- seeds
    flow_th = lambda x, y: np.deg2rad(28 + 42 * smoothstep((np.asarray(y) + 70) / 150.0) - 18 * smoothstep((np.asarray(x) + 40) / 110.0) + 13 * N['flow'](x, y, 0))
    def rfun(x, y):
        g = np.clip(0.5 + 0.5 * ((x * np.cos(0.6) + y * np.sin(0.6)) / 120) + 0.4 * N['rr'](x, y, 0), 0, 1)
        return HOLE_R_MIN + (HOLE_R_MAX - HOLE_R_MIN) * smoothstep(g)
    s1 = dart_seeds(rng, (-140, -130), (140, 130), rfun, flow_th, FLOW_ANISO, ncand=160000)
    s2 = dart_seeds(rng, (-140, -130), (140, 130), lambda x, y: SEC_R * (1 + 0.35 * smoothstep(0.5 + 0.5 * N['rr'](y, x, 0))),
                    flow_th, 1.3, ncand=40000)
    print('seeds', len(s1), len(s2), round(time.time() - t0, 1))
    t1, t2 = cKDTree(s1), cKDTree(s2)
    gseed = np.clip(0.5 + 0.5 * ((s1[:, 0] * np.cos(0.6) + s1[:, 1] * np.sin(0.6)) / 120) + 0.4 * N['rr'](s1[:, 0], s1[:, 1], 0), 0, 1)
    popen = OPEN_P[0] + (OPEN_P[1] - OPEN_P[0]) * smoothstep(gseed)
    open1 = hash01(np.arange(len(s1)), np.arange(len(s1)), 77) < popen
    nn1 = t1.query(s1, k=2)[0][:, 1]
    hole_R = np.minimum(np.maximum(nn1 * (0.30 + 0.14 * hash01(np.arange(len(s1)), np.arange(len(s1)), 31)), 3.0), 0.46 * nn1)
    th1 = flow_th(s1[:, 0], s1[:, 1])
    nn2 = t2.query(s2, k=2)[0][:, 1]
    hole_R2 = np.minimum(np.maximum(nn2 * (0.30 + 0.14 * hash01(np.arange(len(s2)), np.arange(len(s2)), 41)), 3.0), 0.46 * nn2)
    # edge attribute caches evaluated lazily per layer (hash based, deterministic)
    w1f = lambda a, b: pair_attrs(s1, a, b, 1, STRAND_W_MIN, STRAND_W_MAX, EDGE_REMOVE_OO, keep1, boost, open1, WIDTH_TAIL)
    w2f = lambda a, b: pair_attrs(s2, a, b, 5, SEC_W, SEC_W + 0.4, 0.12, keep2, lambda x, y: 1.0)

    F = np.full((nx, ny, nz), -1.0, np.float32)
    LIMB_ZMAX = LIMB_Z0 + LIMB_R + LIMB_RELIEF + 2
    WEB_ZMAX = 40.5
    kcav = int(np.searchsorted(zs, LIMB_ZMAX)) + 1
    CAV = np.full((nx, ny, kcav), -1.0, np.float32)
    PTS = np.stack([X.ravel(), Y.ravel()], 1)

    sl_P, sl_W, sl_n = make_streamlines(np.random.default_rng(SEED + 303), flow_th, sil_sd,
                                        lambda a, b, c: N['wob'](a, b, c))
    sl = StreamSet(sl_P, sl_W)
    print('streamlines', sl_n, len(sl_P), round(time.time() - t0, 1))

    def rib_sd(lat, w, ez, fl):
        sd = (1 - CRISP) * np.hypot(np.maximum(lat, 0), ez) + CRISP * np.maximum(lat, ez) - w * fl
        return np.where(w > 0, sd, 9.0)

    def web_f(z):
        qx = X + WARP_BIG[0] * N['big_x'](X, Y, z * 0.5) + WARP_SMALL[0] * N['sm_x'](X, Y, z * 1.4)
        qy = Y + WARP_BIG[0] * N['big_y'](X, Y, z * 0.5) + WARP_SMALL[0] * N['sm_y'](X, Y, z * 1.4)
        wob = EDGE_WOBBLE * N['wob'](X, Y, z)
        hf = N['hf'](X, Y, z)
        fl = 1 + FLARE * np.exp(-z / 6.0)
        front = np.full(X.shape, -9.0)
        back = np.full(X.shape, -9.0)
        for tree, seeds, wf, hh, is_front in ((t1, s1, w1f, 0.45 * h, True),
                                              (t2, s2, w2f, np.where(ov_grid < 2.0, BACK_H, np.clip(0.45 * h, 6, 15)), False)):
            prs = net_layer(tree, seeds, qx, qy, 0, wf)
            last = net_layer.last
            if is_front: last_primary = last
            else: last_secondary = last
            g = grad_norm(prs[0][0], vox)
            for bis, w, kk in prs:
                w = w * (1 + STRAND_VAR * N['wob'](X * 0.45, Y * 0.45, z * 0.3 + 40))
                w = np.where(w > 0, np.maximum(w, 1.1), 0.0)
                lat = bis / g + wob + RIB_HF * hf
                ez = np.maximum(z - (hh - w), 0)
                sd = rib_sd(lat, w, ez, fl)
                if is_front: front = np.maximum(front, -sd)
                else: back = np.maximum(back, -sd)
        # global-flow streamline ribs (front)
        dS, wS = sl.field(PTS)
        dS = dS.reshape(X.shape); wS = wS.reshape(X.shape)
        wS = np.where(wS > 0, wS, 0.0)
        ezS = np.maximum(z - (SL_H * h - wS), 0)
        front = np.maximum(front, -rib_sd(dS + wob + RIB_HF * hf, wS, ezS, fl))
        # membrane skin of primary cells (open cells suppressed except away from oval rings)
        d1p, i1p = last_primary
        dv = np.stack([qx, qy], -1) - s1[i1p]
        ct, st = np.cos(th1[i1p]), np.sin(th1[i1p])
        al = (dv[..., 0] * ct + dv[..., 1] * st) / HOLE_STRETCH
        pe = -dv[..., 0] * st + dv[..., 1] * ct
        dh = np.hypot(al, pe)
        grain = GRAIN_AMP * N['grain'](al * 0.25 + s1[i1p, 0], pe + s1[i1p, 1], 0.0)
        band = 1 - smoothstep(np.maximum(ov_grid, 0) / RING_W)       # 1 at oval rim -> 0 outside ring
        pitf = smoothstep((N['pit'](X, Y, 0.0) - (PIT_T - 0.6 * band)) / 0.35)
        zsk = SKIN_T + 0.35 * (h - 8) + 1.5 * N['wob'](X * 0.3, Y * 0.3, 0) + grain - PIT_DEPTH * pitf
        zsk = np.maximum(zsk, 2.4) + 9.0 * band ** 1.5      # membrane swells toward each oval rim
        dist_h = dh - hole_R[i1p]
        lip = SKIN_LIP + (zsk - SKIN_LIP) * smoothstep(dist_h / LIP_RAMP)
        f_sk = np.minimum(dist_h + wob + TORN_AMP * hf, lip - z)
        opn = open1[i1p] & (ov_grid > RING_W)
        f_sk = np.where(opn, -9.0, f_sk)
        front = np.maximum(front, f_sk)
        front = np.minimum(front, -sil_sd(X, Y))
        # large oval voids: carve the front web, add a smooth rim
        front = np.minimum(front, ov_grid)
        hr = RIM_H + 4 * N['hfine'](X, Y, 0)
        ezR = np.maximum(z - (hr - RIM_W), 0)
        rimw = RIM_W * np.clip(0.55 + 1.0 * N['hfine'](X * 0.7, Y * 0.7, 3.0), 0.0, 1.6)
        rimw = np.where(rimw < 1.15, 0.0, rimw)                          # rim breaks up: no continuous drawn ellipse
        rim = -rib_sd(np.abs(ov_grid) + RIB_HF * hf, rimw, ezR, fl)
        rim = np.minimum(rim, -sil_sd(X, Y))
        # recessed back membrane inside ovals (perforated, sits on back plane)
        d2p, i2p = last_secondary
        f_bk = np.minimum(d2p - hole_R2[i2p] + wob, BACK_T - z)
        f_bk = np.minimum(f_bk, 2.0 - ov_grid)
        back = np.minimum(np.maximum(back, f_bk), np.where(sil_sd(X, Y) < 0, 9.0, -9.0))
        return np.maximum.reduce([front, rim, back])

    # ---- pass 1: fibres across voids (from the z = FIB_ZREF slice)
    f0 = web_f(FIB_ZREF)
    sil_ok = (sil_sd(X, Y) < -4) & (dL2 > LIMB_R + 2) & ~((X > SHELF_X[0] - 8) & (X < SHELF_X[1] + 12) & (Y < SHELF_Y + 4))
    fib = FibreSet(web_fibres(np.random.default_rng(SEED + 101), f0, X, Y, vox, sil_ok, flow_th))
    print('web fibres', fib.n, round(time.time() - t0, 1))

    for k in range(min(nz, int(np.searchsorted(zs, max(WEB_ZMAX, LIMB_ZMAX))) + 1)):
        z = zs[k]
        f = web_f(z)
        if z < FIB_ZEND[1] + 1.5 and fib.n:
            P3 = np.concatenate([PTS, np.full((PTS.shape[0], 1), z)], 1)
            f = np.maximum(f, fib.field(P3).reshape(X.shape))
        # limb
        if k < kcav:
            P3 = np.concatenate([PTS, np.full((PTS.shape[0], 1), z)], 1)
            rho, ix = ltree.query(P3, workers=4)
            dv = P3 - C[ix]
            phi = np.arctan2((dv * N2[ix]).sum(1), (dv * N1[ix]).sum(1))
            s_ = S[ix]
            u = LIMB_R * np.cos(phi); v = LIMB_R * np.sin(phi)
            rel = LIMB_RELIEF * (0.7 * Nrel(u, v, s_ * 14 / 45) + 0.3 * Nrel2(P3[:, 0], P3[:, 1], z))
            Rr = LIMB_R + rel
            fl_ = (Rr - rho)
            fl_ = np.where(s_ > S[-2], -9, fl_)
            cav = np.minimum(Rr - LIMB_WALL - rho, s_ - 24.0)
            f = np.maximum(f, fl_.reshape(X.shape))
            CAV[:, :, k] = cav.reshape(X.shape)
        F[:, :, k] = f
        if k % 20 == 0:
            print('layer', k, round(z, 1), round(time.time() - t0, 1))
    F[:, :, :kcav] = np.minimum(F[:, :, :kcav], -CAV)
    del CAV

    # ---------------- shelf ----------------
    xs_, zs_ = np.meshgrid(xs, zs, indexing='ij')
    mask_sh = (xs_ > -125) & (xs_ < 75)
    bump = np.clip(4 + 5 * N['sh_o'](xs_, 0, zs_), 0, 9)
    sd_out = np.maximum.reduce([xs_ - SHELF_X[1] - bump, SHELF_X[0] - bump - xs_, zs_ - SHELF_P - bump])
    edge_x = np.minimum(xs_ - SHELF_X[0], SHELF_X[1] - xs_)
    D_root = SHELF_D0 * (0.6 + 0.4 * smoothstep(edge_x / 30.0 + 0.2)) * (1 + 0.3 * N['sh_d'](xs_, 0, zs_))
    shf = FibreSet(shelf_fibres(np.random.default_rng(SEED + 202)))
    print('shelf fibres', shf.n)
    j0 = np.searchsorted(ys, SHELF_Y - 78)
    j1 = np.searchsorted(ys, SHELF_Y + 1.0)
    for j in range(j0, j1):
        y = ys[j]
        t = SHELF_Y - y       # depth below top plane (>=0 under)
        f = np.full(xs_.shape, -9.0)
        # plate
        fy = PLATE_T / 2 - np.abs(y - (SHELF_Y - PLATE_T / 2))
        f = np.maximum(f, np.minimum(fy, -sd_out))
        if t >= 0:
            froot = np.minimum.reduce([ROOT_DEPTH - zs_, D_root - t, -sd_out])
            f = np.maximum(f, froot)
            P3 = np.stack([xs_.ravel(), np.full(xs_.size, y), zs_.ravel()], 1)
            f = np.maximum(f, np.minimum(shf.field(P3).reshape(xs_.shape), -sd_out + 3))
        f = np.where(mask_sh, f, -9.0)
        F[:, j, :] = np.maximum(F[:, j, :], f.astype(np.float32))
    print('fields done', round(time.time() - t0, 1))
    return F, xs, ys, zs, dict(vox=vox, C=C, t0=t0, N=N, Nlam=None, flow=flow_th(X, Y), flow_x0=float(xs[0]), flow_y0=float(ys[0]))


def mesh_from_field(F, xs, ys, zs, vox):
    from skimage import measure
    # mirror-negated pad -> flat cuts exactly half a voxel outside the sampled planes
    # tie-break: exact-zero samples (grid-aligned planes) make marching cubes non-manifold
    jit = np.random.default_rng(1).uniform(-1e-4, 1e-4, F.shape).astype(np.float32)
    Fp = np.pad(F + jit + np.float32(5e-4), 1, mode='edge')
    del jit
    for ax in range(3):
        sl = [slice(None)] * 3
        sl[ax] = 0; lo = tuple(sl)
        sl[ax] = 1; lo1 = tuple(sl)
        Fp[lo] = -np.abs(Fp[lo1])
        sl[ax] = -1; hi = tuple(sl)
        sl[ax] = -2; hi1 = tuple(sl)
        Fp[hi] = -np.abs(Fp[hi1])
    v, f, n, _ = measure.marching_cubes(Fp, 0.0, spacing=(vox, vox, vox))
    v = v + np.array([xs[0] - vox, ys[0] - vox, zs[0] - vox])
    v[:, 2] -= 0.0
    # z pad: first sample at vox/2, pad at -vox/2, crossing at z=0 exactly
    return v, f


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--vox', type=float, default=0.5)
    ap.add_argument('--out', required=True)
    ap.add_argument('--set', nargs='*', default=[], help='override module constants, e.g. OPEN_P=(0.3,0.7)')
    ap.add_argument('--window', type=float, nargs=5, metavar=('X0', 'X1', 'Y0', 'Y1', 'ZMAX'),
                    help='evaluate a sub-window only (same seeds/fields; for resolution studies)')
    a = ap.parse_args()
    import os, trimesh
    os.makedirs(a.out, exist_ok=True)
    import ast
    for kv in a.set:
        k_, v_ = kv.split('=', 1); globals()[k_] = ast.literal_eval(v_)
    if a.window:
        X_RANGE = (a.window[0], a.window[1]); Y_RANGE = (a.window[2], a.window[3]); Z_MAX = a.window[4]
    F, xs, ys, zs, info = run(a.vox, a.out)
    np.save(os.path.join(a.out, 'F.npy'), F.astype(np.float16))
    np.save(os.path.join(a.out, 'flow.npy'), info['flow'].astype(np.float32))
    np.save(os.path.join(a.out, 'occ.npy'), (F > 0))
    json.dump(dict(vox=a.vox, x0=float(xs[0]), y0=float(ys[0]), z0=float(zs[0])), open(os.path.join(a.out, 'grid.json'), 'w'))
    if not a.window:
        v, f = mesh_from_field(F, xs, ys, zs, a.vox)
        print('mc', v.shape, f.shape)
        np.savez(os.path.join(a.out, 'raw_mesh.npz'), v=v.astype(np.float32), f=f.astype(np.uint32))
    print('saved', time.time() - info['t0'])
