"""r12s volumetric smiley mask: sphere / oblate spheroid held up by the rod-cored tentacle (Structural mask-arm-v1.md S1-S10 architecture kept:
separate bonded keyed mask part, pad 70 dia on the ball's back with a flat face, D-flat spigot socket, 44 mm rod bore).
Local frame (heldmask.loc): u right, v up, w out of the wall (viewer side). Ellipsoid semi-axes a (u, v) = D/2 and c (w) = ratio * D/2.
Smiley features are CARVED into the curved front (recess floor follows the surface at a depth, walls along w); weathered edges; no applied parts.
Grips: 'F' -> six cupping tendrils over the back / sides (rim fingers on a disc), 'C' -> one tentacle wrapped round the equator (coil), 'E' -> tentacle threaded through a bored left eye hole."""
import numpy as np
from scipy.spatial import cKDTree
import heldmask as hm

DEPTH_EYE, DEPTH_MOUTH = 0.052, 0.040         # recess depth, fraction of D (8.6 / 6.6 mm at D 165)
EYE_HOLE_SCALE = (0.115, 0.21)                # E grip: left eye bored to w, h (fractions of D)

class Features:
    def __init__(self, D, ratio=1.0, grip='F'):
        self.D, self.ratio, self.grip = D, ratio, grip; self.a = D / 2.0; self.c = ratio * D / 2.0
        # smile: arc through L end, bottom, R end (D units); thin groove tapering to the ends
        P = np.array([[-0.265, -0.062], [0.004, -0.208], [0.265, -0.046]]) * D
        M = np.c_[2 * P[:, 0], 2 * P[:, 1], np.ones(3)]; sol = np.linalg.solve(M, (P ** 2).sum(1)); cx, cy = sol[0], sol[1]; Rr = np.sqrt(sol[2] + cx ** 2 + cy ** 2)
        a0 = np.arctan2(P[0, 1] - cy, P[0, 0] - cx); a1 = np.arctan2(P[2, 1] - cy, P[2, 0] - cx); am = np.arctan2(P[1, 1] - cy, P[1, 0] - cx)
        lo, hi = sorted([a0, a1]); ang = np.linspace(lo, hi, 500) if lo <= am <= hi else np.linspace(hi, lo + 2 * np.pi, 500)
        self.arc = np.stack([cx + Rr * np.cos(ang), cy + Rr * np.sin(ang)], 1); self.tree = cKDTree(self.arc); self.stroke = 0.046 * D
        self.eyes = [(-0.150, 0.125, 0.078, 0.176, np.radians(3.0)), (0.150, 0.125, 0.082, 0.186, np.radians(-3.0))]
        if grip == 'E': self.eyes[0] = (-0.150, 0.125, EYE_HOLE_SCALE[0], EYE_HOLE_SCALE[1], np.radians(3.0))
    # ---- 2D footprint (negative inside), weathered edge
    def _noise(self, u, v):
        D = self.D; return 0.007 * D * (np.sin(37 * u / D + 1.3 * np.cos(23 * v / D)) + 0.7 * np.sin(53 * v / D + 2.0 * np.sin(31 * u / D)))
    def sd(self, u, v):
        D = self.D; out = np.full(np.shape(u), 1e3)
        for ex, ey, w, h, rot in self.eyes:
            ct, st = np.cos(rot), np.sin(rot); uu = ct * (u - ex * D) + st * (v - ey * D); vv = -st * (u - ex * D) + ct * (v - ey * D)
            out = np.minimum(out, (np.sqrt((uu / (w * D / 2)) ** 2 + (vv / (h * D / 2)) ** 2) - 1) * (w * D / 2))
        d, idx = self.tree.query(np.stack([np.ravel(u), np.ravel(v)], 1)); t = idx / (len(self.arc) - 1.0); wid = self.stroke * (0.50 + 0.50 * np.sin(np.pi * t) ** 0.7)
        out = np.minimum(out, (d - wid / 2).reshape(np.shape(u)))
        return out + self._noise(u, v)
    def depth(self, u, v):
        D = self.D; return D * (DEPTH_EYE * (1 + 0.18 * np.sin(17 * u / D + 0.7) * np.cos(13 * v / D)))
    def hf(self, u, v): return self.c * np.sqrt(np.clip(1 - (u / self.a) ** 2 - (v / self.a) ** 2, 0, 1))
    def carve_fn(self, G):
        def fn(X, Y, Z):
            u, v, w = hm.loc(G, X, Y, Z); fl = self.hf(u, v) - self.depth(u, v); out = np.maximum(self.sd(u, v), fl - w)
            if self.grip == 'E':      # bored hole: left eye through the full thickness (the tentacle passes through)
                ex, ey, ww, hh, rot = self.eyes[0]; D = self.D; ct, st = np.cos(rot), np.sin(rot); uu = ct * (u - ex * D) + st * (v - ey * D); vv = -st * (u - ex * D) + ct * (v - ey * D)
                hole = (np.sqrt((uu / (ww * D / 2)) ** 2 + (vv / (hh * D / 2)) ** 2) - 1) * (ww * D / 2)
                out = np.minimum(out, np.maximum(hole, np.abs(w) - (self.c + 3.0)))
            return out
        return fn
    def fv(self, G, x, y, z):
        """render label: negative on carved recess floors (near-black), ~0 on their walls"""
        u, v, w = hm.loc(G, x, y, z); below = self.hf(u, v) - w; return np.maximum(self.sd(u, v), 1.5 - below)

