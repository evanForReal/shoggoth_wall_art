#!/usr/bin/env python3
"""Re-validate the SCULPTED mesh: topology, manifold3d, bbox, mass, re-voxelised (0.5 mm) min-wall + void checks
(same minwall.measure as the field check), with a calibration of the voxelisation method on the pre-sculpt mesh.

Usage: python3 validate_sculpt.py DIR TAG [--stl]
"""
import sys, os, json, argparse
import numpy as np
from scipy import ndimage as ndi
import manifold3d as m3d
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import minwall

ap = argparse.ArgumentParser(); ap.add_argument('dir'); ap.add_argument('tag'); ap.add_argument('--stl', action='store_true')
a = ap.parse_args()
g = json.load(open(os.path.join(a.dir, 'grid.json'))); vox = g['vox']


def topo(v, f):
    """Edge-based manifold / winding check without trimesh (keeps RAM low on 10 M faces)."""
    nv = len(v)
    d = np.concatenate([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]]).astype(np.int64)
    k_dir = d[:, 0] * nv + d[:, 1]
    k_und = np.minimum(d[:, 0], d[:, 1]) * nv + np.maximum(d[:, 0], d[:, 1])
    ud, cd = np.unique(k_dir, return_counts=True)
    uu, cu = np.unique(k_und, return_counts=True)
    return dict(edges=int(len(uu)), edges_not_2_faces=int((cu != 2).sum()), directed_edges_repeated=int((cd > 1).sum()),
                watertight_2manifold=bool((cu == 2).all()), winding_consistent=bool((cd == 1).all()),
                degenerate_faces=int((np.linalg.norm(np.cross(v[f[:, 1]] - v[f[:, 0]], v[f[:, 2]] - v[f[:, 0]]), axis=1) < 1e-10).sum()))


def voxelise(v, f, shape, x0, y0, z0):
    """Surface samples (vertices + face centroids) -> surface voxels -> exterior flood fill."""
    surf = np.zeros(shape, bool)
    for pts in (v, None):
        if pts is None:
            for s in range(0, len(f), 2_000_000):
                ff = f[s:s + 2_000_000]; pts = (v[ff[:, 0]] + v[ff[:, 1]] + v[ff[:, 2]]) / 3.0
                i = np.round((pts - [x0, y0, z0]) / vox).astype(int); i = np.clip(i, 0, np.array(shape) - 1); surf[i[:, 0], i[:, 1], i[:, 2]] = True
        else:
            i = np.round((pts - [x0, y0, z0]) / vox).astype(int); i = np.clip(i, 0, np.array(shape) - 1); surf[i[:, 0], i[:, 1], i[:, 2]] = True
    lab, n = ndi.label(~surf)
    ext = lab[0, 0, shape[2] - 1]
    interior = (~surf) & (lab != ext)
    return interior | surf, interior


def evaluate(v, f, label, variant='incl'):
    pad = 2
    shape = (int(round(g['nx'])) + 2 * pad, int(round(g['ny'])) + 2 * pad, int(round(g['nz'])) + pad)
    x0 = g['x0'] - pad * vox; y0 = g['y0'] - pad * vox; z0 = g['z0']
    occ, interior = voxelise(v, f, shape, x0, y0, z0)
    if variant == 'interior':
        occ = interior   # pessimistic: surface voxels not counted as solid
    vol_vox = occ.sum() * vox ** 3 / 1000; vol_in = interior.sum() * vox ** 3 / 1000
    ys = y0 + vox * np.arange(shape[1])
    res, edt, thin = minwall.measure(occ, vox, ys)
    res['voxel_volume_cm3_surface_inclusive'] = round(float(vol_vox), 1); res['voxel_volume_cm3_interior_only'] = round(float(vol_in), 1)
    res['occ_variant'] = variant
    json.dump(res, open(os.path.join(a.dir, 'revox_%s.json' % label), 'w'), indent=1)
    print(label, {k: res[k] for k in ('frac_below_thin', 'opening_2mm_volume_retained_frac', 'voxel_volume_cm3_surface_inclusive', 'voxel_volume_cm3_interior_only')}, res['ridge'], res['voids']['counts'], flush=True)
    return res


