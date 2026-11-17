"""Figure-first SDF engine: variable-radius sweeps along 3D splines, smooth-min blends, flat back, hard envelope clip."""
import numpy as np
from scipy.interpolate import splprep, splev
from scipy.spatial import cKDTree
RES = 3.0; HALF = 457.0; ZMAX = 300.0
XS = np.arange(-468, 468 + 1e-6, RES); YS = XS.copy(); ZS = np.arange(-9, 312 + 1e-6, RES)
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
    """c01/feature-ref taper: w=w0(1-s)^0.75 to s=.88 then linear to the tip floor."""
    t = np.asarray(t, float); a = r0 * np.clip(1 - t, 0, 1) ** p
    r88 = r0 * 0.12 ** p
    lin = r88 + (r_tip - r88) * np.clip((t - 0.88) / 0.12, 0, 1)
    return np.maximum(np.where(t <= 0.88, a, lin), r_tip)

def apply_wave(c, t, wave):
    if not wave: return c
    A, cyc, ph, tmax = wave; tg = np.gradient(c[:, :2], axis=0); tg /= np.linalg.norm(tg, axis=1)[:, None] + 1e-9
    win = np.sin(np.pi * np.clip(t / tmax, 0, 1)) * (t < tmax); off = A * np.sin(cyc * np.pi * t / tmax + ph) * win
    c = c.copy(); c[:, 0] += -tg[:, 1] * off; c[:, 1] += tg[:, 0] * off
    return c

class Field:
    def __init__(s):
        s.F = np.full((NX, NY, NZ), 1e3, np.float32); s.parts = {}
    def _crop(s, lo, hi):
        i0 = max(int((lo[0] + 468) // RES), 0); i1 = min(int((hi[0] + 468) // RES) + 2, NX)
        j0 = max(int((lo[1] + 468) // RES), 0); j1 = min(int((hi[1] + 468) // RES) + 2, NY)
        k0 = max(int((lo[2] + 9) // RES), 0); k1 = min(int((hi[2] + 9) // RES) + 2, NZ)
        return (slice(i0, i1), slice(j0, j1), slice(k0, k1))
    def grid(s, sl):
        X, Y, Z = np.meshgrid(XS[sl[0]], YS[sl[1]], ZS[sl[2]], indexing='ij'); return X, Y, Z
    def add_sweep(s, name, pts, rfun, k=30.0, zs=1.0, pad=None, wave=None):
        c, t, L = curve(pts)
        c = apply_wave(c, t, wave)
        if False:   # lateral S-wave in the wall plane: A mm, half-cycles, phase, window end tmax (root and window end unchanged)
            A, cyc, ph, tmax = wave; tg = np.gradient(c[:, :2], axis=0); tg /= np.linalg.norm(tg, axis=1)[:, None] + 1e-9
            win = np.sin(np.pi * np.clip(t / tmax, 0, 1)) ** 1.0 * (t < tmax)
            off = A * np.sin(cyc * np.pi * t / tmax + ph) * win
            c = c.copy(); c[:, 0] += -tg[:, 1] * off; c[:, 1] += tg[:, 0] * off
        r = rfun(t); rm = r.max()
        pad = pad if pad is not None else rm + k + 8
        lo = c.min(0) - pad; hi = c.max(0) + pad
        if zs > 1: lo[2] = -9; hi[2] = c[:, 2].max() + (rm + k + 8) / zs
        sl = s._crop(lo, hi); X, Y, Z = s.grid(sl)
        P = np.stack([X.ravel(), Y.ravel(), Z.ravel() * zs], 1)
        cs = c.copy(); cs[:, 2] *= zs
        d, idx = cKDTree(cs).query(P, workers=-1)
        v = (d - r[idx]).reshape(X.shape).astype(np.float32)
        s.F[sl] = smin(s.F[sl], v, k).astype(np.float32)
        s.parts[name] = dict(c=c, t=t, r=r, L=L, zs=zs)
        return c, t, r, L
    def add_fn(s, lo, hi, fn, k=30.0):
        sl = s._crop(lo, hi); X, Y, Z = s.grid(sl)
        s.F[sl] = smin(s.F[sl], fn(X, Y, Z).astype(np.float32), k).astype(np.float32)
    def carve(s, lo, hi, fn):
        sl = s._crop(lo, hi); X, Y, Z = s.grid(sl)
        s.F[sl] = np.maximum(s.F[sl], -fn(X, Y, Z).astype(np.float32))
    def finish(s):
        X, Y, Z = np.meshgrid(XS, YS, ZS, indexing='ij')
        F = np.maximum(s.F, -Z + 1e-3)
        F = np.maximum(F, np.maximum(np.abs(X) - HALF, np.maximum(np.abs(Y) - HALF, Z - ZMAX)))
        return F.astype(np.float32)

def ellipsoid(c, a, b, cz):
    def fn(X, Y, Z):
        q = np.sqrt(((X - c[0]) / a) ** 2 + ((Y - c[1]) / b) ** 2 + ((Z - cz[0]) / cz[1]) ** 2)
        return (q - 1) * min(a, b, cz[1]) * 0.9
    return fn

def almond(cx, cy, w, h, tilt=0.0, wob=0.04, seed=0, upper=0.4):
    """vertical almond (lens, heavier upper third), w:h ~ 1:1.5; w,h full dims. Returns xy-distance fn (neg inside)."""
    a, b = w / 2, h / 2; ct, st = np.cos(tilt), np.sin(tilt)
    rng = np.random.default_rng(seed); ph = rng.uniform(0, 6.28, 3)
    def d2(X, Y):
        dx, dy = X - cx, Y - cy
        u = ct * dx + st * dy; v = -st * dx + ct * dy
        vn = v / b
        sh = np.where(vn > 0, 1.0, 1.0)
        # widest point 40% from top: shift
        t = (vn + 1) / 2                      # 0 bottom .. 1 top
        prof = np.sin(np.pi * np.clip(t, 0, 1) ** 0.82) ** 0.75   # lens profile, widest high
        th = np.arctan2(v, u)
        wb = 1 + wob * np.sin(2 * th + ph[0]) + wob * 0.6 * np.sin(3 * th + ph[1])
        wid = a * prof * wb + 1e-6
        dist_u = (np.abs(u) - wid)
        dist_v = (np.abs(vn) - 1) * b
        return np.maximum(dist_u, dist_v) * 0.9 + 0 * sh
    return d2
