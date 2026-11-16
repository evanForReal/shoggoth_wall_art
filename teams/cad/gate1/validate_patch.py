#!/usr/bin/env python3
"""Clean + validate the Gate-1 patch mesh; export decimated STL if <=20 MB.

Usage: python3 validate_patch.py RAW.npz OUTDIR [--stl]
Writes OUTDIR/validation.json, OUTDIR/patch_clean.npz (full-res), optional gate1_patch.stl.
"""
import sys, json, os, argparse
import numpy as np, trimesh
import manifold3d as m3d
from scipy import ndimage as ndi

ap = argparse.ArgumentParser(); ap.add_argument('raw'); ap.add_argument('out')
ap.add_argument('--stl', action='store_true'); ap.add_argument('--vox', type=float, default=0.5)
a = ap.parse_args()
d = np.load(a.raw)
m = trimesh.Trimesh(d['v'].astype(np.float64), d['f'], process=False)
m.merge_vertices()
res = {}
res['raw_tris'] = int(len(m.faces))
parts = m.split(only_watertight=False)
vols = sorted([abs(p.volume) for p in parts], reverse=True)
res['shells_before_cleanup'] = len(parts)
keep = [p for p in parts if abs(p.volume) > 0.02 * vols[0]]   # drop floating specks < 2% of largest
res['shells_dropped'] = len(parts) - len(keep)
res['dropped_volume_mm3'] = float(sum(abs(p.volume) for p in parts if p not in keep))
m = trimesh.util.concatenate(keep) if len(keep) > 1 else keep[0]
m.merge_vertices()
if m.volume < 0: m.invert()
res['shells_final'] = len(m.split(only_watertight=False))
res['watertight'] = bool(m.is_watertight); res['winding_consistent'] = bool(m.is_winding_consistent)
res['tris'] = int(len(m.faces)); res['verts'] = int(len(m.vertices))
res['bbox_min_mm'] = [round(float(x), 2) for x in m.bounds[0]]; res['bbox_max_mm'] = [round(float(x), 2) for x in m.bounds[1]]
res['bbox_size_mm'] = [round(float(x), 1) for x in m.extents]
mf = m3d.Manifold(m3d.Mesh(np.asarray(m.vertices, np.float32), np.asarray(m.faces, np.uint32)))
res['manifold3d_status'] = str(mf.status())
res['manifold3d_volume_mm3'] = float(mf.volume()) if str(mf.status()).endswith('NoError') else None
vol = abs(float(m.volume)); res['volume_cm3'] = round(vol / 1000, 2)
res['mass_g_solid_PETG_1.27'] = round(vol / 1000 * 1.27, 1)
res['surface_area_cm2'] = round(float(m.area) / 100, 1)
v = np.asarray(m.vertices)
res['back_plane_z_range'] = [round(float(v[v[:, 2] < 0.6, 2].min()), 3), round(float(v[v[:, 2] < 0.6, 2].max()), 3)]
fn = m.face_normals; fc = m.triangles_center
sel = (fn[:, 1] > 0.999) & (np.abs(fc[:, 1] - (-34.75)) < 0.05)
tv = np.unique(m.faces[sel].ravel()); top = v[tv]
res['shelf_top_flatness_mm'] = round(float(np.ptp(top[:, 1])), 4) if len(top) else None
res['shelf_top_flat_area_cm2'] = round(float(m.area_faces[sel].sum()) / 100, 1)

# ---- min-strand sample check: EDT medial ridge thickness on the voxelised mesh
vox = a.vox
occ = np.load(os.path.join(os.path.dirname(a.raw), 'occ.npy'))
edt = ndi.distance_transform_edt(occ, sampling=vox).astype(np.float32)
mx = ndi.maximum_filter(edt, size=3)
medial = (edt == mx) & (edt > 0)
th = 2 * edt[medial]
res['strand_check'] = dict(
    medial_samples=int(medial.sum()),
    thickness_p1_mm=round(float(np.percentile(th, 1)), 2), thickness_p5_mm=round(float(np.percentile(th, 5)), 2),
    thickness_p50_mm=round(float(np.percentile(th, 50)), 2),
    frac_below_2mm=round(float((th < 2.0).mean()), 4), frac_below_1p5mm=round(float((th < 1.5).mean()), 4),
    note='medial-ridge EDT sample; voxel quantisation +-%.2f mm; tips/junction shoulders inflate low tail' % (vox))
# opening test: material surviving a 1.0 mm radius opening (== all features >= 2.0 mm wide)
er = edt >= 1.0
op = ndi.distance_transform_edt(~er, sampling=vox) < 1.0
res['opening_2mm_volume_retained_frac'] = round(float((op & occ).sum() / occ.sum()), 4)
del op, er

np.savez(os.path.join(a.out, 'patch_clean.npz'), v=np.asarray(m.vertices, np.float32), f=np.asarray(m.faces, np.uint32))
if a.stl:
    import fast_simplification as fs
    tgt = 380000
    vv, ff = fs.simplify(np.asarray(m.vertices, np.float32), np.asarray(m.faces, np.int64), target_count=tgt, agg=5)
    mf2 = m3d.Manifold(m3d.Mesh(np.asarray(vv, np.float32), np.asarray(ff, np.uint32)))
    mm = mf2.to_mesh()   # manifold3d round trip removes the few non-manifold edges quadric decimation leaves
    dm = trimesh.Trimesh(np.asarray(mm.vert_properties)[:, :3], np.asarray(mm.tri_verts), process=False)
    res['decimated'] = dict(tris=int(len(dm.faces)), watertight=bool(dm.is_watertight),
                            winding_consistent=bool(dm.is_winding_consistent),
                            manifold3d_status=str(mf2.status()),
                            volume_change_pct=round(100 * (abs(dm.volume) - vol) / vol, 2))
    p = os.path.join(a.out, 'gate1_patch.stl')
    dm.export(p)
    res['decimated']['stl_MB'] = round(os.path.getsize(p) / 1e6, 1)
    np.savez(os.path.join(a.out, 'patch_render.npz'), v=np.asarray(dm.vertices, np.float32), f=np.asarray(dm.faces, np.uint32))
json.dump(res, open(os.path.join(a.out, 'validation.json'), 'w'), indent=1)
print(json.dumps(res, indent=1))
