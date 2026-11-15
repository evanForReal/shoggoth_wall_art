"""Mesh/manifold helpers shared by structural and aesthetic generators."""
import numpy as np
import trimesh
import manifold3d as m3d

# Repair/flip accounting. Module-level, reset with reset_repair_log(); generate.py writes it to the manifest and the
# selfcheck fails if counts exceed thresholds (silent repairs can mask real holes).
REPAIR_LOG = dict(loft_calls=0, loft_winding_flips=0, clean_calls=[])


def reset_repair_log():
    REPAIR_LOG.update(loft_calls=0, loft_winding_flips=0, clean_calls=[])


def to_manifold(mesh):
    mm = m3d.Mesh64(vert_properties=np.array(mesh.vertices, dtype=np.float64),
                    tri_verts=np.array(mesh.faces, dtype=np.uint64))
    out = m3d.Manifold(mm)
    if out.status() != m3d.Error.NoError:
        raise ValueError(f"mesh not manifold: {out.status()}")
    return out


def to_trimesh(man):
    mm = man.to_mesh64()
    v = np.asarray(mm.vert_properties, dtype=np.float64)[:, :3]
    f = np.asarray(mm.tri_verts, dtype=np.int64)
    t = trimesh.Trimesh(v, f, process=False)
    return t


def union(parts):
    parts = [p for p in parts if p is not None]
    return m3d.Manifold.batch_boolean(parts, m3d.OpType.Add)


def frame_matrix(origin, N, U, T):
    """3x4 matrix mapping local x->N, y->U, z->T."""
    return np.column_stack([N, U, T, origin])


def place(man, origin, N, U, T):
    return man.transform(frame_matrix(origin, N, U, T))


def prism(outline2d, t0, t1):
    """Extrude 2D outline (local x,y) from z=t0 to z=t1 (local coords)."""
    cs = m3d.CrossSection([np.asarray(outline2d, dtype=np.float64)])
    return m3d.Manifold.extrude(cs, t1 - t0).translate((0, 0, t0))


def ring_prism(outer2d, inner2d, t0, t1):
    co = m3d.CrossSection([np.asarray(outer2d, dtype=np.float64)])
    ci = m3d.CrossSection([np.asarray(inner2d, dtype=np.float64)])
    return m3d.Manifold.extrude(co - ci, t1 - t0).translate((0, 0, t0))


def box(center, size):
    c = np.asarray(center, float)
    s = np.asarray(size, float)
    return m3d.Manifold.cube(tuple(s), center=True).translate(tuple(c))


def cyl(p0, p1, r, seg=48):
    """Cylinder between two 3D points."""
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float)
    d = p1 - p0
    L = np.linalg.norm(d)
    z = d / L
    a = np.array([1.0, 0, 0]) if abs(z[0]) < 0.9 else np.array([0, 1.0, 0])
    x = np.cross(a, z); x /= np.linalg.norm(x)
    y = np.cross(z, x)
    c = m3d.Manifold.cylinder(L, r, r, seg)
    return c.transform(np.column_stack([x, y, z, p0]))


def loft_mesh(centers, Ns, Us, profiles, cap_start=True, cap_end=True):
    """Loft closed profiles (n,m,2) given in (N,U) frame coords at each station.
    Profiles must have consistent CCW winding in (N,U) with T = N x U ... (N,U,T right-handed)."""
    n, mcount, _ = profiles.shape
    P = (centers[:, None, :] + profiles[:, :, 0:1] * Ns[:, None, :]
         + profiles[:, :, 1:2] * Us[:, None, :])
    verts = [P.reshape(-1, 3)]
    faces = []
    idx = lambda i, j: i * mcount + (j % mcount)
    for i in range(n - 1):
        for j in range(mcount):
            a, b, c, d = idx(i, j), idx(i, j + 1), idx(i + 1, j + 1), idx(i + 1, j)
            faces.append([a, b, c]); faces.append([a, c, d])
    nv = n * mcount
    extra = []
    if cap_start:
        cs = P[0].mean(axis=0); extra.append(cs); ci = nv + len(extra) - 1
        for j in range(mcount):
            faces.append([ci, idx(0, j + 1), idx(0, j)])
    if cap_end:
        ce = P[-1].mean(axis=0); extra.append(ce); ci = nv + len(extra) - 1
        for j in range(mcount):
            faces.append([ci, idx(n - 1, j), idx(n - 1, j + 1)])
    if extra:
        verts.append(np.array(extra))
    V = np.vstack(verts)
    F = np.array(faces)
    # orientation: with (N,U,T) right-handed and CCW profile, side normal points outward when
    # faces wind (a,b,c) as above; verify by volume sign
    t = trimesh.Trimesh(V, F, process=False)
    REPAIR_LOG["loft_calls"] += 1
    if t.volume < 0:
        REPAIR_LOG["loft_winding_flips"] += 1
        t.faces = t.faces[:, ::-1]
    return t


