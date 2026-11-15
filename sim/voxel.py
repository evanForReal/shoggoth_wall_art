"""Voxel rasterizer shared by FEA and printcheck.

Signed-winding raster of a closed triangle mesh on a regular grid (ray parity along +X).
Handles internal cavities (hollow shells) correctly: occupancy = winding == 1.
Cells with winding not in {0,1} flag self-overlap / inverted shells.
"""
from __future__ import annotations
import numpy as np
import trimesh

JIT = (0.0137, 0.0291)  # sub-cell jitter (grid units) to avoid exact edge hits


class Grid:
    def __init__(self, origin, pitch, shape):
        self.origin = np.asarray(origin, float)
        self.pitch = float(pitch)
        self.shape = tuple(int(s) for s in shape)

    @classmethod
    def from_bounds(cls, lo, hi, pitch, pad=1):
        lo = np.asarray(lo, float); hi = np.asarray(hi, float)
        origin = lo - pad * pitch
        shape = np.ceil((hi - origin) / pitch).astype(int) + pad
        return cls(origin, pitch, shape)

    def centers(self, idx):
        return self.origin + (np.asarray(idx, float) + 0.5) * self.pitch


def load_mesh(path) -> trimesh.Trimesh:
    m = trimesh.load(str(path), force="mesh", process=False)
    return m


def winding_raster(mesh: trimesh.Trimesh, grid: Grid, max_cand=15_000_000) -> np.ndarray:
    """int8 winding number at each cell center, shape grid.shape."""
    nx, ny, nz = grid.shape
    p = grid.pitch
    tri = (mesh.triangles - grid.origin) / p            # grid units
    nrm_x = mesh.face_normals[:, 0]
    # use geometric normal from vertices (robust even if face_normals unreliable)
    e1 = tri[:, 1] - tri[:, 0]; e2 = tri[:, 2] - tri[:, 0]
    nvec = np.cross(e1, e2)
    nrm_x = nvec[:, 0]
    y = tri[:, :, 1]; z = tri[:, :, 2]
    # projected signed area (2x) in YZ
    a2 = (y[:, 1] - y[:, 0]) * (z[:, 2] - z[:, 0]) - (y[:, 2] - y[:, 0]) * (z[:, 1] - z[:, 0])
    ok = np.abs(a2) > 1e-12
    j0 = np.ceil(y.min(1) - 0.5 - JIT[0]).astype(int); j1 = np.floor(y.max(1) - 0.5 - JIT[0]).astype(int)
    k0 = np.ceil(z.min(1) - 0.5 - JIT[1]).astype(int); k1 = np.floor(z.max(1) - 0.5 - JIT[1]).astype(int)
    j0 = np.maximum(j0, 0); k0 = np.maximum(k0, 0)
    j1 = np.minimum(j1, ny - 1); k1 = np.minimum(k1, nz - 1)
    cnt = np.maximum(j1 - j0 + 1, 0) * np.maximum(k1 - k0 + 1, 0)
    cnt[~ok] = 0
    ids = np.nonzero(cnt)[0]
    diff = np.zeros((ny * nz * (nx + 1),), np.int8)
    csum = np.cumsum(cnt[ids])
    start = 0
    while start < len(ids):
        base = csum[start - 1] if start else 0
        end = np.searchsorted(csum, base + max_cand, side="right")
        end = max(end, start + 1)
        t = ids[start:end]
        c = cnt[t]
        rep = np.repeat(np.arange(len(t)), c)
        off = np.arange(c.sum()) - np.repeat(np.cumsum(c) - c, c)
        nk = (k1[t] - k0[t] + 1)[rep]
        jj = j0[t][rep] + off // nk
        kk = k0[t][rep] + off % nk
        cy = jj + 0.5 + JIT[0]; cz = kk + 0.5 + JIT[1]
        tt = t[rep]
        y0 = y[tt, 0]; z0 = z[tt, 0]
        y1 = y[tt, 1]; z1 = z[tt, 1]
        y2 = y[tt, 2]; z2 = z[tt, 2]
        d = a2[tt]
        l1 = ((cy - y0) * (z2 - z0) - (y2 - y0) * (cz - z0)) / d
        l2 = ((y1 - y0) * (cz - z0) - (cy - y0) * (z1 - z0)) / d
        l0 = 1 - l1 - l2
        inside = (l0 >= 0) & (l1 >= 0) & (l2 >= 0)
        tt = tt[inside]; l0 = l0[inside]; l1 = l1[inside]; l2 = l2[inside]
        jj = jj[inside]; kk = kk[inside]
        xh = l0 * tri[tt, 0, 0] + l1 * tri[tt, 1, 0] + l2 * tri[tt, 2, 0]
        ci = np.clip(np.floor(xh - 0.5).astype(int) + 1, 0, nx)
        delta = np.where(nrm_x[tt] < 0, 1, -1).astype(np.int8)
        flat = (jj * nz + kk) * (nx + 1) + ci
        np.add.at(diff, flat, delta)
        start = end
    w = np.cumsum(diff.reshape(ny, nz, nx + 1), axis=2, dtype=np.int8)[:, :, :nx]
    return np.ascontiguousarray(w.transpose(2, 0, 1))


def occupancy(mesh, pitch, grid=None, pad=1):
    """Returns (occ bool, anomalies int count, Grid)."""
    if grid is None:
        b = mesh.bounds
        grid = Grid.from_bounds(b[0], b[1], pitch, pad)
    w = winding_raster(mesh, grid)
    occ = w == 1
    bad = int(((w != 0) & (w != 1)).sum())
    return occ, bad, grid
