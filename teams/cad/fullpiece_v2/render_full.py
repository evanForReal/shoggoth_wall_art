#!/usr/bin/env python3
"""bpy Cycles renders of a full-piece variant on a dark wall: 1C crevice shader + locked warm lighting.

Usage: python3 render_full.py DIR VARIANT OUTDIR [--views front,tq,rake,side] [--w 1200 --h 900 --samples 48]
"""
import sys, os, json, argparse
import numpy as np
import bpy, mathutils
from scipy import ndimage as ndi, sparse
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'gate2'))
from gen_patch import Noise

ap = argparse.ArgumentParser(); ap.add_argument('dir'); ap.add_argument('variant'); ap.add_argument('out')
ap.add_argument('--views', default='front,tq'); ap.add_argument('--w', type=int, default=1200); ap.add_argument('--h', type=int, default=900)
ap.add_argument('--samples', type=int, default=48)
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
d = np.load(os.path.join(a.dir, a.variant + '.npz')); v = d['v'].astype(np.float64); f = d['f'].astype(np.int64)
meta = json.load(open(os.path.join(a.dir, a.variant + '_meta.json')))
aux = d['aux']; calm_v, maw_sd, eye_t, teeth_t = aux[:, 0], aux[:, 1], aux[:, 2], aux[:, 3]
x, y, z = v[:, 0], v[:, 1], v[:, 2]


def sstep(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)


# ---- crevice shading (scaled for a 914 mm piece)
res = 4.0; nxg = int(930 / res) + 2
gx = np.clip(((x + 465) / res).astype(int), 0, nxg - 1); gy = np.clip(((y + 465) / res).astype(int), 0, nxg - 1)
H = np.zeros((nxg, nxg)); o = np.argsort(z); H[gx[o], gy[o]] = z[o]
Hf = ndi.gaussian_filter(ndi.maximum_filter(H, size=15), 2.0)
depth = ndi.map_coordinates(Hf, [np.clip((x + 465) / res, 0, nxg - 1), np.clip((y + 465) / res, 0, nxg - 1)], order=1) - z
HL = ndi.gaussian_filter(ndi.maximum_filter(H, size=41), 4.0)
depthL = ndi.map_coordinates(HL, [np.clip((x + 465) / res, 0, nxg - 1), np.clip((y + 465) / res, 0, nxg - 1)], order=1) - z
for sh in meta['shelves']:                         # under-shelf fibre fans sit in shadow of the plate
    inx = (x > sh['x_range'][0] - 10) & (x < sh['x_range'][1] + 10) & (y < sh['top_y'] - 8) & (y > sh['top_y'] - 200)
    depth = np.where(inx & (z > 40), depth + 40 * sstep((sh['top_y'] - y) / 120.0), depth)
nv = len(v)
e = np.concatenate([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]]); e = np.concatenate([e, e[:, ::-1]])
A = sparse.csr_matrix((np.ones(len(e), np.float32), (e[:, 0], e[:, 1])), shape=(nv, nv)); A.data[:] = 1
dg = np.asarray(A.sum(1)).ravel(); dg[dg == 0] = 1
m = v.copy()
for _ in range(4): m = (A @ m) / dg[:, None]
fn = np.cross(v[f[:, 1]] - v[f[:, 0]], v[f[:, 2]] - v[f[:, 0]]); vn = np.zeros_like(v)
for c_ in range(3):
    for k in range(3): vn[:, c_] += np.bincount(f[:, k], weights=fn[:, c_], minlength=nv)
