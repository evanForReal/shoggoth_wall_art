"""Printability checks on closed triangle meshes (numpy/scipy/trimesh/manifold3d only; no rtree/networkx)."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import trimesh
from scipy import ndimage

from sim.voxel import Grid, winding_raster

LIM = json.loads((Path(__file__).parent / "limits.json").read_text())


def mesh_integrity(m: trimesh.Trimesh, pitch=0.8):
    f = m.faces
    e = np.sort(m.edges, axis=1)
    _, cnt = np.unique(e, axis=0, return_counts=True)
    nonman = int((cnt > 2).sum()); open_e = int((cnt == 1).sum())
    area = m.area_faces
    degenerate = int((area < 1e-9).sum())
    # connected components via scipy
    import scipy.sparse as sp
    from scipy.sparse.csgraph import connected_components
    nv = len(m.vertices)
    A = sp.coo_matrix((np.ones(len(f) * 3), (f.ravel(), np.roll(f, -1, axis=1).ravel())), shape=(nv, nv))
    ncomp, _ = connected_components(A, directed=False)
    out = {"watertight": bool(m.is_watertight), "winding_consistent": bool(m.is_winding_consistent), "volume_mm3": float(m.volume),
           "non_manifold_edges": nonman, "open_edges": open_e, "degenerate_faces": degenerate, "components": int(ncomp), "n_faces": int(len(f)),
           "inverted": bool(m.volume < 0)}
    # self-overlap proxy: winding anomalies on a coarse raster
    g = Grid.from_bounds(m.bounds[0], m.bounds[1], max(pitch, float(np.cbrt(np.prod(m.extents) / 3e7))))
    w = winding_raster(m, g)
    out["self_intersection_proxy_cells"] = int(((w != 0) & (w != 1)).sum())
    out["self_intersection_note"] = f"voxel winding proxy at pitch {g.pitch:.2f} mm: cells with |winding|>=2 or <0; sub-pitch overlaps not detected"
    out["pass"] = bool(out["watertight"] and out["winding_consistent"] and not out["inverted"] and nonman == 0 and open_e == 0 and out["self_intersection_proxy_cells"] == 0)
    return out


def orient_stats(m, up, angle=45.0):
    """overhang stats for build direction `up` (unit)."""
    n = m.face_normals; a = m.area_faces
    nz = n @ up
    zc = m.triangles_center @ up
    zmin = (m.vertices @ up).min()
    on_bed = (m.triangles[:, :, :].reshape(-1, 3, 3) @ up).max(axis=1) < zmin + 0.15
    over = (nz < -np.sin(np.radians(angle))) & ~on_bed
    tot = a.sum()
    # support volume proxy: projected area * height above bed (upper bound, no shadowing)
    sv = float((a[over] * np.abs(nz[over]) * (zc[over] - zmin)).sum())
    return {"overhang_area_mm2": float(a[over].sum()), "overhang_fraction": float(a[over].sum() / tot), "support_volume_proxy_cm3": sv / 1000.0, "_over_mask": over}


def bed_fit_xy(m, up, step=3.0):
    """min XY bbox (best rotation about `up`), and height."""
    up = up / np.linalg.norm(up)
    t = np.cross(up, [1, 0, 0] if abs(up[0]) < 0.9 else [0, 1, 0]); t /= np.linalg.norm(t); s = np.cross(up, t)
    v = m.vertices
    P = np.c_[v @ t, v @ s]; h = float(np.ptp(v @ up))
    best = None
    for ang in np.arange(0, 90, step):
        c, sn = np.cos(np.radians(ang)), np.sin(np.radians(ang))
        R = np.array([[c, -sn], [sn, c]])
        q = P @ R.T
        ext = q.max(0) - q.min(0)
        key = max(ext)
        if best is None or key < best[0]:
            best = (key, ext, ang)
    return {"xy_extent_mm": best[1].round(1).tolist(), "rot_deg": float(best[2]), "height_mm": float(h)}


def orientations(m, bed=None, target=None):
    bed = bed or LIM["bed_mm"]; target = target or LIM["bed_target_mm"]
    dirs = {"+z": [0, 0, 1], "-z": [0, 0, -1], "+x": [1, 0, 0], "-x": [-1, 0, 0], "+y": [0, 1, 0], "-y": [0, -1, 0]}
    res = []
    for k, d in dirs.items():
        up = np.array(d, float)
        bf = bed_fit_xy(m, up); st = orient_stats(m, up, LIM["overhang_angle_deg"]); st.pop("_over_mask")
        fits = max(bf["xy_extent_mm"]) <= bed and bf["height_mm"] <= bed
        res.append({"up": k, **bf, **st, "fits_bed": bool(fits), "fits_target": bool(max(bf["xy_extent_mm"]) <= target and bf["height_mm"] <= target)})
    return res


def best_orientation(m):
    o = orientations(m)
    fit = [x for x in o if x["fits_bed"]]
    pool = fit if fit else o
    return min(pool, key=lambda x: x["overhang_fraction"]), o


def bridges(m, up, angle=45.0, min_len=1.0):
    """connected overhang patches (face adjacency): report extents (major/minor, in plane normal to up)."""
    st = orient_stats(m, up, angle); mask = st["_over_mask"]
    idx = np.nonzero(mask)[0]
    if len(idx) == 0:
        return {"n_patches": 0, "max_minor_extent_mm": 0.0, "max_major_extent_mm": 0.0}
    import scipy.sparse as sp
    from scipy.sparse.csgraph import connected_components
    adj = m.face_adjacency
    ok = mask[adj[:, 0]] & mask[adj[:, 1]]
    remap = -np.ones(len(m.faces), int); remap[idx] = np.arange(len(idx))
    a = remap[adj[ok, 0]]; b = remap[adj[ok, 1]]
    A = sp.coo_matrix((np.ones(len(a)), (a, b)), shape=(len(idx), len(idx)))
    nc, lab = connected_components(A, directed=False)
    up = up / np.linalg.norm(up)
    t = np.cross(up, [1, 0, 0] if abs(up[0]) < 0.9 else [0, 1, 0]); t /= np.linalg.norm(t); s = np.cross(up, t)
    best_minor = 0.0; best_major = 0.0; worst = None
    for c in range(nc):
        fi = idx[lab == c]
        if m.area_faces[fi].sum() < 4.0:
            continue
        pts = m.triangles[fi].reshape(-1, 3)
        q = np.c_[pts @ t, pts @ s]
        q = q - q.mean(0)
        u, sv, vt = np.linalg.svd(q, full_matrices=False)
        pr = q @ vt.T
        ext = pr.max(0) - pr.min(0)
        if ext[1] > best_minor:
            best_minor = float(ext[1]); worst = m.triangles_center[fi].mean(0).round(1).tolist()
        best_major = max(best_major, float(ext[0]))
    return {"n_patches": int(nc), "max_minor_extent_mm": best_minor, "max_major_extent_mm": best_major, "worst_patch_center": worst}


def thin_scan(m, thresholds=(0.6, 0.8, 1.0, 1.2, 1.6, 2.0), pitch=None, slab_mm=60.0, min_cells=30):
    """Opening-residual thickness scan. For each threshold t: material voxels not covered by any inscribed ball of diameter t.
    Returns per-t thin volume (clusters >= min_cells cells) and location of the largest cluster. Also thin gaps (void thinner than t_gap)."""
    if pitch is None:
        pitch = 0.4 if np.prod(m.extents[1:]) < 4e4 else 0.5
        pitch = max(pitch, float(np.cbrt(np.prod(m.extents) / 4e7)) if np.prod(m.extents) / pitch ** 3 > 4e7 else pitch)
    p = pitch; rmax = max(thresholds) / 2 + 2 * p
    lo, hi = m.bounds
    xs = np.arange(lo[0] - 2 * p, hi[0] + 2 * p, slab_mm)
    out = {t: {"vol_mm3": 0.0, "clusters": 0, "worst": None, "worst_cells": 0} for t in thresholds}
    for x0 in xs:
        x1 = min(x0 + slab_mm, hi[0] + 2 * p)
        glo = np.array([x0 - rmax, lo[1], lo[2]]); ghi = np.array([x1 + rmax, hi[1], hi[2]])
        g = Grid.from_bounds(glo, ghi, p, pad=int(np.ceil(rmax / p)) + 1)
        occ = winding_raster(m, g) == 1
        if not occ.any():
            continue
        core = np.zeros(occ.shape[0], bool)
        xc = g.origin[0] + (np.arange(occ.shape[0]) + 0.5) * p
        core = (xc >= x0) & (xc < x1)
        if not (occ[core].any()):
            continue
        d_in = ndimage.distance_transform_edt(occ, sampling=p)
        for t in thresholds:
            r = max(t / 2 - 0.5 * p, 0.5 * p)
            er = d_in > r
            dil = ndimage.distance_transform_edt(~er, sampling=p) <= r
            thin = occ & ~dil
            thin &= core[:, None, None]
            if not thin.any():
                continue
            lab, nl = ndimage.label(thin)
            sizes = np.bincount(lab.ravel())[1:]
            keep = np.nonzero(sizes >= min_cells)[0]
            if len(keep):
                # drop convex-edge slivers left by the opening: require volume/major_extent >= 0.3 t^2 (cross-section of a real thin feature)
                objs = ndimage.find_objects(lab)
                good = []
                for k in keep:
                    sl = objs[k]
                    major = max((s_.stop - s_.start) for s_ in sl) * p
                    if sizes[k] * p ** 3 / max(major, p) >= 0.3 * t * t:
                        good.append(k)
                keep = np.array(good, int)
            if len(keep) == 0:
                continue
            out[t]["clusters"] += len(keep); out[t]["vol_mm3"] += float(sizes[keep].sum() * p ** 3)
            k = keep[np.argmax(sizes[keep])]
            if sizes[k] > out[t]["worst_cells"]:
                cc = ndimage.center_of_mass(lab == (k + 1))
                out[t]["worst"] = (g.origin + (np.array(cc) + 0.5) * p).round(1).tolist(); out[t]["worst_cells"] = int(sizes[k])
    res = {"pitch_mm": p, "min_cells": min_cells, "by_threshold": {str(t): v for t, v in out.items()}}
    wall = LIM["min_wall_mm"]
    clean = [t for t in thresholds if out[t]["vol_mm3"] == 0.0]
    res["min_wall_resolved_ge_mm"] = max(clean) if clean else 0.0
    res["pass_min_wall"] = bool(out[min(thresholds, key=lambda t: abs(t - wall))]["vol_mm3"] == 0.0)
    res["note"] = "wall >= t demonstrated for the largest t with zero significant thin clusters; resolution ~ +-pitch"
    return res


def mass_time(m, rho_g_cm3, wall, pitch=1.0):
    """20 % infill estimate: material within `wall` of any surface solid, interior infill fraction."""
    g = Grid.from_bounds(m.bounds[0], m.bounds[1], max(pitch, float(np.cbrt(np.prod(m.extents) / 4e7))))
    occ = winding_raster(m, g) == 1
    d = ndimage.distance_transform_edt(occ, sampling=g.pitch)
    solid = occ & (d <= wall)
    inner = occ & ~solid
    v = (solid.sum() + LIM["infill_fraction"] * inner.sum()) * g.pitch ** 3
    vfull = float(m.volume)
    mass = v * rho_g_cm3 * 1e-3 / 1000.0   # mm3 -> cm3 -> g -> kg: v*1e-3 cm3 * rho g/cm3 /1000
    layers = (m.extents.min() if False else m.extents[2]) / 0.2
    t_h = (v / LIM["flow_mm3_s"] + layers * LIM["layer_overhead_s"]) / 3600.0
    return {"extruded_volume_cm3": v / 1000.0, "geom_volume_cm3": vfull / 1000.0, "mass_kg_20pct_infill": mass, "mass_kg_solid": vfull * rho_g_cm3 * 1e-6,
            "print_time_proxy_h": t_h, "note": f"voxel pitch {g.pitch:.2f}; time = V/{LIM['flow_mm3_s']} mm3/s + layers*{LIM['layer_overhead_s']} s (proxy, no travel/retraction model)"}
