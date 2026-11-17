"""r08 figure engine: variable-radius sweeps, strand bundles, lace-web membranes, surface-riding ribs, carved features. Flat back, hard clip. RES 2 mm."""
import numpy as np
from PIL import Image, ImageDraw
from scipy.interpolate import splprep, splev
from scipy.spatial import cKDTree
from scipy import ndimage as ndi
RES = 2.0; HALF = 457.0; ZMAX = 300.0; X0 = -468.0
XS = np.arange(X0, 468 + 1e-6, RES); YS = XS.copy(); ZS = np.arange(-8, 310 + 1e-6, RES)
NX, NY, NZ = len(XS), len(YS), len(ZS)

def smin(a, b, k):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b * (1 - h) + a * h - k * h * (1 - h)

def curve(pts, step=1.5):
    p = np.asarray(pts, float).T
    tck, _ = splprep(p, k=min(3, len(pts) - 1), s=0)
    u = np.linspace(0, 1, 4000); c = np.array(splev(u, tck)).T
    seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(c, axis=0), axis=1))]
    n = max(int(seg[-1] / step), 8); s = np.linspace(0, seg[-1], n)
    u2 = np.interp(s, seg, u); c2 = np.array(splev(u2, tck)).T
    return c2, s / seg[-1], seg[-1]

def tent_r(t, r0, r_tip=6.0, p=0.75):
    t = np.asarray(t, float); a = r0 * np.clip(1 - t, 0, 1) ** p; r88 = r0 * 0.12 ** p
    lin = r88 + (r_tip - r88) * np.clip((t - 0.88) / 0.12, 0, 1)
    return np.maximum(np.where(t <= 0.88, a, lin), r_tip)

def apply_wave(c, t, wave):
    if not wave: return c
    A, cyc, ph, tmax = wave; tg = np.gradient(c[:, :2], axis=0); tg /= np.linalg.norm(tg, axis=1)[:, None] + 1e-9
    win = np.sin(np.pi * np.clip(t / tmax, 0, 1)) * (t < tmax); off = A * np.sin(cyc * np.pi * t / tmax + ph) * win
    c = c.copy(); c[:, 0] += -tg[:, 1] * off; c[:, 1] += tg[:, 0] * off
    return c

def spine_rfun(p4):
    """p4 = [(x,y,z,r)...]: radius interpolated on chord-length fraction."""
    P = np.asarray(p4, float); d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P[:, :2], axis=0), axis=1))]; u = d / d[-1]
    return (lambda t: np.interp(t, u, P[:, 3])), P[:, :3]

