#!/usr/bin/env python3
"""Narrow-depression depth check behind rp2-blind-pockets.md s.3 "Fabrication cross-check".

Step 1 (heightfield): z-buffer of a patch mesh, top surface only, 0.5 mm grid
  python3 heightfield_check.py build <mesh.stl> <tag>     -> H_<tag>.npy
  Inputs used 2026-11-16: gate1c and gate2 preview STLs (decimated, gitignored,
  regenerate with each gate's run script).
Step 2 (stats): narrow (< 6 mm) depression area, depth percentiles, depth-band shares
  python3 heightfield_check.py stats H_gate1c.npy H_gate2.npy > heightfield_check.json
Indicative only: top surface (no undercuts), patch scale, closing width ~ mouth width.
"""
import sys, json
import numpy as np
from scipy import ndimage as ndi

STEP, MARGIN, W = 0.5, 40, 6.0
BANDS = [(0.5, 3), (3, 6), (6, 12), (12, 24), (24, 1e9)]

def disk(r):
    n = int(np.ceil(r / STEP)); y, x = np.mgrid[-n:n + 1, -n:n + 1]
    return (x * x + y * y) * STEP * STEP <= r * r

def build(path, tag):
    import trimesh
    m = trimesh.load(path); b = m.bounds
    P, _ = trimesh.sample.sample_surface(m, 6_000_000, seed=1)
    nx = int((b[1, 0] - b[0, 0]) / STEP) + 1; ny = int((b[1, 1] - b[0, 1]) / STEP) + 1
    ix = ((P[:, 0] - b[0, 0]) / STEP).astype(int); iy = ((P[:, 1] - b[0, 1]) / STEP).astype(int)
    H = np.full((nx, ny), -1.0); np.maximum.at(H, (ix, iy), P[:, 2])
    H = ndi.grey_closing(np.where(H < 0, 0, H), size=(3, 3))
    np.save(f"H_{tag}.npy", H)

def stats(path):
    H = np.load(path)
    core = np.zeros_like(H, bool); core[MARGIN:-MARGIN, MARGIN:-MARGIN] = True
    D = ndi.grey_closing(H, footprint=disk(W / 2)) - H
    sel = core & (D > 0.5); dd = D[sel]
    cm2 = lambda n: round(float(n) * STEP * STEP / 100, 1)
    return {
        "core_area_cm2": cm2(core.sum()),
        "narrow_area_cm2": cm2(sel.sum()),
        "narrow_area_frac": round(float(sel.sum() / core.sum()), 3),
        "depth_p50_p90_p99_max_mm": [round(float(v), 1) for v in np.percentile(dd, [50, 90, 99, 100])],
        "depth_band_share": {f"{lo}-{hi if hi < 1e9 else 'inf'}": round(float(np.mean((dd > lo) & (dd <= hi))), 3) for lo, hi in BANDS},
        "share_le_6mm_deep": round(float(np.mean(dd <= 6)), 3),
        "relief_p10_p50_p90_mm": [round(float(v), 1) for v in np.percentile(H[core], [10, 50, 90])],
    }

if __name__ == "__main__":
    if sys.argv[1] == "build":
        build(sys.argv[2], sys.argv[3])
    else:
        print(json.dumps({p.split("/")[-1]: stats(p) for p in sys.argv[2:]}, indent=1))
