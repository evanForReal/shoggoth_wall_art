#!/usr/bin/env python3
"""Gate 2 character pass: flow-aligned fibre-grain displacement on the clamped SDF mesh, hosted in bpy.

Usage: python3 sculpt.py DIR [--amp-rib 0.9 --amp-mem 0.35 --tag main]
DIR holds patch_clean.npz (clamped mesh), occ_clamped.npy, grid.json, flow.npy (from gen_patch.py/minwall.py).
Writes DIR/sculpt_<tag>.npz (v, f) and DIR/sculpt_<tag>.json.

Steps
 1. Taubin smoothing (volume-preserving) of the 0.5 mm marching-cubes mesh: removes staircase and small bead knobs;
    extra masked Taubin on the limb (pitting). Back-plane and flat-top vertices are pinned.
 2. One midpoint subdivision (edge ~0.5 mm -> ~0.25 mm) so 0.7-1.2 mm grain is resolved.
 3. Displacement along vertex normals, outward only (never thins a wall): multi-octave RIDGED noise sampled in
    flow-aligned, strongly stretched coordinates (along-flow wavelength 4-14 mm, across-flow 0.7-2.5 mm),
    stronger on ribs than on membranes, scaled to zero near narrow gaps (< 1.8 mm) so neighbouring surfaces cannot touch.
 4. Mesh is loaded into bpy (mesh.validate, Blender normals) as the host for the pass and the renders.
"""
import sys, os, json, time, argparse
import numpy as np
from scipy import ndimage as ndi, sparse
from scipy.spatial import cKDTree
from scipy.interpolate import CubicSpline

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_patch import LIMB_PTS, LIMB_R, SHELF_Y

ap = argparse.ArgumentParser(); ap.add_argument('dir')
ap.add_argument('--amp-rib', type=float, default=0.9); ap.add_argument('--amp-mem', type=float, default=0.35)
ap.add_argument('--tag', default='main'); ap.add_argument('--taubin', type=int, default=8)
ap.add_argument('--along-scale', type=float, default=1.0, help='multiplies along-flow wavelengths (more fibre-like anisotropy)')
ap.add_argument('--grain-scale', type=float, default=1.0, help='multiplies across-flow wavelengths')
a = ap.parse_args()
t0 = time.time()
g = json.load(open(os.path.join(a.dir, 'grid.json'))); vox = g['vox']
d = np.load(os.path.join(a.dir, 'patch_clean.npz')); v = d['v'].astype(np.float64); f = d['f'].astype(np.int64)
print('loaded', v.shape, f.shape, flush=True)


def sstep(t):
    t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)


def vnormals(v, f):
    fn = np.cross(v[f[:, 1]] - v[f[:, 0]], v[f[:, 2]] - v[f[:, 0]])
    vn = np.zeros_like(v)
    for c in range(3):
        for k in range(3):
            vn[:, c] += np.bincount(f[:, k], weights=fn[:, c], minlength=len(v))
    return vn / (np.linalg.norm(vn, axis=1)[:, None] + 1e-12)


def adjacency(f, nv):
    e = np.concatenate([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]]); e = np.concatenate([e, e[:, ::-1]])
    A = sparse.csr_matrix((np.ones(len(e), np.float32), (e[:, 0], e[:, 1])), shape=(nv, nv)); A.data[:] = 1
    dg = np.asarray(A.sum(1)).ravel(); dg[dg == 0] = 1
    return A, dg


def taubin(v, A, dg, free, iters, lam=0.5, mu=-0.53):
    v = v.copy()
    for _ in range(iters):
        for k in (lam, mu):
            lap = (A @ v) / dg[:, None] - v
            v[free] += k * lap[free]
    return v


