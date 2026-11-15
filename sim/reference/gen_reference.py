"""Reference articles for harness validation (independent of Geometry's P0).

tapered_tube(): hollow tapered tube along +X from an anchor plate at x in [0, plate_t].
Same params.json key names as the spec so the same code path (sim.common.load_params) is exercised.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
import trimesh
import manifold3d as m3d

HERE = Path(__file__).resolve().parent

REF_PARAMS = {
    "_comment": "REFERENCE ARTICLE (not P0): straight tapered hollow tube + plate, spec key names",
    "span_length": 450.0, "root_diameter": 100.0, "tip_diameter": 40.0, "shell_wall": 2.4,
    "anchor_plate": {"size_y": 160.0, "size_z": 110.0, "thickness": 8.0, "hole_dia": 6.0,
                     "pattern_y": 120.0, "pattern_z": 70.0},
    "centerline": [[8, 0, 0], [158, 0, 0], [308, 0, 0], [458, 0, 0]],
    "shelf_zone": {"center_frac": 0.8},
    "material": "PETG", "layer_dir": [0, 0, 1],
}


def _revolve_profile(profile_xr, segs=96):
    """profile_xr: closed polygon of (axial x, radius r), r>=0. Returns Manifold with axis along +X."""
    pts = np.array([[r, x] for x, r in profile_xr], float)    # revolve about Y axis of (r,y) plane -> result axis Z
    cs = m3d.CrossSection([pts])
    man = m3d.Manifold.revolve(cs, segs)
    # axis Z -> axis X : rotate about Y by +90 deg maps z->x
    return man.rotate([0, 90, 0])


def tapered_tube(params=None, segs=96, tip_cap=2.4, with_skin=False, wall=None, hole=True, plate=True):
    p = dict(REF_PARAMS if params is None else params)
    wall = p["shell_wall"] if wall is None else wall
    pl = p["anchor_plate"]; t = pl["thickness"]
    L = p["span_length"]; r0 = p["root_diameter"] / 2; r1 = p["tip_diameter"] / 2
    x0, x1 = t, t + L
    n = 40
    xs = np.linspace(x0, x1, n)
    ro = r0 + (r1 - r0) * (xs - x0) / L
    ri = np.maximum(ro - wall, 0.1)
    # polygon (x,r): outer root->tip, tip cap, inner tip->root; closed with root opening into plate (x0-1)
    outer = [(x, r) for x, r in zip(xs, ro)]
    inner = [(x, r) for x, r in zip(xs[::-1], ri[::-1])]
    prof = [(x0 - 1.0, ro[0])] + outer + [(x1, ri[-1])] + inner[:-1][::1]
    # simplest closed ring polygon: outer wall (x0-1..x1) then inner back; tip cap by closing r from ro[-1] to ri[-1]
    prof = [(x0 - 1.0, ro[0])] + outer + [(x1 + 0.0, 0.0)] if False else None
    tube_poly = [(x0 - 1.0, 0.0)] + [(x0 - 1.0, ro[0])] + outer + [(x1, 0.0)]
    solid = _revolve_profile(tube_poly, segs)
    cav_poly = [(x0 - 1.0, 0.0)] + [(x0 - 1.0, ri[0])] + [(x, r) for x, r in zip(xs, ri)][:-1]
    if tip_cap > 0:
        cav_poly += [(x1 - tip_cap, ri[-1]), (x1 - tip_cap, 0.0)]
    else:
        cav_poly += [(x1 + 1.0, ri[-1]), (x1 + 1.0, 0.0)]
    cavity = _revolve_profile(cav_poly, segs)
    tube = solid - cavity
    parts = []
    if plate:
        plt = m3d.Manifold.cube([t, pl["size_y"], pl["size_z"]], center=True).translate([t / 2, 0, 0])
        if hole:
            for sy in (-1, 1):
                for sz in (-1, 1):
                    h = m3d.Manifold.cylinder(t + 2, pl["hole_dia"] / 2, pl["hole_dia"] / 2, 32, True).rotate([0, 90, 0])
                    plt = plt - h.translate([t / 2, sy * pl["pattern_y"] / 2, sz * pl["pattern_z"] / 2])
        # plate opening under the tube root cavity so the hollow is open to the plate (cavity continues through plate? no: plate is solid)
        tube = tube + plt
    return man_to_trimesh(tube)


def man_to_trimesh(man):
    mm = man.to_mesh()
    return trimesh.Trimesh(np.asarray(mm.vert_properties)[:, :3], np.asarray(mm.tri_verts), process=False)


def straight_bar(kind="tube", L=200.0, D=40.0, wall=2.4, plate_t=10.0, segs=128, square=False, side=20.0):
    """validation specimens, axis +X from x=0 (clamped face) to x=L. kind: tube|solid|square"""
    if kind == "square":
        return trimesh.creation.box([L, side, side], transform=trimesh.transformations.translation_matrix([L / 2, 0, 0]))
    r = D / 2
    pts = [(0, 0), (0, r), (L, r), (L, 0)]
    solid = _revolve_profile(pts, segs)
    if kind == "solid":
        return man_to_trimesh(solid)
    # open-ended tube (no end caps): keeps closed-form mass/stiffness exact (a tip cap adds ~3 % tip mass and ~6 % f1 shift)
    cav = _revolve_profile([(-1, 0), (-1, r - wall), (L + 1, r - wall), (L + 1, 0)], segs)
    return man_to_trimesh(solid - cav)


def skin_for(under: trimesh.Trimesh, proud=3.0, seed=0, amp=1.0):
    """synthetic additive skin: displaced offset shell of tube (outer only), <= proud mm. Returns closed mesh
    = (offset outer surface) minus underlay outer volume, as a thin 'skin' solid."""
    rng = np.random.default_rng(seed)
    big = under.copy()
    v = big.vertices; n = big.vertex_normals
    disp = proud * amp * (0.5 + 0.5 * np.sin(v[:, 0] * 0.15 + seed) * np.cos(v[:, 1] * 0.2 + v[:, 2] * 0.13))
    big.vertices = v + n * disp[:, None]
    A = m3d.Manifold(m3d.Mesh(np.asarray(big.vertices, np.float32), np.asarray(big.faces, np.uint32)))
    B = m3d.Manifold(m3d.Mesh(np.asarray(under.vertices, np.float32), np.asarray(under.faces, np.uint32)))
    return man_to_trimesh(A - B)


def write_reference(out=HERE / "out"):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    (out / "params.json").write_text(json.dumps(REF_PARAMS, indent=2))
    u = tapered_tube()
    u.export(out / "underlay.stl")
    return u


if __name__ == "__main__":
    u = write_reference()
    print("ref underlay: watertight", u.is_watertight, "vol", u.volume, "bounds", u.bounds.tolist())
