#!/usr/bin/env python3
"""Headless bpy (Cycles CPU) renders of the Gate-1 patch.

Usage: python3 render_views.py MESH.npz OUTDIR [--w 1200 --h 900 --samples 64 --views front,tq,rake,side]
MESH.npz: v (N,3 float32, mm), f (M,3). Vertex colours (ochre / rust / bone) computed here.
"""
import sys, argparse, os
import numpy as np
import bpy, mathutils
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_patch import Noise

ap = argparse.ArgumentParser()
ap.add_argument('mesh'); ap.add_argument('out')
ap.add_argument('--w', type=int, default=1200); ap.add_argument('--h', type=int, default=900)
ap.add_argument('--samples', type=int, default=64)
ap.add_argument('--views', default='front,tq,rake,side')
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)

d = np.load(a.mesh)
v = d['v'].astype(np.float64); f = d['f'].astype(np.int64)

# ---- vertex colours: dried ochre, bone highlights, rust patches, darker toward back plane
rng = np.random.default_rng(3)
n1 = Noise(rng, 70.0); n2 = Noise(rng, 16.0); n3 = Noise(rng, 5.0)
x, y, z = v[:, 0], v[:, 1], v[:, 2]
def sstep(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)
rust = sstep((n1(x, y, z * 0.3) - 0.05) * 1.6) * sstep(0.3 + 0.8 * n2(x, y, z))
bone = sstep(0.5 + 0.45 * n2(y, z, x) + 0.25 * n3(x, y, z) + 0.35 * (z - 10) / 25.0 - 0.1)
ochre = np.array([0.40, 0.25, 0.11]); boneC = np.array([0.74, 0.62, 0.44]); rustC = np.array([0.30, 0.09, 0.025])
col = ochre[None] * (1 - bone[:, None]) + boneC[None] * bone[:, None]
col = col * (1 - 0.85 * rust[:, None]) + rustC[None] * (0.85 * rust[:, None])
col *= (0.30 + 0.70 * sstep(z / 12.0))[:, None]
col = np.clip(col, 0, 1) ** 2.2  # sRGB -> linear

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
S = 0.001
me = bpy.data.meshes.new('patch')
me.vertices.add(len(v)); me.vertices.foreach_set('co', (v * S).astype(np.float32).ravel())
me.loops.add(len(f) * 3); me.loops.foreach_set('vertex_index', f.astype(np.int32).ravel())
me.polygons.add(len(f)); me.polygons.foreach_set('loop_start', np.arange(0, len(f) * 3, 3, dtype=np.int32))
me.polygons.foreach_set('loop_total', np.full(len(f), 3, np.int32))
me.update(calc_edges=True)
ca = me.color_attributes.new('Col', 'FLOAT_COLOR', 'POINT')
rgba = np.concatenate([col, np.ones((len(v), 1))], 1).astype(np.float32)
ca.data.foreach_set('color', rgba.ravel())
ob = bpy.data.objects.new('patch', me); sc.collection.objects.link(ob)
for p in me.polygons: p.use_smooth = True

mat = bpy.data.materials.new('ochre'); mat.use_nodes = True
nt = mat.node_tree; nt.nodes.clear()
out = nt.nodes.new('ShaderNodeOutputMaterial'); bs = nt.nodes.new('ShaderNodeBsdfPrincipled')
vc = nt.nodes.new('ShaderNodeVertexColor'); vc.layer_name = 'Col'
ao = nt.nodes.new('ShaderNodeAmbientOcclusion'); ao.inputs['Distance'].default_value = 0.012
mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'; mix.inputs[0].default_value = 1.0
nt.links.new(vc.outputs['Color'], ao.inputs['Color'])
nt.links.new(ao.outputs['Color'], bs.inputs['Base Color'])
bs.inputs['Roughness'].default_value = 0.78
for nm, val in (('Specular IOR Level', 0.2),):
    if nm in bs.inputs: bs.inputs[nm].default_value = val
nt.links.new(bs.outputs['BSDF'], out.inputs['Surface'])
ob.data.materials.append(mat)