class Field:
    def __init__(s): s.F = np.full((NX, NY, NZ), 1e3, np.float32); s.K = np.zeros((NX, NY, NZ), np.uint8); s.parts = {}
    def _crop(s, lo, hi):
        i0 = max(int((lo[0] - X0) // RES), 0); i1 = min(int((hi[0] - X0) // RES) + 2, NX)
        j0 = max(int((lo[1] - X0) // RES), 0); j1 = min(int((hi[1] - X0) // RES) + 2, NY)
        k0 = max(int((lo[2] + 8) // RES), 0); k1 = min(int((hi[2] + 8) // RES) + 2, NZ)
        return (slice(i0, i1), slice(j0, j1), slice(k0, k1))
    def grid(s, sl): return np.meshgrid(XS[sl[0]], YS[sl[1]], ZS[sl[2]], indexing='ij')
    def _upd(s, sl, v, k, kind):
        old = s.F[sl]; new = smin(old, v, k).astype(np.float32); s.K[sl] = np.where(v < old, kind, s.K[sl]).astype(np.uint8); s.F[sl] = new
    def sweep(s, name, c, r, k=30.0, zs=1.0, store=True, kind=2):
        rm = r.max(); pad = rm + k + 6; lo = c.min(0) - pad; hi = c.max(0) + pad
        if zs > 1: lo[2] = -8; hi[2] = c[:, 2].max() + (rm + k + 8) / zs
        sl = s._crop(lo, hi); X, Y, Z = s.grid(sl)
        P = np.stack([X.ravel(), Y.ravel(), Z.ravel() * zs], 1); cs = c.copy(); cs[:, 2] *= zs
        d, idx = cKDTree(cs).query(P, workers=-1)
        v = (d - r[idx]).reshape(X.shape).astype(np.float32)
        s._upd(sl, v, k, kind)
        if store: s.parts[name] = dict(c=c, r=r)
    def add_sweep(s, name, pts, rfun, k=30.0, zs=1.0, wave=None, kind=1):
        c, t, L = curve(pts); c = apply_wave(c, t, wave); r = rfun(t); s.sweep(name, c, r, k, zs, kind=kind); return c, t, r, L
    def add_bundle(s, name, pts, R0, n=4, p=0.75, r_tip=6.0, wave=None, twist=1.3, k=10.0, seed=0.0, spread=0.66, rs=0.40):
        """rope of n twisted strands around the limb centreline; strands merge into one toward the tip."""
        c, t, L = curve(pts); c = apply_wave(c, t, wave); R = tent_r(t, R0, r_tip, p)
        tg = np.gradient(c[:, :2], axis=0); tg /= np.linalg.norm(tg, axis=1)[:, None] + 1e-9; nrm = np.stack([-tg[:, 1], tg[:, 0]], 1)
        merge = 1 - np.clip((t - 0.62) / 0.3, 0, 1) ** 1.5
        for q in range(n):
            ang = seed + 2 * np.pi * q / n + twist * 2 * np.pi * t
            on = spread * R * np.cos(ang) * merge; oz = 0.6 * spread * R * np.sin(ang) * merge
            cq = c.copy(); cq[:, :2] += nrm * on[:, None]; cq[:, 2] = np.maximum(c[:, 2] + oz, 3.0)
            rq = np.maximum(rs * R + (1 - merge) * 0.35 * R, max(r_tip * 0.8, 4.5))
            s.sweep(f'{name}.{q}', cq, rq, k, store=False, kind=2)
        s.parts[name] = dict(c=c, r=R); return c, t, R, L
    def add_fn(s, lo, hi, fn, k=30.0, kind=1):
        sl = s._crop(lo, hi); X, Y, Z = s.grid(sl); s._upd(sl, fn(X, Y, Z).astype(np.float32), k, kind)
    def carve(s, lo, hi, fn):
        sl = s._crop(lo, hi); X, Y, Z = s.grid(sl); s.F[sl] = np.maximum(s.F[sl], -fn(X, Y, Z).astype(np.float32))
    def surface_z(s, x, y):
        i = np.clip(((np.asarray(x) - X0) / RES).astype(int), 0, NX - 1); j = np.clip(((np.asarray(y) - X0) / RES).astype(int), 0, NY - 1)
        col = s.F[i, j, :] < 0; top = NZ - 1 - np.argmax(col[..., ::-1], axis=-1); return np.where(col.any(-1), ZS[top], 0.0)
    def add_rib(s, name, xy, r0=8.0, r1=5.0, lift=3.0, k=8.0):
        """strand riding the current surface along an xy polyline."""
        c, t, L = curve([(x, y, 0.0) for x, y in xy], 2.0); zz = s.surface_z(c[:, 0], c[:, 1]); zz = ndi.gaussian_filter1d(zz, 14, mode='nearest'); c[:, 2] = zz + lift - 0.5 * r0
        r = r0 + (r1 - r0) * t; s.sweep(name, c, r, k, store=False, kind=4)
    def add_web(s, poly, anchors, sag=0.22, th=8.0, cell=46.0, sw=9.0, rim=9.0, seed=0, k=5.0, zmin=5.0):
        """lace membrane: xy polygon, z surface = IDW of anchor points minus sag*distance, Worley lace holes (strand width sw), solid rim."""
        poly = np.asarray(poly, float); lo = poly.min(0) - 12; hi = poly.max(0) + 12
        i0 = int((lo[0] - X0) // RES); i1 = int((hi[0] - X0) // RES) + 2; j0 = int((lo[1] - X0) // RES); j1 = int((hi[1] - X0) // RES) + 2
        i0, j0 = max(i0, 0), max(j0, 0); i1, j1 = min(i1, NX), min(j1, NY)
        im = Image.new('L', (i1 - i0, j1 - j0), 0); ImageDraw.Draw(im).polygon([((x - X0) / RES - i0, (y - X0) / RES - j0) for x, y in poly], fill=255)
        reg = np.asarray(im).T > 0; din = ndi.distance_transform_edt(reg) * RES; dout = ndi.distance_transform_edt(~reg) * RES; qreg = dout - din
        Xg, Yg = np.meshgrid(XS[i0:i1], YS[j0:j1], indexing='ij'); rng = np.random.default_rng(seed)
        gx = np.arange(lo[0] - cell, hi[0] + cell, cell); gy = np.arange(lo[1] - cell, hi[1] + cell, cell); GX, GY = np.meshgrid(gx, gy)
        pts = np.stack([GX.ravel() + rng.uniform(-.42, .42, GX.size) * cell, GY.ravel() + rng.uniform(-.42, .42, GX.size) * cell], 1)
        dd, _ = cKDTree(pts).query(np.stack([Xg.ravel(), Yg.ravel()], 1), k=2); lace = ((dd[:, 1] - dd[:, 0]) * 0.5 - sw / 2).reshape(Xg.shape)
        q = np.maximum(qreg, np.minimum(lace, din - rim))
        A = np.vstack([curve(a, 4.0)[0] for a in anchors]); tr = cKDTree(A[:, :2]); dA, iA = tr.query(np.stack([Xg.ravel(), Yg.ravel()], 1), k=4)
        w = 1.0 / (dA ** 2 + 4.0); zs_ = (A[iA, 2] * w).sum(1) / w.sum(1); zs_ = np.maximum(zs_ - sag * dA[:, 0], zmin).reshape(Xg.shape)
        k0 = max(int((zs_[reg].min() - th - 8) // RES) + 4, 0) if reg.any() else 0; k1 = min(int((zs_.max() + th + 8) // RES) + 6, NZ)
        Zg = ZS[k0:k1][None, None, :]; val = np.maximum(np.abs(Zg - zs_[..., None]) - th / 2, q[..., None]).astype(np.float32)
        sl = (slice(i0, i1), slice(j0, j1), slice(k0, k1)); s._upd(sl, val, k, 3)
    def finish(s):
        X = XS[:, None, None]; Y = YS[None, :, None]; Z = ZS[None, None, :]
        F = np.maximum(s.F, -Z + 1e-3); F = np.maximum(F, np.maximum(np.abs(X) - HALF, np.maximum(np.abs(Y) - HALF, Z - ZMAX)))
        return F.astype(np.float32)

def ellipsoid(c, a, b, cz):
    def fn(X, Y, Z):
        q = np.sqrt(((X - c[0]) / a) ** 2 + ((Y - c[1]) / b) ** 2 + ((Z - cz[0]) / cz[1]) ** 2); return (q - 1) * min(a, b, cz[1]) * 0.9
    return fn

def almond(cx, cy, w, h, tilt=0.0, wob=0.04, seed=0):
    a, b = w / 2, h / 2; ct, st = np.cos(tilt), np.sin(tilt); ph = np.random.default_rng(seed).uniform(0, 6.28, 3)
    def d2(X, Y):
        dx, dy = X - cx, Y - cy; u = ct * dx + st * dy; v = -st * dx + ct * dy; t = (v / b + 1) / 2
        prof = np.sin(np.pi * np.clip(t, 0, 1) ** 0.82) ** 0.75; th = np.arctan2(v, u)
        wid = a * prof * (1 + wob * np.sin(2 * th + ph[0]) + wob * 0.6 * np.sin(3 * th + ph[1])) + 1e-6
        return np.maximum(np.abs(u) - wid, (np.abs(v / b) - 1) * b) * 0.9
    return d2