# ---- masks on the original mesh
vn0 = vnormals(v, f)
back = v[:, 2] < 0.55
plate = (np.abs(v[:, 1] - SHELF_Y) < 0.35) & (vn0[:, 1] > 0.9)
sp = CubicSpline(np.r_[0, np.cumsum(np.linalg.norm(np.diff(LIMB_PTS, axis=0), axis=1))], LIMB_PTS)
Cl = sp(np.arange(0, sp.x[-1], 0.5))
dl, _ = cKDTree(Cl).query(v, workers=4)
limb = (dl < LIMB_R + 4.0) & (v[:, 2] < 30)
A, dg = adjacency(f, len(v))
free = ~(back | plate)
v1 = taubin(v, A, dg, free, a.taubin)
v1 = taubin(v1, A, dg, free & limb, 14)           # extra limb pit smoothing
mv = np.linalg.norm(v1 - v, axis=1)
print('taubin done; max/mean move mm', round(float(mv.max()), 2), round(float(mv.mean()), 3), round(time.time() - t0, 1), flush=True)
del A

# ---- one-level midpoint subdivision
nv = len(v1)
e = np.sort(np.concatenate([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]]), axis=1)
key = e[:, 0] * nv + e[:, 1]
uk, inv = np.unique(key, return_inverse=True)
ea, eb = uk // nv, uk % nv
vm = 0.5 * (v1[ea] + v1[eb])
mid = (nv + inv).reshape(3, -1) if False else None
nf = len(f)
m01 = nv + inv[:nf]; m12 = nv + inv[nf:2 * nf]; m20 = nv + inv[2 * nf:]
a0, a1, a2 = f[:, 0], f[:, 1], f[:, 2]
F2 = np.concatenate([np.stack([a0, m01, m20], 1), np.stack([a1, m12, m01], 1), np.stack([a2, m20, m12], 1), np.stack([m01, m12, m20], 1)])
V2 = np.concatenate([v1, vm])
del e, key, inv, vm
edge_len = np.linalg.norm(V2[F2[:, 0]] - V2[F2[:, 1]], axis=1)
print('subdivided', V2.shape, F2.shape, 'mean edge mm', round(float(edge_len.mean()), 3), round(time.time() - t0, 1), flush=True)
del edge_len
is_back = np.concatenate([back, back[ea] & back[eb]]); is_plate = np.concatenate([plate, plate[ea] & plate[eb]])
is_limb = np.concatenate([limb, limb[ea] & limb[eb]])
del ea, eb
N2 = vnormals(V2, F2)

# ---- clearance factor from narrow gaps in the clamped field (voxel closing)
occ = np.load(os.path.join(a.dir, 'occ_clamped.npy'))
R_GAP = 0.9
dil = ndi.distance_transform_edt(~occ, sampling=vox).astype(np.float32) <= R_GAP
closed = ndi.distance_transform_edt(dil, sampling=vox).astype(np.float32) > R_GAP
del dil
gap = closed & ~occ
del closed
distG = ndi.distance_transform_edt(~gap, sampling=vox).astype(np.float32) if gap.any() else np.full(occ.shape, 99, np.float32)
print('gap voxels', int(gap.sum()), round(time.time() - t0, 1), flush=True)
del gap, occ
ix = np.clip(np.round((V2[:, 0] - g['x0']) / vox).astype(int), 0, distG.shape[0] - 1)
iy = np.clip(np.round((V2[:, 1] - g['y0']) / vox).astype(int), 0, distG.shape[1] - 1)
iz = np.clip(np.round((V2[:, 2] - g['z0']) / vox).astype(int), 0, distG.shape[2] - 1)
clear = sstep((distG[ix, iy, iz] - 0.4) / 1.2)
del distG, ix, iy, iz

# ---- flow-aligned ridged noise
class PNoise:
    def __init__(self, rng, shape=(192, 192, 48)):
        a_ = ndi.gaussian_filter(rng.standard_normal(shape), 1.0, mode='wrap'); a_ /= a_.std()
        self.a = ndi.spline_filter(a_, order=3, mode='grid-wrap')

    def __call__(self, u, v_, w):
        out = np.empty(len(u))
        for s in range(0, len(u), 1_000_000):
            c = np.stack([u[s:s + 1_000_000], v_[s:s + 1_000_000], w[s:s + 1_000_000]])
            out[s:s + 1_000_000] = ndi.map_coordinates(self.a, c, order=3, prefilter=False, mode='grid-wrap')
        return out


