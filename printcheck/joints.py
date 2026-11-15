"""Joint-fit / clearance check between two segment meshes in assembled pose."""
from __future__ import annotations
import numpy as np
import trimesh
import manifold3d as m3d
from scipy.spatial import cKDTree
from .checks import LIM


def _man(m):
    return m3d.Manifold(m3d.Mesh(np.asarray(m.vertices, np.float32), np.asarray(m.faces, np.uint32)))


def joint_fit(A: trimesh.Trimesh, B: trimesh.Trimesh, search_mm=2.0, spacing=0.2):
    lo = np.maximum(A.bounds[0], B.bounds[0]) - search_mm; hi = np.minimum(A.bounds[1], B.bounds[1]) + search_mm
    if (hi < lo).any():
        return {"mating": False}
    try:
        inter = float((_man(A) ^ _man(B)).volume())      # manifold3d: ^ is intersection
    except Exception:
        inter = float("nan")
    area_tot = A.area + B.area
    def samp(M):
        n = int(min(max(M.area / spacing ** 2, 1000), 2_500_000))
        pts, _ = trimesh.sample.sample_surface(M, n, seed=0)
        keep = ((pts >= lo) & (pts <= hi)).all(1)
        return pts[keep]
    pa, pb = samp(A), samp(B)
    if len(pa) == 0 or len(pb) == 0:
        return {"mating": False}
    tb = cKDTree(pb)
    d, _ = tb.query(pa)
    mate = d < search_mm
    if mate.sum() < 20:
        return {"mating": False}
    dm = d[mate]
    # sampling spacing bias: nearest-sample distance overestimates true gap by up to ~spacing/2
    acc = LIM["joint_clearance_accept_mm"]
    gap_min = float(dm.min()); p5 = float(np.percentile(dm, 5)); med = float(np.median(dm))
    edges = [0.0, 0.05, 0.15, acc[1], 1e9]
    names = ["abut(<0.05)", "tight(0.05-0.15)", f"fit(0.15-{acc[1]})", "loose(>%s)" % acc[1]]
    h, _ = np.histogram(dm, bins=edges); fr = (h / h.sum()).round(3)
    bands = dict(zip(names, fr.tolist()))
    ok = bool((inter != inter or inter < 5.0) and fr[1] < 0.10 and fr[3] < 0.10 and fr[2] > 0.05)
    return {"mating": True, "interference_mm3": inter, "gap_min_mm": gap_min, "gap_p5_mm": p5, "gap_median_mm": med, "n_mating_samples": int(mate.sum()),
            "band_fractions": bands, "center": pa[mate].mean(0).round(1).tolist(), "pass": ok, "note": f"sample spacing {spacing} mm (gap resolution +-{spacing/2:.2f}); pass = interference<5 mm3 (float32 boolean noise), tight band(0.05-0.15) <10 %, loose band <10 %, fit band >5 % (zero-gap abutting faces are treated as intended)"}
