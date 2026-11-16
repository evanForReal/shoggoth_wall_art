#!/usr/bin/env python3
"""Gate-1 test patch generator: procedural SDF webbing + limb + shelf stub.

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
FLARE = 0.35                   # fillet flare of strand roots at back plane / shelf plate
EDGE_REMOVE_P = 0.17           # fraction of Voronoi edges deleted (merges holes)
HOLE_R_MIN, HOLE_R_MAX = 13.0, 24.0   # seed spacing radius field (hole-size gradient)
HOLE_STRETCH = 1.5             # membrane hole elongation along flow
STRAND_VAR = 0.45              # along-strand width modulation (+-)
FLOW_ANISO = 1.7               # seed spacing ratio along flow vs across (cell elongation)
WARP_BIG = (14.0, 170.0)       # amplitude, wavelength: large flow warp
WARP_SMALL = (3.0, 55.0)       # small wobble warp (also z-dependent => leaning walls)
EDGE_WOBBLE = 0.45             # strand-edge noise amplitude
H_MIN, H_MAX = 9.0, 30.0      # relief height range of primary web
SKIN_T = 3.0                   # membrane skin thickness (z) in non-open cells
OPEN_P = (0.04, 0.34)          # probability a cell is an open hole: low -> high along density gradient
EDGE_REMOVE_OO = 0.35          # open-open edges deleted (merged holes)
SEC_R = 9.5                    # secondary (low membrane) net spacing
SEC_W = 2.0                    # secondary strand full width
SIL_HALF = 100.0               # web silhouette half-size
LIMB_R = 13.0                  # limb outer radius (26 mm OD)
LIMB_WALL = 2.0
LIMB_Z0 = 11.0                 # limb axis height above back plane
LIMB_RELIEF = 2.2
LIMB_PTS = np.array([[40, -62, 11], [78, -48, 11], [92, -10, 12], [68, 28, 11],
                     [35, 52, 12], [45, 85, 11], [70, 112, 11]], float)
SHELF_X = (-95.0, 55.0)        # nominal shelf footprint 150 wide
SHELF_P = 150.0                # protrusion
SHELF_Y = -34.75               # flat top plane height
PLATE_T = 4.0
SHELF_D0, SHELF_DTIP = 55.0, 14.0   # underside web depth at root / tip
ROOT_DEPTH = 10.0              # solid root block depth (placeholder for cleat embed)
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


def pair_attrs(seeds, i1, i2, salt, wmin, wmax, remove_p, keep_fn, boost_fn, openv=None):
    """Half-width per Voronoi edge (i1,i2); 0 where deleted or outside keep mask."""
    u = hash01(i1, i2, salt)
    u2 = hash01(i1, i2, salt + 11)
    w = 0.5 * (wmin + (wmax - wmin) * u2)
    mid = 0.5 * (seeds[i1] + seeds[i2])
    if openv is not None:
        rm = (u < remove_p) & openv[i1] & openv[i2]
    else:
        rm = u < remove_p
    ok = (~rm) & keep_fn(mid[..., 0], mid[..., 1])
    return np.where(ok, w * boost_fn(mid[..., 0], mid[..., 1]), 0.0)


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
    h = H_MIN + (H_MAX - H_MIN) * S_h + 9 * np.exp(-np.maximum(dL2 - LIMB_R, 0) ** 2 / (2 * 16 ** 2))
    h = np.minimum(h, 38)
    h = np.where(sx > 0, h * (1 - sx * (1 - above)) + sx * (1 - above) * np.minimum(h, 13) , h)
    h = np.maximum(h, 7.0)
    sec_mask = N['sec'](X, Y, 0)

    def boost(x, y):
        d = ltree2.query(np.stack([np.ravel(x), np.ravel(y)], 1))[0].reshape(np.shape(x))
        b = np.clip(1 - (d - LIMB_R) / 25.0, 0, 1)
        return 1 + LOAD_BOOST * b

    def keep1(x, y): return sil_sd(x, y) < 0
    def keep2(x, y): return (sil_sd(x, y) < 0) & (N['sec'](x, y, 0) > -0.15)

    # ---- seeds
    flow_th = lambda x, y: np.deg2rad(55 + 50 * N['flow'](x, y, 0))
    def rfun(x, y):
        g = np.clip(0.5 + 0.5 * ((x * np.cos(0.6) + y * np.sin(0.6)) / 120) + 0.4 * N['rr'](x, y, 0), 0, 1)
        return HOLE_R_MIN + (HOLE_R_MAX - HOLE_R_MIN) * smoothstep(g)
    s1 = dart_seeds(rng, (-140, -130), (140, 130), rfun, flow_th, FLOW_ANISO)
    s2 = dart_seeds(rng, (-140, -130), (140, 130), lambda x, y: SEC_R * (1 + 0.35 * smoothstep(0.5 + 0.5 * N['rr'](y, x, 0))),
                    flow_th, 1.3, ncand=40000)
    print('seeds', len(s1), len(s2), round(time.time() - t0, 1))
    t1, t2 = cKDTree(s1), cKDTree(s2)
    gseed = np.clip(0.5 + 0.5 * ((s1[:, 0] * np.cos(0.6) + s1[:, 1] * np.sin(0.6)) / 120) + 0.4 * N['rr'](s1[:, 0], s1[:, 1], 0), 0, 1)
    popen = OPEN_P[0] + (OPEN_P[1] - OPEN_P[0]) * smoothstep(gseed)
    open1 = hash01(np.arange(len(s1)), np.arange(len(s1)), 77) < popen
    nn1 = t1.query(s1, k=2)[0][:, 1]
    hole_R = nn1 * (0.30 + 0.14 * hash01(np.arange(len(s1)), np.arange(len(s1)), 31))
    th1 = np.deg2rad(55 + 50 * N['flow'](s1[:, 0], s1[:, 1], 0))
    # edge attribute caches evaluated lazily per layer (hash based, deterministic)
    w1f = lambda a, b: pair_attrs(s1, a, b, 1, STRAND_W_MIN, STRAND_W_MAX, EDGE_REMOVE_OO, keep1, boost, open1)
    w2f = lambda a, b: pair_attrs(s2, a, b, 5, SEC_W, SEC_W + 0.4, 0.12, keep2, lambda x, y: 1.0)

    F = np.full((nx, ny, nz), -1.0, np.float32)
    LIMB_ZMAX = LIMB_Z0 + LIMB_R + LIMB_RELIEF + 2
    WEB_ZMAX = 40.5
    kcav = int(np.searchsorted(zs, LIMB_ZMAX)) + 1
    CAV = np.full((nx, ny, kcav), -1.0, np.float32)
    PTS = np.stack([X.ravel(), Y.ravel()], 1)

    for k in range(min(nz, int(np.searchsorted(zs, max(WEB_ZMAX, LIMB_ZMAX))) + 1)):
        z = zs[k]
        # warped query coords
        qx = X + WARP_BIG[0] * N['big_x'](X, Y, z * 0.5) + WARP_SMALL[0] * N['sm_x'](X, Y, z * 1.4)
        qy = Y + WARP_BIG[0] * N['big_y'](X, Y, z * 0.5) + WARP_SMALL[0] * N['sm_y'](X, Y, z * 1.4)
        wob = EDGE_WOBBLE * N['wob'](X, Y, z)
        fl = 1 + FLARE * np.exp(-z / 6.0)
        best = np.full(X.shape, -9.0)
        for tree, seeds, wf, hh in ((t1, s1, w1f, h), (t2, s2, w2f, np.clip(0.45 * h, 6, 15))):
            prs = net_layer(tree, seeds, qx, qy, 0, wf)
            if tree is t1: net_layer.last_primary = net_layer.last
            g = grad_norm(prs[0][0], vox)
            for bis, w, kk in prs:
                w = w * (1 + STRAND_VAR * N['wob'](X * 0.45, Y * 0.45, z * 0.3 + 40))
                w = np.where(w > 0, np.maximum(w, 1.0), 0.0)
                lat = bis / g + wob
                ez = np.maximum(z - (hh - w), 0)
                sd = np.hypot(np.maximum(lat, 0) + 0 * lat, ez) - w * fl
                sd = np.where(w > 0, sd, 9.0)
                best = np.maximum(best, -sd)
        d1p, i1p = net_layer.last_primary
        zsk = SKIN_T + 0.35 * (h - 8) + 1.5 * N['wob'](X * 0.3, Y * 0.3, 0)
        dv = np.stack([qx, qy], -1) - s1[i1p]
        ct, st = np.cos(th1[i1p]), np.sin(th1[i1p])
        al = (dv[..., 0] * ct + dv[..., 1] * st) / HOLE_STRETCH
        pe = -dv[..., 0] * st + dv[..., 1] * ct
        dh = np.hypot(al, pe)
        f_sk = np.minimum(dh - hole_R[i1p] + wob, zsk - z + 0 * wob)
        f_sk = np.where(open1[i1p], -9.0, f_sk)
        f_sk = np.minimum(f_sk, -sil_sd(X, Y))
        best = np.maximum(best, f_sk)
        f = best
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
    # shelf web seeds in (x,z)
    rsh = lambda x, z: 11 + 12 * np.clip(z / 150.0, 0, 1)
    ssh = dart_seeds(rng, (-125, -15), (80, 180), rsh, lambda x, z: np.deg2rad(90.0 + 0 * x), 1.6)
    tsh = cKDTree(ssh)
    keep_sh = lambda x, z: (SHELF_X[0] - 6 - 0 * x < x) & (x < SHELF_X[1] + 6) & (z < SHELF_P + 4)
    boost_sh = lambda x, z: 1 + LOAD_BOOST * np.clip(1 - z / 40.0, 0, 1)
    wsh = lambda a, b: pair_attrs(ssh, a, b, 9, STRAND_W_MIN, STRAND_W_MAX, 0.14, keep_sh, boost_sh)
    qx = xs_ + 3 * N['sm_x'](xs_, 0, zs_) + 8 * N['big_x'](xs_, 0, zs_)
    qz = zs_ + 3 * N['sm_y'](xs_, 0, zs_) + 8 * N['big_y'](xs_, 0, zs_)
    prs = net_layer(tsh, ssh, qx, qz, 0, wsh)
    gsh = grad_norm(prs[0][0], vox)
    edge_x = np.minimum(xs_ - SHELF_X[0], SHELF_X[1] - xs_)
    Dm = SHELF_DTIP + (SHELF_D0 - SHELF_DTIP) * np.clip(1 - zs_ / SHELF_P, 0, 1) ** 1.5
    Dm = Dm * (0.5 + 0.5 * smoothstep(edge_x / 30.0 + 0.2)) * (1 + 0.25 * N['sh_d'](xs_, 0, zs_))
    Dm = np.maximum(Dm, 8.0)
    # root block depth profile
    D_root = SHELF_D0 * (0.5 + 0.5 * smoothstep(edge_x / 30.0 + 0.2))
    j0 = np.searchsorted(ys, SHELF_Y - SHELF_D0 * 1.4 - 8)
    j1 = np.searchsorted(ys, SHELF_Y + 1.0)
    for j in range(j0, j1):
        y = ys[j]
        t = SHELF_Y - y       # depth below top plane (>=0 under)
        f = np.full(xs_.shape, -9.0)
        # plate
        fy = PLATE_T / 2 - np.abs(y - (SHELF_Y - PLATE_T / 2))
        f = np.maximum(f, np.minimum(fy, -sd_out))
        if t >= 0:
            flare = 1 + FLARE * np.exp(-t / 6.0)
            for bis, w, kk in prs:
                lat = bis / gsh + 0.4 * N['wob'](xs_, y, zs_)
                ez = np.maximum(t - (Dm - w), 0)
                sd = np.hypot(np.maximum(lat, 0), ez) - w * flare
                sd = np.where(w > 0, sd, 9.0)
                f = np.maximum(f, np.minimum(-sd, -sd_out + 3))
            # solid root block
            froot = np.minimum.reduce([ROOT_DEPTH - zs_, D_root - t, -sd_out])
            f = np.maximum(f, froot)
        f = np.where(mask_sh, f, -9.0)
        F[:, j, :] = np.maximum(F[:, j, :], f.astype(np.float32))
    print('fields done', round(time.time() - t0, 1))
    return F, xs, ys, zs, dict(vox=vox, C=C, t0=t0, N=N, Nlam=None)


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
    a = ap.parse_args()
    import os, trimesh
    os.makedirs(a.out, exist_ok=True)
    F, xs, ys, zs, info = run(a.vox, a.out)
    v, f = mesh_from_field(F, xs, ys, zs, a.vox)
    print('mc', v.shape, f.shape)
    np.save(os.path.join(a.out, 'occ.npy'), (F > 0))
    m = trimesh.Trimesh(v, f, process=False)
    np.savez(os.path.join(a.out, 'raw_mesh.npz'), v=np.asarray(m.vertices, np.float32), f=np.asarray(m.faces, np.uint32))
    print('saved', time.time() - info['t0'])