flow = np.load(os.path.join(a.dir, 'flow.npy')).astype(np.float64)
fx = (V2[:, 0] - g['x0']) / vox; fy = (V2[:, 1] - g['y0']) / vox
th = ndi.map_coordinates(flow, [np.clip(fx, 0, flow.shape[0] - 1), np.clip(fy, 0, flow.shape[1] - 1)], order=1)
cth, sth = np.cos(th), np.sin(th)
U = V2[:, 0] * cth + V2[:, 1] * sth; W_ = -V2[:, 0] * sth + V2[:, 1] * cth; Z = V2[:, 2]
rng = np.random.default_rng(11)
oct_ = [  # (lambda_along, lambda_across, lambda_z, weight)  all mm
    (14.0 * a.along_scale, 2.5 * a.grain_scale, 6.0, 0.8),
    (8.0 * a.along_scale, 1.2 * a.grain_scale, 4.0, 1.0),
    (4.5 * a.along_scale, 0.75 * a.grain_scale, 2.5, 0.6),
]
ridge = np.zeros(len(V2)); wsum = 0
for (lu, lv, lz, wt) in oct_:
    nz_ = PNoise(rng)(U * 5.0 / lu + 40, W_ * 5.0 / lv + 70, Z * 5.0 / lz)
    ridge += wt * (1 - np.abs(np.clip(nz_ / 2.2, -1, 1))) ** 2
    wsum += wt
    print('octave', lu, lv, round(time.time() - t0, 1), flush=True)
ridge /= wsum
w_rib = sstep((Z - 6.0) / 6.0)
amp = (a.amp_mem + (a.amp_rib - a.amp_mem) * w_rib) * clear
amp = np.where(is_back | is_plate, 0.0, amp)
amp = np.where(is_limb, np.minimum(amp, 0.45), amp)
disp = amp * ridge
V3 = V2 + N2 * disp[:, None]
print('displacement mm: mean', round(float(disp.mean()), 3), 'p99', round(float(np.percentile(disp, 99)), 3), 'max', round(float(disp.max()), 3), flush=True)

# ---- host in bpy: validate + Blender normals, report
import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
me = bpy.data.meshes.new('sculpt')
me.vertices.add(len(V3)); me.vertices.foreach_set('co', V3.astype(np.float32).ravel())
me.loops.add(len(F2) * 3); me.loops.foreach_set('vertex_index', F2.astype(np.int32).ravel())
me.polygons.add(len(F2)); me.polygons.foreach_set('loop_start', np.arange(0, len(F2) * 3, 3, dtype=np.int32))
me.polygons.foreach_set('loop_total', np.full(len(F2), 3, np.int32))
me.update(calc_edges=True)
changed = me.validate(verbose=False)
co = np.empty(len(V3) * 3, np.float32); me.vertices.foreach_get('co', co)
print('bpy mesh', len(me.vertices), len(me.polygons), 'validate() changed:', changed, flush=True)
bpy_v = co.reshape(-1, 3)
np.savez(os.path.join(a.dir, 'sculpt_%s.npz' % a.tag), v=bpy_v, f=F2.astype(np.uint32))
json.dump(dict(tag=a.tag, amp_rib=a.amp_rib, amp_mem=a.amp_mem, taubin=a.taubin, along_scale=a.along_scale, grain_scale=a.grain_scale, subdiv=1, verts=int(len(V3)), tris=int(len(F2)),
               taubin_max_move_mm=round(float(mv.max()), 2), taubin_mean_move_mm=round(float(mv.mean()), 3),
               disp_mean_mm=round(float(disp.mean()), 3), disp_p99_mm=round(float(np.percentile(disp, 99)), 3),
               disp_max_mm=round(float(disp.max()), 3), bpy_validate_changed=bool(changed), seconds=round(time.time() - t0, 1)),
          open(os.path.join(a.dir, 'sculpt_%s.json' % a.tag), 'w'), indent=1)
print('done', round(time.time() - t0, 1))
