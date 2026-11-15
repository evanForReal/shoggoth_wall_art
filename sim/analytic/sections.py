"""Cross-section properties from the ACTUAL mesh (planar slices normal to the centerline).
Independent of sim.hexfea / sim.voxel: uses trimesh plane slicing + shapely only.

Section frame: tangent t, u = z_hat x t (horizontal, ~Y), v = t x u (~up). I_u = int v^2 dA (about u axis; vertical bending),
I_v = int u^2 dA (lateral bending). Infill-equivalent: material deeper than `wall` from any boundary has E,rho scaled by f.
"""
from __future__ import annotations
import numpy as np
import trimesh
from shapely.geometry import Polygon, MultiPolygon, Point
from shapely.ops import unary_union


def frame(t):
    z = np.array([0, 0, 1.0])
    u = np.cross(z, t)
    if np.linalg.norm(u) < 1e-6:
        u = np.array([0, 1.0, 0])
    u /= np.linalg.norm(u)
    v = np.cross(t, u)
    return u, v


def ring_moments(c):
    """signed area, centroid-moments of a closed ring (Green)."""
    x = c[:, 0]; y = c[:, 1]
    x1 = np.roll(x, -1); y1 = np.roll(y, -1)
    cr = x * y1 - x1 * y
    A = cr.sum() / 2
    Sx = ((y + y1) * cr).sum() / 6       # int y dA
    Sy = ((x + x1) * cr).sum() / 6       # int x dA
    Ixx = ((y * y + y * y1 + y1 * y1) * cr).sum() / 12   # int y^2
    Iyy = ((x * x + x * x1 + x1 * x1) * cr).sum() / 12   # int x^2
    Ixy = ((x * y1 + 2 * x * y + 2 * x1 * y1 + x1 * y) * cr).sum() / 24
    return A, Sx, Sy, Ixx, Iyy, Ixy


def poly_moments(poly):
    """area, int u dA, int v dA, int v^2, int u^2, int uv (about origin); coordinates are (u,v)."""
    tot = np.zeros(6)
    polys = [poly] if isinstance(poly, Polygon) else list(poly.geoms)
    for p in polys:
        for ring, sgn in [(p.exterior, 1)] + [(r, -1) for r in p.interiors]:
            c = np.asarray(ring.coords)[:-1]
            a = ring_moments(c)
            s = 1 if a[0] > 0 else -1   # normalise orientation then apply sign
            tot += sgn * s * np.array([a[0], a[2], a[1], a[3], a[4], a[5]])
    return tot  # A, Su=int u, Sv=int v, I_u=int v^2, I_v=int u^2, Iuv


def slice_loops(mesh, origin, t):
    """closed 3D loops of mesh intersection with plane (no networkx): chain mesh_plane segments."""
    segs = trimesh.intersections.mesh_plane(mesh, plane_normal=t, plane_origin=origin)
    if segs is None or len(segs) == 0:
        return []
    key = lambda p: tuple(np.round(p, 3))
    adj = {}
    for a, b in segs:
        ka, kb = key(a), key(b)
        if ka == kb:
            continue
        adj.setdefault(ka, []).append(kb); adj.setdefault(kb, []).append(ka)
    used = set(); loops = []
    for start in list(adj):
        if start in used:
            continue
        loop = [start]; used.add(start); prev = None; cur = start
        while True:
            nxt = [k for k in adj[cur] if k != prev and k not in used]
            if not nxt:
                break
            prev, cur = cur, nxt[0]; used.add(cur); loop.append(cur)
        if len(loop) >= 4:
            loops.append(np.array(loop))
    return loops


def section_polygon(mesh, origin, t, radius_hint):
    u, v = frame(t)
    loops = []
    for d in slice_loops(mesh, origin, t):
        rel = d - origin
        loops.append(np.c_[rel @ u, rel @ v])
    region = None
    for l in sorted(loops, key=lambda l: -abs(ring_moments(l)[0])):
        pg = Polygon(l).buffer(0)
        if pg.is_empty:
            continue
        region = pg if region is None else region.symmetric_difference(pg)
    if region is None:
        return None, u, v
    # keep components near the centerline point (origin -> (0,0))
    comps = [region] if isinstance(region, Polygon) else list(region.geoms)
    near = [c for c in comps if c.distance(Point(0, 0)) < 1.6 * radius_hint]
    if not near:
        return None, u, v
    return unary_union(near), u, v


def props(poly, wall, ffac):
    """effective section properties about the effective centroid. returns dict."""
    m = poly_moments(poly)
    inner = poly.buffer(-wall)
    mi = poly_moments(inner) if not inner.is_empty else np.zeros(6)
    k = 1.0 - ffac
    me = m - k * mi          # E-weighted (and rho-weighted) moments about origin
    A = me[0]
    cu, cv = me[1] / A, me[2] / A
    Iu = me[3] - A * cv * cv; Iv = me[4] - A * cu * cu; Iuv = me[5] - A * cu * cv
    # torsion: Bredt for hollow single-cell shell parts, else polar
    holes = sum(len(p.interiors) for p in ([poly] if isinstance(poly, Polygon) else poly.geoms))
    if holes == 1:
        p = poly if isinstance(poly, Polygon) else max(poly.geoms, key=lambda g: g.area)
        Aout = Polygon(p.exterior).area; Ain = Polygon(p.interiors[0]).area
        Am = 0.5 * (Aout + Ain); Pm = 0.5 * (p.exterior.length + p.interiors[0].length)
        t_eff = p.area / Pm
        J = 4 * Am ** 2 / (Pm / t_eff)
    else:
        J = Iu + Iv
    bnd = []
    for p in ([poly] if isinstance(poly, Polygon) else poly.geoms):
        for ring in [p.exterior] + list(p.interiors):
            bnd.append(np.asarray(ring.coords)[::2])
    bnd = np.vstack(bnd) - np.array([cu, cv])
    return {"A_eff": float(A), "A_geom": float(m[0]), "cu": float(cu), "cv": float(cv), "Iu": float(Iu), "Iv": float(Iv),
            "Iuv": float(Iuv), "J": float(J), "bnd": bnd, "t_eff_mm": float(2 * poly.area / poly.length) if poly.length else 0.0,
            "n_holes": int(holes)}


def sections_along(mesh, cl, wall, ffac, n=45, s0=0.0, s1=1.0, r_hint=None):
    """list of station dicts along centerline fraction s0..s1."""
    out = []
    for f in np.linspace(s0, s1, n):
        p, t = cl.at(f); p = p[0]; t = t[0]
        r = r_hint(f) if r_hint else 50.0
        poly, u, v = section_polygon(mesh, p, t, r)
        if poly is None:
            continue
        pr = props(poly, wall, ffac)
        cen = p + pr["cu"] * u + pr["cv"] * v
        out.append({"s": float(f), "p": cen, "t": t, "u": u, "v": v, **pr})
    return out
