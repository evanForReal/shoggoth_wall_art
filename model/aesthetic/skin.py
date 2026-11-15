"""Swappable aesthetic skin generator.

    skin(envelope, seed=1, style="calcified_webbing", keepouts=None, max_proud=6.0, min_proud=0.8,
         edge_len=2.5, inset=0.6) -> trimesh.Trimesh   (watertight shell solid)

Contract (docs/PROTOTYPE_SPEC.md, Layering):
  * additive only: skin = D(envelope displaced outward by d in [min_proud, max_proud]) minus E(envelope displaced
    INWARD by `inset`), so it overlaps the underlay wall by `inset` (clean union) and never removes underlay material.
  * proud height above the underlay outer surface <= max_proud (hard clamp).
  * keepouts (Manifold list) are subtracted from the skin: shelf-flat column, wall plane, screw-access bores.
  * pure function of (envelope, seed, style): deterministic.

Styles (Beksinski idiom): calcified_webbing, bone_crust, flowstone, rust_blister, mummified_ochre.
"""
import numpy as np
import trimesh
import manifold3d as m3d
from ..mtools import to_manifold, to_trimesh, union
from .noise import fbm, smooth, cells, blobs, fourier_noise

STYLES = {}


def style(fn):
    STYLES[fn.__name__] = fn
    return fn


@style
def calcified_webbing(P, n, seed):
    """Thin raised web/vein network over a low calcified crust."""
    g1 = fourier_noise(P, seed, 1, 1 / 26.0, 40)
    g2 = fourier_noise(P, seed, 2, 1 / 17.0, 40)
    w1 = np.exp(-(g1 / 0.16) ** 2); w2 = np.exp(-(g2 / 0.13) ** 2)
    web = np.maximum(w1, 0.8 * w2)
    crust = 0.5 + 0.5 * np.tanh(fbm(P, seed, 3, 1 / 9.0, 3))
    fine = 0.5 + 0.5 * fbm(P, seed, 4, 1 / 3.5, 2)
    return np.clip(0.8 * web + 0.22 * crust + 0.06 * fine, 0, 1)


@style
def bone_crust(P, n, seed):
    """Plated bone crust: Voronoi plates, cracked grooves, per-plate height."""
    f1, f2, rid = cells(P, seed, 5, 15.0)
    edge = smooth(f2 - f1, 0.5, 3.2)
    dome = 1 - (f1 / 11.0) ** 2
    rough = 0.5 + 0.5 * fbm(P, seed, 6, 1 / 4.0, 2)
    return np.clip(edge * (0.35 + 0.45 * rid) * (0.7 + 0.3 * np.clip(dome, 0, 1)) + 0.12 * rough * edge, 0, 1)


@style
def flowstone(P, n, seed):
    """Drip-curtain rivulets running down Z with stalactite-like rims on downward faces."""
    low = fbm(P, seed, 7, 1 / 60.0, 2)
    ph = (P[:, 0] * 0.6 + P[:, 1] * 0.8) / 14.0 + 0.9 * low
    riv = (0.5 + 0.5 * np.sin(2 * np.pi * ph)) ** 2
    zmod = 0.5 + 0.5 * fbm(P, seed, 8, 1 / 90.0, 2, aniso=(1.0, 1.0, 0.25))
    layers = 0.5 + 0.5 * np.sin(2 * np.pi * (P[:, 2] / 9.0 + 0.6 * low))
    down = smooth(-n[:, 2], -0.2, 0.7)
    return np.clip(0.75 * riv * (0.3 + 0.7 * zmod) + 0.15 * layers * (0.4 + 0.6 * zmod) + 0.2 * down * riv, 0, 1)


@style
def rust_blister(P, n, seed):
    """Corrosion blisters + scabs with streak modulation."""
    b = blobs(P, seed, 9, 11.0, 4.5)
    scab = np.clip(0.5 + 0.9 * fbm(P, seed, 10, 1 / 12.0, 3), 0, 1) ** 2
    streak = 0.5 + 0.5 * fbm(P, seed, 11, 1 / 50.0, 2, aniso=(1, 1, 0.2))
    return np.clip(0.85 * b + 0.3 * scab * streak + 0.05, 0, 1)


@style
def mummified_ochre(P, n, seed):
    """Dried, wrinkled hide: ridged folds, directional creasing."""
    g = fbm(P, seed, 12, 1 / 16.0, 3, aniso=(1.0, 0.6, 1.4))
    ridge = 1 - np.abs(np.tanh(1.6 * g))
    g2 = fbm(P, seed, 13, 1 / 7.0, 2)
    return np.clip(0.75 * ridge ** 2 + 0.2 * (0.5 + 0.5 * g2), 0, 1)


def _smooth_normals(mesh, iters=2):
    n = mesh.vertex_normals.copy()
    adj = mesh.vertex_neighbors
    for _ in range(iters):
        n2 = np.array([n[nb].mean(0) + n[i] for i, nb in enumerate(adj)]) if len(adj) < 0 else None
        break
    # vectorised neighbor average using edge list
    e = mesh.edges_unique
    nv = len(mesh.vertices)
    for _ in range(iters):
        acc = n.copy()
        np.add.at(acc, e[:, 0], n[e[:, 1]]); np.add.at(acc, e[:, 1], n[e[:, 0]])
        n = acc / np.linalg.norm(acc, axis=1, keepdims=True)
    return n


def skin(envelope, seed=1, style="calcified_webbing", keepouts=None, max_proud=6.0, min_proud=0.8,
         edge_len=2.5, inset=0.6):
    if style not in STYLES:
        raise KeyError(f"unknown style {style}; have {sorted(STYLES)}")
    env = envelope if isinstance(envelope, trimesh.Trimesh) else to_trimesh(envelope)
    v, f = trimesh.remesh.subdivide_to_size(env.vertices, env.faces, max_edge=edge_len, max_iter=8)
    m = trimesh.Trimesh(v, f, process=True)
    m.merge_vertices()
    n = _smooth_normals(m)
    h = STYLES[style](m.vertices, n, seed)
    d = min_proud + (max_proud - min_proud) * np.clip(h, 0, 1)
    D = trimesh.Trimesh(m.vertices + n * d[:, None], m.faces, process=False)
    Ein = trimesh.Trimesh(m.vertices - n * inset, m.faces, process=False)
    sk = to_manifold(D) - to_manifold(Ein)
    if keepouts:
        sk = sk - union(keepouts)
    out = to_trimesh(sk)
    return out
