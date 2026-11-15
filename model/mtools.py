"""Mesh/manifold helpers shared by structural and aesthetic generators."""
import numpy as np
import trimesh
import manifold3d as m3d


def to_manifold(mesh):
    mesh = mesh if isinstance(mesh, trimesh.Trimesh) else mesh
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
    if t.volume < 0:
        t.faces = t.faces[:, ::-1]
    return t


def _fill_boundary_loops(t, max_loop=64):
    """Fan-fill small boundary loops (no networkx). Returns new Trimesh."""
    F = t.faces
    de = np.concatenate([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]])
    und = np.sort(de, axis=1)
    u, inv, c = np.unique(und, axis=0, return_inverse=True, return_counts=True)
    inv = inv.reshape(-1)
    bnd = de[(c[inv] == 1)]
    if len(bnd) == 0:
        return t
    nxt = {}
    for a, b in bnd:
        nxt.setdefault(int(a), []).append(int(b))
    used = set(); new = []
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
                for i in range(1, len(v) - 1):
                    new.append([v[i + 1], v[i], v[0]])
    if new:
        t = trimesh.Trimesh(t.vertices, np.vstack([F, np.array(new)]), process=False)
    return t


def clean_mesh(mesh, q=2e-3):
    """STL-safe cleanup: snap to a q-mm grid, weld, drop degenerate faces, fan-fill residual tiny boundary loops.
    Manifold output keeps zero-area triangles that STL loaders delete (leaving holes); this removes them consistently."""
    v = np.round(np.asarray(mesh.vertices) / q) * q
    t = trimesh.Trimesh(v, np.asarray(mesh.faces), process=False)
    t.merge_vertices()
    f = t.faces
    keep = (f[:, 0] != f[:, 1]) & (f[:, 1] != f[:, 2]) & (f[:, 0] != f[:, 2])
    t = trimesh.Trimesh(t.vertices, f[keep], process=False)
    t = _fill_boundary_loops(t)
    t.remove_unreferenced_vertices()
    return t
