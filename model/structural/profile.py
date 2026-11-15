"""Centerline, taper and cross-section family for the P0 span.

Section family: rounded rectangle (A half-width, B half-height, R corner radius).
A=B=R -> circle (tube). Pad: A>>B, small R -> flat top of width 2(A-R).
"""
import numpy as np
from scipy.interpolate import PchipInterpolator

M_SEC = 128  # vertices per section
WALL_BOOST = 1.03  # margin on normal wall thickness (mesh chord error; tuned against the ray-cast check)


def smoothstep(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


class Span:
    def __init__(self, p):
        self.p = p
        L = p["span_length"]
        self.L = L
        cl = p["centerline"]
        self.neck = cl["neck_len"]
        hk = np.array(cl["heading_knots_deg"], float)
        zk = np.array(cl["z_knots"], float)
        self._head = PchipInterpolator(hk[:, 0], np.radians(hk[:, 1]))
        self._z = PchipInterpolator(zk[:, 0], zk[:, 1])
        # integrate plan path on fine grid (s measured from root, root at s=0)
        ds = 0.25
        s = np.arange(-self.neck - 25.0, L + 40 + ds, ds)
        sf = np.clip(s / L, 0, 1)
        th = np.where(s < 0, np.radians(hk[0, 1]), self._head(sf))
        x = np.empty_like(s); y = np.empty_like(s)
        x0, y0, _ = cl["root_xyz"]
        i0 = np.searchsorted(s, 0.0)
        x[i0] = x0; y[i0] = y0
        for i in range(i0 + 1, len(s)):
            x[i] = x[i - 1] + ds * 0.5 * (np.cos(th[i]) + np.cos(th[i - 1]))
            y[i] = y[i - 1] + ds * 0.5 * (np.sin(th[i]) + np.sin(th[i - 1]))
        for i in range(i0 - 1, -1, -1):
            x[i] = x[i + 1] - ds * 0.5 * (np.cos(th[i]) + np.cos(th[i + 1]))
            y[i] = y[i + 1] - ds * 0.5 * (np.sin(th[i]) + np.sin(th[i + 1]))
        z = np.where(s < 0, cl["root_xyz"][2], self._z(sf))
        self._s = s
        self._xyz = np.column_stack([x, y, z])
        # arc length in 3D differs slightly from s (z rise); stations are by s (plan arc)
        sh = p["shelf"]
        self.s_pad0 = sh["plateau_start_frac"] * L
        self.s_pad1 = sh["plateau_end_frac"] * L
        self.ramp_up0 = sh["ramp_up_start_frac"] * L
        self.ramp_dn1 = sh["ramp_down_end_frac"] * L
        self.pad_A = sh["half_width"]; self.pad_R = sh["corner_radius"]; self.pad_B = sh["half_height"]
        self.r_root = p["root_diameter"] / 2; self.r_tip = p["tip_diameter"] / 2
        self.t = p["shell_wall"]
        self._g = None

    # --- centerline -------------------------------------------------------
    def point(self, s):
        s = np.asarray(s, float)
        return np.column_stack([np.interp(s, self._s, self._xyz[:, k]) for k in range(3)])

    def tangent(self, s):
        e = 0.5
        d = self.point(np.asarray(s, float) + e) - self.point(np.asarray(s, float) - e)
        return d / np.linalg.norm(d, axis=-1, keepdims=True)

    def frame(self, s):
        T = self.tangent(s)
        Z = np.array([0, 0, 1.0])
        N = np.cross(Z, T); N /= np.linalg.norm(N, axis=-1, keepdims=True)
        U = np.cross(T, N)
        return T, N, U

    # --- section parameters ----------------------------------------------
    def radius(self, s):
        f = np.clip(np.asarray(s, float) / self.L, 0, 1)
        return self.r_root + (self.r_tip - self.r_root) * f

    def pad_w(self, s):
        s = np.asarray(s, float)
        up = smoothstep((s - self.ramp_up0) / (self.s_pad0 - self.ramp_up0))
        dn = 1 - smoothstep((s - self.s_pad1) / (self.ramp_dn1 - self.s_pad1))
        return np.minimum(up, dn)

    def _outer_ABR(self, s):
        s = np.atleast_1d(np.asarray(s, float))
        r = self.radius(s); w = self.pad_w(s)
        return (r + w * (self.pad_A - r), r + w * (self.pad_B - r), r + w * (self.pad_R - r))

    # --- exact normal-offset (shell inner) sections ----------------------------------------------------------
    def _grid(self):
        """Outer surface on a fine s grid: 3D points X (g,M,3) and outward unit normals n3 (g,M,3), cached."""
        if self._g is not None:
            return self._g
        sg = np.arange(-self.neck - 15.0, self.L + 30.0, 0.25)
        P = np.stack([rrect_polygon(a, b, r) for a, b, r in zip(*self._outer_ABR(sg))])
        T, N, U = self.frame(sg)
        X = self.point(sg)[:, None, :] + P[:, :, 0:1] * N[:, None, :] + P[:, :, 1:2] * U[:, None, :]
        dXds = np.gradient(X, sg, axis=0)
        t2 = np.roll(P, -1, axis=1) - np.roll(P, 1, axis=1)
        dXdph = t2[:, :, 0:1] * N[:, None, :] + t2[:, :, 1:2] * U[:, None, :]
        n3 = np.cross(dXds, dXdph)
        n3 /= np.linalg.norm(n3, axis=-1, keepdims=True)
        n2 = np.stack([t2[:, :, 1], -t2[:, :, 0]], axis=-1)
        n2_3d = n2[:, :, 0:1] * N[:, None, :] + n2[:, :, 1:2] * U[:, None, :]
        n3 *= np.sign(np.sum(n3 * n2_3d, axis=-1, keepdims=True))        # outward
        self._g = (sg, X, n3)
        return self._g

    def inset_polygons(self, s_arr, d):
        """Inner section polygons (n, M, 2) whose loft is the exact normal offset (distance d*WALL_BOOST) of the outer
        loft. The wall is realised as per-station in-plane sections (perpendicular to T) but, where the outer surface is
        inclined (shelf ramps, taper, tip cap ramp) or the centerline bends, an in-plane inset of d would give only
        d*cos(theta). So: offset the outer surface points along their 3D normals (Q = X - d n3), then for each polygon
        vertex index j intersect the offset curve Q_j(s) with the station plane and take its in-plane coordinates."""
        s_arr = np.atleast_1d(np.asarray(s_arr, float))
        sg, X, n3 = self._grid()
        dd = d * WALL_BOOST
        Q = X - dd * n3
        W = int((2.2 * dd + 6.0) / 0.25)
        out = np.empty((len(s_arr), X.shape[1], 2))
        T, N, U = self.frame(s_arr); C = self.point(s_arr)
        for i, sv in enumerate(s_arr):
            i0 = int(np.searchsorted(sg, sv))
            lo, hi = max(i0 - W, 0), min(i0 + W + 1, len(sg))
            f = np.einsum("gjk,k->gj", Q[lo:hi] - C[i], T[i])                 # signed distance to station plane
            k = np.clip((f < 0).sum(axis=0), 1, f.shape[0] - 1)               # crossing between k-1 and k
            jj = np.arange(X.shape[1])
            f0, f1 = f[k - 1, jj], f[k, jj]
            w = np.clip(-f0 / np.where(np.abs(f1 - f0) < 1e-12, 1e-12, f1 - f0), 0, 1)
            q = Q[lo:hi][k - 1, jj] * (1 - w)[:, None] + Q[lo:hi][k, jj] * w[:, None]
            r = q - C[i]
            out[i, :, 0] = r @ N[i]; out[i, :, 1] = r @ U[i]
        return out

    def ABR(self, s, inset=0.0):
        """Outer (inset=0) or inset section params (A, B, R) at stations s, for symmetric rounded-rect prisms (ribs,
        rails, joint dims). Inset = normal wall thickness; side/top half-extents taken as the minimum over the opposite
        vertices, so rib members always overlap the wall rather than floating off it."""
        s = np.atleast_1d(np.asarray(s, float))
        A, B, R = self._outer_ABR(s)
        if inset:
            Pin = self.inset_polygons(s, inset)
            h = M_SEC // 2; q = M_SEC // 4
            Ain = np.minimum(Pin[:, 0, 0], -Pin[:, h, 0]); Bin = np.minimum(Pin[:, q, 1], -Pin[:, q + h, 1])
            iA = A - Ain; iB = B - Bin
            A, B, R = Ain, Bin, np.maximum(R - np.maximum(iA, iB), 0.5)
        return A, B, R

    def top_plane_z(self):
        zc = float(self.point(0.5 * (self.s_pad0 + self.s_pad1))[0, 2])
        return zc + self.pad_B


def rrect_polygon(A, B, R, m=M_SEC):
    """Polar-sampled rounded-rectangle boundary, CCW, starting at +x. Returns (m,2).
    Vectorised bisection on the rounded-box SDF."""
    th = np.linspace(0, 2 * np.pi, m, endpoint=False)
    d = np.column_stack([np.cos(th), np.sin(th)])
    Rr = min(R, A - 1e-6, B - 1e-6)
    hx, hy = A - Rr, B - Rr

    def sdf(p):
        q = np.abs(p) - np.array([hx, hy])
        return np.linalg.norm(np.maximum(q, 0), axis=1) + np.minimum(np.maximum(q[:, 0], q[:, 1]), 0) - Rr

    lo = np.zeros(m); hi = np.full(m, 2 * max(A, B) + 1)
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        inside = sdf(d * mid[:, None]) < 0
        lo = np.where(inside, mid, lo); hi = np.where(inside, hi, mid)
    return d * (0.5 * (lo + hi))[:, None]


def section_profiles(span, s_arr, inset=0.0):
    """(n, M, 2) section polygons. inset>0: exact-normal-offset inner sections (Span.inset_polygons)."""
    s_arr = np.atleast_1d(np.asarray(s_arr, float))
    if not inset:
        return np.stack([rrect_polygon(a, b, r) for a, b, r in zip(*span._outer_ABR(s_arr))])
    return span.inset_polygons(s_arr, inset)