# grid dims from the clamped occupancy
occ_c = np.load(os.path.join(a.dir, 'occ_clamped.npy'), mmap_mode='r')
g['nx'], g['ny'], g['nz'] = occ_c.shape; del occ_c

out = {}
sc = np.load(os.path.join(a.dir, 'sculpt_%s.npz' % a.tag)); v = sc['v'].astype(np.float64); f = sc['f'].astype(np.int64)
out['tris'] = int(len(f)); out['verts'] = int(len(v))
out['topology'] = topo(v, f)
out['bbox_min_mm'] = [round(float(x), 2) for x in v.min(0)]; out['bbox_max_mm'] = [round(float(x), 2) for x in v.max(0)]
out['bbox_size_mm'] = [round(float(x), 1) for x in (v.max(0) - v.min(0))]
mf = m3d.Manifold(m3d.Mesh(v.astype(np.float32), f.astype(np.uint32)))
out['manifold3d_status'] = str(mf.status())
if str(mf.status()).endswith('NoError'):
    out['manifold3d_volume_cm3'] = round(mf.volume() / 1000, 2); out['manifold3d_genus'] = int(mf.genus())
    out['mass_g_solid_PETG_1.27'] = round(mf.volume() / 1000 * 1.27, 1); out['surface_area_cm2'] = round(mf.surface_area() / 100, 1)
back = v[v[:, 2] < 0.6, 2]; out['back_plane_z_range'] = [round(float(back.min()), 3), round(float(back.max()), 3)]
top = v[(np.abs(v[:, 1] + 34.75) < 0.05)]; out['shelf_top_vertex_spread_mm'] = round(float(np.ptp(top[:, 1])), 4) if len(top) else None
print(json.dumps(out, indent=1), flush=True)

pre = np.load(os.path.join(a.dir, 'patch_clean.npz')); pv = pre['v'].astype(np.float64); pf = pre['f'].astype(np.int64)
keys = ('skeleton_voxels', 'frac_below_thin', 'opening_2mm_volume_retained_frac', 'ridge', 'voids', 'width_hist_mm',
        'voxel_volume_cm3_surface_inclusive', 'voxel_volume_cm3_interior_only', 'thickness_p5_mm', 'thickness_p50_mm')
out['revox'] = {}
for variant in ('incl', 'interior'):
    pr = evaluate(pv, pf, 'presculpt_' + variant, variant)
    po = evaluate(v, f, 'postsculpt_%s_%s' % (a.tag, variant), variant)
    out['revox'][variant] = dict(pre={k: pr[k] for k in keys}, post={k: po[k] for k in keys})
    json.dump(out, open(os.path.join(a.dir, 'validation_sculpt_%s.json' % a.tag), 'w'), indent=1)
if a.stl:
    import fast_simplification as fs
    import trimesh
    vv, ff = fs.simplify(v.astype(np.float32), f, target_count=380000, agg=5)
    mf2 = m3d.Manifold(m3d.Mesh(np.asarray(vv, np.float32), np.asarray(ff, np.uint32))); mm = mf2.to_mesh()
    dm = trimesh.Trimesh(np.asarray(mm.vert_properties)[:, :3], np.asarray(mm.tri_verts), process=False)
    p = os.path.join(a.dir, 'gate2_%s.stl' % a.tag); dm.export(p)
    out['stl'] = dict(tris=int(len(dm.faces)), watertight=bool(dm.is_watertight), MB=round(os.path.getsize(p) / 1e6, 1),
                      volume_change_pct=round(100 * (abs(dm.volume) - mf.volume()) / mf.volume(), 2),
                      note='decimated to the 20 MB budget; sub-mm grain is NOT preserved in the STL')
json.dump(out, open(os.path.join(a.dir, 'validation_sculpt_%s.json' % a.tag), 'w'), indent=1)
