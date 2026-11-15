"""Centerline, taper and cross-section family for the P0 span.

Section family: rounded rectangle (A half-width, B half-height, R corner radius).
A=B=R -> circle (tube). Pad: A>>B, small R -> flat top of width 2(A-R).
"""
import numpy as np
from scipy.interpolate import PchipInterpolator

M_SEC = 128  # vertices per section


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
        s = np.arange(-self.neck, L + 40 + ds, ds)
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

    def ABR(self, s, inset=0.0):
        """Outer (inset=0) or inset section params at stations s."""
        s = np.atleast_1d(np.asarray(s, float))
        r = self.radius(s); w = self.pad_w(s)
        A = r + w * (self.pad_A - r)
        B = r + w * (self.pad_B - r)
        R = r + w * (self.pad_R - r)
        if inset:
            A = A - inset; B = B - inset; R = np.maximum(R - inset, 0.5)
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
    A, B, R = span.ABR(s_arr, inset)
    return np.stack([rrect_polygon(a, b, r) for a, b, r in zip(A, B, R)])
