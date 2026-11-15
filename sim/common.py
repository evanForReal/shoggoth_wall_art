"""Shared helpers: params / loadcases loading, centerline, material."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from scipy.interpolate import CubicSpline

ROOT = Path(__file__).resolve().parent.parent
P0 = ROOT / "prototype" / "p0"


def load_json(p):
    return json.loads(Path(p).read_text())


def load_params(path):
    p = load_json(path)
    return p


def load_loadcases(path=None):
    return load_json(path or (P0 / "loadcases.json"))


def material(lc, params):
    name = params.get("material", "PETG")
    if isinstance(name, dict):
        name = name.get("primary", name.get("name", "PETG"))
    m = dict(lc["materials"][name]); m["name"] = name
    m["rho_t_mm3"] = m["rho_g_cm3"] * 1e-9
    return m


def _cl_points(params):
    c = params.get("centerline")
    if isinstance(c, dict):
        c = c.get("points") or c.get("control_points")
    if c is None:
        c = params.get("centerline_points") or params.get("centerline_control_points")
    if c is None:
        return None
    a = np.asarray(c, float)
    return a if a.ndim == 2 and a.shape[1] == 3 else None


class Centerline:
    """arclength-parametrized cubic spline through control points (x,y,z in mm, global frame)."""
    def __init__(self, pts):
        pts = np.asarray(pts, float)
        d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]
        self.cs = CubicSpline(d, pts, bc_type="natural")
        self.length = float(d[-1])
        u = np.linspace(0, self.length, 4001)
        q = self.cs(u)
        seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(q, axis=0), axis=1))]
        self.u = u; self.s_tab = seg; self.L = float(seg[-1])

    def at(self, frac):
        frac = np.atleast_1d(frac)
        u = np.interp(frac * self.L, self.s_tab, self.u)
        p = self.cs(u); t = self.cs(u, 1)
        t = t / np.linalg.norm(t, axis=1, keepdims=True)
        return p, t

    def project(self, xyz):
        """nearest arclength fraction for points (n,3)."""
        from scipy.spatial import cKDTree
        if not hasattr(self, "_tree"):
            self._pts = self.cs(self.u); self._tree = cKDTree(self._pts)
        d, i = self._tree.query(xyz)
        return self.s_tab[i] / self.L, d


def get_centerline(params, manifest=None):
    if manifest and manifest.get("centerline"):
        pts = np.array([c["xyz"] for c in manifest["centerline"]], float)
        return Centerline(pts)
    pts = _cl_points(params)
    return Centerline(pts) if pts is not None else None


def load_manifest(params_path, underlay_path=None):
    """Geometry's geometry_manifest.json if present next to the artifacts (not part of the spec contract; used opportunistically)."""
    cands = []
    if underlay_path:
        cands.append(Path(underlay_path).parent / "geometry_manifest.json")
    cands.append(Path(params_path).parent / "out" / "geometry_manifest.json")
    for c in cands:
        if c.exists():
            return load_json(c)
    return None


def plate_dims(params, manifest=None):
    """(size_y, size_z, thickness, hole_d, pattern_y, pattern_z) tolerant to spec-style and Geometry-style keys."""
    pl = params.get("anchor_plate", {})
    if "size" in pl:
        sy, sz, t = pl["size"]
    else:
        sy, sz, t = pl.get("size_y", 160.0), pl.get("size_z", 110.0), pl.get("thickness", 8.0)
    pat = pl.get("hole_pattern") or [pl.get("pattern_y", 120.0), pl.get("pattern_z", 70.0)]
    return dict(size_y=sy, size_z=sz, thickness=t, hole_d=pl.get("hole_d", pl.get("hole_dia", 6.0)), pattern_y=pat[0], pattern_z=pat[1])


def stub_depth(params):
    b = params.get("body_stub") or {}
    return float(b.get("depth", 0.0)) if isinstance(b, dict) else 0.0


def local_radius(params, frac):
    r0 = params["root_diameter"] / 2; r1 = params["tip_diameter"] / 2
    return r0 + (r1 - r0) * np.asarray(frac)


def layer_dir(params):
    v = params.get("layer_dir")   # spec: vector, or text such as "span axis horizontal within each segment" -> build axis +Z
    if isinstance(v, (list, tuple)) and len(v) == 3:
        v = np.asarray(v, float)
        return v / np.linalg.norm(v)
    return np.array([0.0, 0.0, 1.0])


def screw_positions(params, manifest=None):
    if manifest and manifest.get("anchor", {}).get("holes_yz"):
        h = np.array(manifest["anchor"]["holes_yz"], float)
        return h[np.lexsort((h[:, 1], -h[:, 0]))]      # +Y first
    pd = plate_dims(params)
    py, pz = pd["pattern_y"], pd["pattern_z"]
    return np.array([[sy * py / 2, sz * pz / 2] for sy in (1, -1) for sz in (1, -1)])   # (y,z) pairs; +Y first

TODAY = "2026-11-15"