vn /= np.linalg.norm(vn, axis=1)[:, None] + 1e-12
cav = ((m - v) * vn).sum(1)
del A, e, m
rng = np.random.default_rng(3); n1 = Noise(rng, 330.0, lo=(-520, -520, -20), hi=(520, 520, 330)); n3 = Noise(rng, 30.0, lo=(-520, -520, -20), hi=(520, 520, 330))
dark = np.clip(0.85 * sstep(depth / 40.0) + 0.45 * sstep(depthL / 110.0) + 0.50 * sstep(cav / 4.5) - 0.12 * sstep(-cav / 3.0), 0, 1)
dark = np.clip(dark + 0.10 * (n3(x, y, z) - 0.3), 0, 1)
dark = np.where(calm_v > 0.6, dark * (1.0 - 0.22 * np.clip(calm_v, 0, 1)), dark)          # calm muscle bellies read lighter/smoother
dark = np.clip(np.maximum(dark, 0.93 * (maw_sd < 6) * sstep((60 - z) / 40.0) * (teeth_t < 0.5)), 0, 1)   # maw interior: unmistakably dark
# tonal zones (ochre / bone / rust) from low-frequency noise, per the locked palette
nz_ = n1(x * 0.9 + 70, y * 0.9 - 40, z * 0.1)
zb_ = sstep((-nz_ - 0.05) / 0.5)[:, None]; zr_ = sstep((nz_ - 0.15) / 0.5)[:, None]
pale_o, mid_o = np.array([0.80, 0.62, 0.31]), np.array([0.45, 0.27, 0.10])
pale_b, mid_b = np.array([0.82, 0.73, 0.55]), np.array([0.50, 0.35, 0.19])
pale_r, mid_r = np.array([0.66, 0.36, 0.17]), np.array([0.38, 0.16, 0.07])
pale = pale_o * (1 - zb_ - zr_) + pale_b * zb_ + pale_r * zr_; mid = mid_o * (1 - zb_ - zr_) + mid_b * zb_ + mid_r * zr_
deep = np.array([0.045, 0.028, 0.018])
lo = np.clip(dark / 0.5, 0, 1)[:, None]; hi = np.clip((dark - 0.5) / 0.5, 0, 1)[:, None]
col = np.where(dark[:, None] < 0.5, pale * (1 - lo) + mid * lo, mid * (1 - hi) + deep * hi)
rw = 0.40 * sstep(n1(x, y, z * 0.2) + 0.2) * (4 * dark * (1 - dark))
col = col * (1 - rw[:, None]) + np.array([0.50, 0.19, 0.06]) * rw[:, None] * (0.4 + dark)[:, None]
# teeth: dirty ivory;  eyes: sickly sclera (iris pits go dark by cavity)
tw = (0.65 * teeth_t * (1 - 0.6 * sstep(depth / 60.0)))[:, None]
col = col * (1 - tw) + np.array([0.72, 0.62, 0.42]) * tw * (1 - 0.5 * dark[:, None])
ew = (0.55 * eye_t * (1 - 0.8 * sstep(cav / 2.0)))[:, None]
col = col * (1 - ew) + np.array([0.78, 0.66, 0.40]) * ew * (1 - 0.6 * dark[:, None])
# mask: pale carved bone (the ONE clean contrasting element), weathered: cavity-shaded + stain streaks, darker in the groove/eyes
mk = meta['mask']; dx, dy = x - mk['centre'][0], y - mk['centre'][1]
mq = np.sqrt((dx / mk['semi'][0]) ** 2 + (dy / mk['semi'][1]) ** 2)
mw = (1 - sstep((mq - 1.0) / 0.06)) * (z > 20)
stain = np.clip(0.55 * sstep(n3(x * 0.6, y * 0.25, z * 0.2) * 0.8 + 0.1) * (0.4 + 0.6 * sstep((-dy / mk['semi'][1] + 0.3) / 1.0)) * (0.5 + meta['mask']['weather']), 0, 0.7)
bone = np.array([0.86, 0.80, 0.66]) * (0.55 + 0.45 * (1 - sstep(cav / 3.0)))[:, None] * (1 - stain)[:, None] + np.array([0.45, 0.30, 0.14]) * stain[:, None]
bone = bone * (1 - 0.65 * sstep(depth / 28.0))[:, None]
col = col * (1 - mw[:, None]) + bone * mw[:, None]
col = np.clip(col, 0, 1) ** 2.2
print('colours done', flush=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; S = 0.001
me = bpy.data.meshes.new('piece')
me.vertices.add(nv); me.vertices.foreach_set('co', (v * S).astype(np.float32).ravel())
me.loops.add(len(f) * 3); me.loops.foreach_set('vertex_index', f.astype(np.int32).ravel())
me.polygons.add(len(f)); me.polygons.foreach_set('loop_start', np.arange(0, len(f) * 3, 3, dtype=np.int32))
me.polygons.foreach_set('loop_total', np.full(len(f), 3, np.int32)); me.update(calc_edges=True)
ca = me.color_attributes.new('Col', 'FLOAT_COLOR', 'POINT')
ca.data.foreach_set('color', np.concatenate([col, np.ones((nv, 1))], 1).astype(np.float32).ravel())
ob = bpy.data.objects.new('piece', me); sc.collection.objects.link(ob)
for p in me.polygons: p.use_smooth = True
mat = bpy.data.materials.new('ochre'); mat.use_nodes = True; nt = mat.node_tree; nt.nodes.clear()
out = nt.nodes.new('ShaderNodeOutputMaterial'); bs = nt.nodes.new('ShaderNodeBsdfPrincipled')
vc = nt.nodes.new('ShaderNodeVertexColor'); vc.layer_name = 'Col'
ao = nt.nodes.new('ShaderNodeAmbientOcclusion'); ao.inputs['Distance'].default_value = 0.04
nt.links.new(vc.outputs['Color'], ao.inputs['Color']); nt.links.new(ao.outputs['Color'], bs.inputs['Base Color'])
bs.inputs['Roughness'].default_value = 0.78
if 'Specular IOR Level' in bs.inputs: bs.inputs['Specular IOR Level'].default_value = 0.2
nt.links.new(bs.outputs['BSDF'], out.inputs['Surface']); ob.data.materials.append(mat)
bpy.ops.mesh.primitive_plane_add(size=6.0, location=(0, 0, -0.0004)); wall = bpy.context.object
wm = bpy.data.materials.new('wall'); wm.use_nodes = True; wb = wm.node_tree.nodes['Principled BSDF']
wb.inputs['Base Color'].default_value = (0.012, 0.010, 0.009, 1); wb.inputs['Roughness'].default_value = 0.85; wall.data.materials.append(wm)
w_ = bpy.data.worlds.new('w'); sc.world = w_; w_.use_nodes = True; w_.node_tree.nodes['Background'].inputs[0].default_value = (0.012, 0.011, 0.011, 1)


def look(loc, tgt):
    zz = (mathutils.Vector(loc) - mathutils.Vector(tgt)).normalized(); xx = mathutils.Vector((0, 1, 0)).cross(zz).normalized(); yy = zz.cross(xx)
    return mathutils.Matrix(((xx[0], yy[0], zz[0]), (xx[1], yy[1], zz[1]), (xx[2], yy[2], zz[2]))).to_euler()


def light(name, kind, loc, tgt, power, color, size=0.5, spot=None):
    l = bpy.data.lights.new(name, kind); l.energy = power; l.color = color
    if kind == 'AREA': l.size = size
    if kind == 'SPOT': l.spot_size = np.deg2rad(spot); l.spot_blend = 0.9
    o = bpy.data.objects.new(name, l); sc.collection.objects.link(o); o.location = loc; o.rotation_euler = look(loc, tgt)


WARM = (1.0, 0.68, 0.38)
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = a.samples; sc.cycles.use_denoising = True
try: sc.cycles.denoiser = 'OPENIMAGEDENOISE'
except Exception: pass
sc.render.resolution_x, sc.render.resolution_y = a.w, a.h
sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_depth = '8'; sc.render.image_settings.compression = 100
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'None'; sc.view_settings.exposure = 0.0
cam_d = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cam_d); sc.collection.objects.link(cam); sc.camera = cam
VIEWS = {
    'front': dict(loc=(0, 0.02, 1.9), tgt=(0, 0.02, 0.05), lens=40, wall=True, key=(-0.55, 1.1, 1.3), kp=95),
    'tq': dict(loc=(0.95, 0.45, 1.55), tgt=(-0.02, 0.0, 0.08), lens=40, wall=True, key=(-0.55, 1.1, 1.3), kp=95),
    'rake': dict(loc=(-0.30, 0.20, 0.62), tgt=(-0.105, 0.165, 0.06), lens=50, wall=True, key=(-1.0, 0.10, 0.18), kp=55),
    'maw': dict(loc=(-0.02, -0.02, 0.62), tgt=(-0.095, -0.078, 0.04), lens=45, wall=True, key=(-0.45, 0.45, 0.55), kp=60),
    'side': dict(loc=(2.2, 0.0, 0.15), tgt=(0.0, 0.0, 0.15), ortho=1.25, wall=False, key=(0.5, 1.2, 0.9), kp=90),
}
for nm in a.views.split(','):
    cfg = VIEWS[nm]
    for o_ in [o_ for o_ in sc.objects if o_.type == 'LIGHT']: bpy.data.objects.remove(o_)
    wall.hide_render = not cfg['wall']
    cam.location = cfg['loc']; cam.rotation_euler = look(cfg['loc'], cfg['tgt'])
    if cfg.get('ortho'): cam.data.type = 'ORTHO'; cam.data.ortho_scale = cfg['ortho']
    else: cam.data.type = 'PERSP'; cam.data.lens = cfg['lens']
    light('key', 'AREA', cfg['key'], (0, 0, 0.05), cfg['kp'], WARM, 0.7)
    light('fill', 'AREA', (0.9, -0.4, 0.9), (0, 0, 0.05), 5, (0.7, 0.75, 1.0), 0.9)
    light('rim', 'AREA', (0.0, -0.3, 0.6), (0, 0, 0.05), 9, (1.0, 0.6, 0.35), 0.5)
    if cfg['wall']:
        light('wash1', 'SPOT', (-0.35, 0.95, 0.5), (-0.1, 0.1, 0.0), 55, WARM, spot=75)     # c01-style downlights
        light('wash2', 'SPOT', (0.45, 0.95, 0.5), (0.2, 0.1, 0.0), 55, WARM, spot=75)
    sc.render.filepath = os.path.join(a.out, f'{a.variant}_{nm}.png')
    bpy.ops.render.render(write_still=True); print('rendered', nm, flush=True)