def _fill_boundary_loops(t, max_loop=64):
    """Fan-fill small boundary loops (no networkx). Returns (Trimesh, n_loops_filled, n_loops_left_open)."""
    F = t.faces
    de = np.concatenate([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]])
    und = np.sort(de, axis=1)
    u, inv, c = np.unique(und, axis=0, return_inverse=True, return_counts=True)
    inv = inv.reshape(-1)
    bnd = de[(c[inv] == 1)]
    if len(bnd) == 0:
        return t, 0, 0
    nxt = {}
    for a, b in bnd:
        nxt.setdefault(int(a), []).append(int(b))
    used = set(); new = []; n_filled = 0; n_open = 0
    for a0 in list(nxt):
        for b0 in nxt[a0]:
            if (a0, b0) in used:
                continue
            loop = [a0]; cur = (a0, b0); used.add(cur)
            while True:
                loop.append(cur[1])
                if cur[1] == a0 or len(loop) > max_loop + 2:
                    break
                cand = [x for x in nxt.get(cur[1], []) if (cur[1], x) not in used]
                if not cand:
                    break
                cur = (cur[1], cand[0]); used.add(cur)
            if loop[-1] == a0 and 3 <= len(loop) - 1 <= max_loop:
                v = loop[:-1]
                n_filled += 1
                for i in range(1, len(v) - 1):
                    new.append([v[i + 1], v[i], v[0]])
            else:
                n_open += 1
    if new:
        t = trimesh.Trimesh(t.vertices, np.vstack([F, np.array(new)]), process=False)
    return t, n_filled, n_open


def clean_mesh(mesh, q=2e-3, name=""):
    """STL-safe cleanup: snap to a q-mm grid, weld, drop degenerate faces, fan-fill residual tiny boundary loops.
    Manifold output keeps zero-area triangles that STL loaders delete (leaving holes); this removes them consistently.
    Counts of every repair are appended to REPAIR_LOG['clean_calls']."""
    n_v0, n_f0 = len(mesh.vertices), len(mesh.faces)
    v = np.round(np.asarray(mesh.vertices) / q) * q
    t = trimesh.Trimesh(v, np.asarray(mesh.faces), process=False)
    t.merge_vertices()
    n_merged = n_v0 - len(t.vertices)
    f = t.faces
    keep = (f[:, 0] != f[:, 1]) & (f[:, 1] != f[:, 2]) & (f[:, 0] != f[:, 2])
    n_degen = int((~keep).sum())
    t = trimesh.Trimesh(t.vertices, f[keep], process=False)
    t, n_filled, n_open = _fill_boundary_loops(t)
    t.remove_unreferenced_vertices()
    REPAIR_LOG["clean_calls"].append(dict(name=name, faces_in=int(n_f0), vertices_merged=int(n_merged),
                                          degenerate_faces_dropped=n_degen, boundary_loops_filled=int(n_filled),
                                          boundary_loops_left_open=int(n_open)))
    return t


def shell_components(mesh):
    """Connected surface components (by shared vertices). Returns list of dict(faces, volume, bounds); a closed solid
    with sealed internal voids or stray fragments yields >1 component (voids have negative signed volume)."""
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    F = np.asarray(mesh.faces); n = len(mesh.vertices)
    a = np.concatenate([F[:, 0], F[:, 1]]); b = np.concatenate([F[:, 1], F[:, 2]])
    _, lab = connected_components(coo_matrix((np.ones(len(a)), (a, b)), shape=(n, n)), directed=False)
    fl = lab[F[:, 0]]
    out = []
    for c in np.unique(fl):
        sub = trimesh.Trimesh(mesh.vertices, F[fl == c], process=False)
        sub.remove_unreferenced_vertices()
        out.append(dict(faces=int(len(sub.faces)), volume=float(sub.volume), bounds=sub.bounds.round(2).tolist()))
    return out