def pt(F, th, ph, off):
    """point on the ellipsoid at azimuth th, polar angle ph from the back pole (ph = pi/2 equator), offset along the outward normal (local u, v, w)"""
    a, c = F.a, F.c; u = a * np.sin(ph) * np.cos(th); v = a * np.sin(ph) * np.sin(th); w = -c * np.cos(ph)
    n = np.array([u / a ** 2, v / a ** 2, w / c ** 2]); n /= np.linalg.norm(n); return (u + off * n[0], v + off * n[1], w + off * n[2])

def add_cup(fld, G, F):
    """six tendrils fan out from the pad over the back and round the sides; tips hook over the equator onto the front rim (q >= 0.93, clear of the face)"""
    bu, bv = G['H']['boss']; thb = np.arctan2(bv, bu); phb = np.arcsin(min(np.hypot(bu, bv) / F.a, 0.9)); out = []
    rng = np.random.default_rng(5)
    for j, dl in enumerate([-122, -76, -30, 30, 76, 122]):
        pts = []; ph_end = np.radians(100 + 3 * (j % 3) + (4 if abs(dl) > 100 else 0)); th_end = thb + np.radians(dl)
        for t in np.linspace(0, 1, 9):
            s = t * t * (3 - 2 * t); th = thb + (th_end - thb) * (0.25 * t + 0.75 * s); ph = phb + (ph_end - phb) * t ** 0.85
            rt = 9.0 - 5.0 * t; pts.append(pt(F, th + rng.uniform(-0.02, 0.02), ph, 0.55 * rt))
        out.append(dict(kind='cup', length=hm._tube(fld, f'cup{j}', pts, 9.0, 3.8, k=4.0, G=G, rmin=3.8)))
    return out

def add_wrap(fld, G, F):
    """one tentacle from the pad up the back to the equator, 1.15 turns round the equator band, tip resting on the front rim"""
    bu, bv = G['H']['boss']; thb = np.arctan2(bv, bu); phb = np.arcsin(min(np.hypot(bu, bv) / F.a, 0.9)); pts = []; th0 = thb - np.radians(55)
    for t in np.linspace(0, 0.18, 4): pts.append(pt(F, thb + (th0 - thb) * (t / 0.18), phb + (np.radians(88) - phb) * (t / 0.18) ** 0.8, 5.0))
    n = 30
    for i in range(1, n + 1):
        t = i / n; th = th0 - 1.15 * 2 * np.pi * t; ph = np.radians(88 + 18 * t ** 1.3 + 4 * np.sin(3 * np.pi * t)); rt = 9.5 - 4.5 * t; pts.append(pt(F, th, ph, 0.5 * rt))
    pts = [pts[0]] + [p for i, p in enumerate(pts[1:], 1) if np.linalg.norm(np.array(p) - np.array(pts[i - 1])) > 1.5]
    return [dict(kind='wrap', length=hm._tube(fld, 'wrap', pts, 9.5, 4.5, k=3.0, G=G, rmin=4.2))]

def add_thread(fld, G, F):
    """tentacle from the pad along the back to the bored left eye hole, through it, over the face rim-ward and down to the left rim"""
    D = F.D; bu, bv = G['H']['boss']; ex, ey = F.eyes[0][0] * D, F.eyes[0][1] * D; r_hole = min(F.eyes[0][2] * D / 2, F.eyes[0][3] * D / 2) - 2.5; r0 = min(6.0, r_hole); hb = lambda u, v: float(np.sqrt(max(1 - (u / F.a) ** 2 - (v / F.a) ** 2, 0)) * F.c)
    pts = [(bu * 0.6, bv * 0.6, -hb(bu * 0.6, bv * 0.6) - 6), ((bu + ex) * 0.5, (bv + ey) * 0.5, -hb((bu + ex) * 0.5, (bv + ey) * 0.5) - 8), (ex, ey - 2, -hb(ex, ey) - 5), (ex, ey, -0.35 * hb(ex, ey)), (ex, ey, 0.35 * hb(ex, ey)), (ex, ey, hb(ex, ey) + 0.8 * r0)]
    for du, dv in [(-0.075, 0.035), (-0.14, 0.0), (-0.21, -0.07), (-0.255, -0.15)]:
        u, v = ex + du * D, ey + dv * D; pts.append((u, v, hb(u, v) + 0.7 * r0))
    return [dict(kind='thread', length=hm._tube(fld, 'thread', pts, r0, 0.7 * r0, k=3.0, G=G, rmin=3.6))]

def add_ball(fld, G, F, part='main'):
    """ball + pad (+ grip + carved smiley); part='mask' adds the D-flat spigot socket and rod bore (the isolated mask part)"""
    R = G['R']; c = G['c3']; mfn = hm.mask_sdf_fn(G); ext = R + 40; lo = (c[0] - ext, c[1] - ext, c[2] - ext); hi = (c[0] + ext, c[1] + ext, c[2] + ext)
    fld.add_fn(lo, hi, mfn, k=6, kind=6); hm.add_pad(fld, G); fld.carve(lo, hi, F.carve_fn(G))
    grip = G['H'].get('grip', 'F'); info = add_cup(fld, G, F) if grip == 'F' else (add_wrap(fld, G, F) if grip == 'C' else add_thread(fld, G, F))
    if part == 'mask':
        def sock(X, Y, Z):
            s, r, U, V = hm.axc(G, X, Y, Z); a = np.maximum(np.maximum(r - hm.SPIG_R, U - hm.FLAT), np.maximum(G['s_T'] - s, s - (G['s_T'] + hm.SPIG_L))); b = np.maximum(r - hm.BORE_D / 2, np.maximum(G['s_T'] - s, s - (G['s_T'] + hm.MASK_BORE))); return np.minimum(a, b)
        T = G['T']; fld.carve((T[0] - 60, T[1] - 60, T[2] - 40), (T[0] + 60, T[1] + 60, T[2] + 90), sock)
    return info