# wall plane (dark plaster)
bpy.ops.mesh.primitive_plane_add(size=3.0, location=(0, 0, -0.0004))
wall = bpy.context.object
wm = bpy.data.materials.new('wall'); wm.use_nodes = True
wb = wm.node_tree.nodes['Principled BSDF']
wb.inputs['Base Color'].default_value = (0.012, 0.010, 0.009, 1); wb.inputs['Roughness'].default_value = 0.85
wall.data.materials.append(wm)

w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs[0].default_value = (0.012, 0.011, 0.011, 1)

def look(loc, tgt):
    z = (mathutils.Vector(loc) - mathutils.Vector(tgt)).normalized()
    x = mathutils.Vector((0, 1, 0)).cross(z).normalized()
    y = z.cross(x)
    m = mathutils.Matrix(((x[0], y[0], z[0]), (x[1], y[1], z[1]), (x[2], y[2], z[2])))
    return m.to_euler()

def light(name, kind, loc, target, power, color, size=0.25):
    l = bpy.data.lights.new(name, kind); l.energy = power; l.color = color
    if kind == 'AREA': l.size = size
    o = bpy.data.objects.new(name, l); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = look(loc, target)
    return o

WARM = (1.0, 0.68, 0.38)
sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'; sc.cycles.samples = a.samples
sc.cycles.use_denoising = True
try: sc.cycles.denoiser = 'OPENIMAGEDENOISE'
except Exception: pass
sc.render.resolution_x, sc.render.resolution_y = a.w, a.h
sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_depth = '8'
sc.render.image_settings.compression = 100
sc.view_settings.view_transform = 'AgX' if 'AgX' in [x.identifier for x in sc.view_settings.bl_rna.properties['view_transform'].enum_items] else 'Filmic'
sc.view_settings.look = 'None'; sc.view_settings.exposure = 0.0

cam_d = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cam_d); sc.collection.objects.link(cam)
sc.camera = cam

def point(cam, loc, tgt, lens=50, ortho=None):
    cam.location = loc
    cam.rotation_euler = look(loc, tgt)
    if ortho:
        cam.data.type = 'ORTHO'; cam.data.ortho_scale = ortho
    else:
        cam.data.type = 'PERSP'; cam.data.lens = lens

VIEWS = {
    # name: (cam loc, target, lens/ortho, key light loc, key power, spot-on-wall, wall visible)
    'front': dict(loc=(0.0, 0.0, 0.62), tgt=(0.0, -0.005, 0.02), lens=50, key=(-0.18, 0.40, 0.45), kp=22, wall=True),
    'tq':    dict(loc=(0.36, 0.22, 0.42), tgt=(-0.01, -0.02, 0.05), lens=50, key=(-0.25, 0.42, 0.40), kp=22, wall=True),
    'rake':  dict(loc=(0.03, 0.0, 0.17), tgt=(0.04, 0.025, 0.01), lens=50, key=(-0.40, 0.03, 0.07), kp=16, wall=True),
    'side':  dict(loc=(0.9, -0.01, 0.075), tgt=(0.0, -0.01, 0.075), ortho=0.34, key=(0.1, 0.4, 0.3), kp=15, wall=False, rot=True),
}
for name in a.views.split(','):
    cfg = VIEWS[name]
    for o in [o for o in sc.objects if o.type == 'LIGHT']: bpy.data.objects.remove(o)
    wall.hide_render = not cfg['wall']
    point(cam, cfg['loc'], cfg['tgt'], cfg.get('lens', 50), cfg.get('ortho'))
    light('key', 'AREA', cfg['key'], (0, 0, 0.02), cfg['kp'] * (1.0), WARM, 0.35)
    light('fill', 'AREA', (0.45, -0.2, 0.35), (0, 0, 0.02), 6, (0.7, 0.75, 1.0), 0.5)
    light('rim', 'AREA', (0.0, -0.1, 0.25), (0, 0, 0.02), 8, (1.0, 0.6, 0.35), 0.3)
    sc.render.filepath = os.path.join(a.out, f'{name}.png')
    bpy.ops.render.render(write_still=True)
    print('rendered', name)
