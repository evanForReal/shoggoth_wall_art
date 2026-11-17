#!/usr/bin/env python3
"""bpy Cycles value-blocked render: python3 render_comp.py ID [--views front,tq] [--mask]  -> renders/study_<ID>_<view>.png (+ study_<ID>_mask.png)
Same camera + lights for every study. Front = orthographic (mask png shares its framing exactly: 1.175 mm/px)."""
import sys, os, json, argparse
import numpy as np
import bpy, mathutils
ap = argparse.ArgumentParser(); ap.add_argument('id'); ap.add_argument('--views', default='front'); ap.add_argument('--samples', type=int, default=40)
ap.add_argument('--mask', action='store_true'); ap.add_argument('--out', default=None)
a = ap.parse_args()
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.join(HERE, 'build'); OUT = a.out or os.path.join(HERE, 'renders'); os.makedirs(OUT, exist_ok=True)
d = np.load(os.path.join(B, a.id + '.npz')); v = d['v'].astype(np.float64); f = d['f'].astype(np.int64); mk = d['mk']; dm = d['dm']
meta = json.load(open(os.path.join(B, a.id + '_meta.json')))
nv = len(v); z = v[:, 2]
def sstep(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)
FLESH = np.array([0.39, 0.28, 0.19]); MASK = np.array([1.0, 0.96, 0.84]); MAWC = np.array([0.012, 0.008, 0.006])
col = FLESH[None] * (0.82 + 0.30 * sstep(z / 220.0))[:, None]
dark = 1 - sstep(dm / 38.0)                       # maw interior + rim falloff (rim never lighter than body)
col = col * (1 - 0.88 * dark)[:, None] + MAWC[None] * (0.88 * dark)[:, None]
mw = (1 - sstep((mk + 1.5) / 3.0))                # mask dome surface = the ONE pale value
col = col * (1 - mw[:, None]) + MASK[None] * mw[:, None]
col = np.clip(col, 0, 1) ** 2.2

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; S = 0.001
me = bpy.data.meshes.new('piece')
me.vertices.add(nv); me.vertices.foreach_set('co', (v * S).astype(np.float32).ravel())
me.loops.add(len(f) * 3); me.loops.foreach_set('vertex_index', f.astype(np.int32).ravel())
me.polygons.add(len(f)); me.polygons.foreach_set('loop_start', np.arange(0, len(f) * 3, 3, dtype=np.int32))
me.polygons.foreach_set('loop_total', np.full(len(f), 3, np.int32)); me.update(calc_edges=True)
# marching cubes winding: flip so normals face out
me.polygons.foreach_set('use_smooth', np.ones(len(f), bool))
ca = me.color_attributes.new('Col', 'FLOAT_COLOR', 'POINT')
ca.data.foreach_set('color', np.concatenate([col, np.ones((nv, 1))], 1).astype(np.float32).ravel())
ob = bpy.data.objects.new('piece', me); sc.collection.objects.link(ob)
mat = bpy.data.materials.new('flesh'); mat.use_nodes = True; nt = mat.node_tree; nt.nodes.clear()
out = nt.nodes.new('ShaderNodeOutputMaterial'); bs = nt.nodes.new('ShaderNodeBsdfPrincipled'); vc = nt.nodes.new('ShaderNodeVertexColor'); vc.layer_name = 'Col'
ao = nt.nodes.new('ShaderNodeAmbientOcclusion'); ao.inputs['Distance'].default_value = 0.06
nt.links.new(vc.outputs['Color'], ao.inputs['Color']); nt.links.new(ao.outputs['Color'], bs.inputs['Base Color'])
bs.inputs['Roughness'].default_value = 0.85
if 'Specular IOR Level' in bs.inputs: bs.inputs['Specular IOR Level'].default_value = 0.1
nt.links.new(bs.outputs['BSDF'], out.inputs['Surface']); ob.data.materials.append(mat)
bpy.ops.mesh.primitive_plane_add(size=6.0, location=(0, 0, -0.0004)); wall = bpy.context.object
wm = bpy.data.materials.new('wall'); wm.use_nodes = True; wb = wm.node_tree.nodes['Principled BSDF']
wb.inputs['Base Color'].default_value = (0.0075, 0.0065, 0.0058, 1); wb.inputs['Roughness'].default_value = 1.0; wb.inputs['Specular IOR Level'].default_value = 0.0; wall.data.materials.append(wm)
w_ = bpy.data.worlds.new('w'); sc.world = w_; w_.use_nodes = True; w_.node_tree.nodes['Background'].inputs[0].default_value = (0.0008, 0.0008, 0.0008, 1)

def look(loc, tgt):
    zz = (mathutils.Vector(loc) - mathutils.Vector(tgt)).normalized(); xx = mathutils.Vector((0, 1, 0)).cross(zz).normalized(); yy = zz.cross(xx)
    return mathutils.Matrix(((xx[0], yy[0], zz[0]), (xx[1], yy[1], zz[1]), (xx[2], yy[2], zz[2]))).to_euler()
def light(name, kind, loc, tgt, power, color, size=0.5):
    l = bpy.data.lights.new(name, kind); l.energy = power; l.color = color
    if kind == 'AREA': l.size = size
    o = bpy.data.objects.new(name, l); sc.collection.objects.link(o); o.location = loc; o.rotation_euler = look(loc, tgt)
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = a.samples; sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 1200, 900
sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_depth = '8'
sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera = cam
VIEWS = {'front': dict(loc=(0, 0, 2.0), tgt=(0, 0, 0), ortho=1.41), 'tq': dict(loc=(0.85, 0.35, 1.7), tgt=(0, 0, 0.05), lens=42)}
# LOCKED lighting (identical for every study): soft raking key from upper-left, faint cool fill
KEY = (-0.95, 0.62, 0.78); WARM = (1.0, 0.90, 0.78)
def setup_lights():
    for o_ in [o_ for o_ in sc.objects if o_.type == 'LIGHT']: bpy.data.objects.remove(o_)
    light('key', 'AREA', KEY, (0, 0, 0.05), 120, WARM, 1.4)
    light('fill', 'AREA', (0.9, -0.5, 1.2), (0, 0, 0.05), 6, (0.75, 0.8, 1.0), 1.0)
for nm in a.views.split(','):
    cfg = VIEWS[nm]; setup_lights()
    cam.location = cfg['loc']; cam.rotation_euler = look(cfg['loc'], cfg['tgt'])
    if 'ortho' in cfg: cam.data.type = 'ORTHO'; cam.data.ortho_scale = cfg['ortho']
    else: cam.data.type = 'PERSP'; cam.data.lens = cfg['lens']
    sc.render.filepath = os.path.join(OUT, f'study_{a.id}_{nm}.png'); bpy.ops.render.render(write_still=True); print('rendered', nm, flush=True)
    from PIL import Image as _I; _I.open(sc.render.filepath).convert('RGB').save(sc.render.filepath, optimize=True, compress_level=9)   # <= 1 MB
if a.mask:
    for o_ in [o_ for o_ in sc.objects if o_.type == 'LIGHT']: bpy.data.objects.remove(o_)
    cfg = VIEWS['front']; cam.location = cfg['loc']; cam.rotation_euler = look(cfg['loc'], cfg['tgt']); cam.data.type = 'ORTHO'; cam.data.ortho_scale = cfg['ortho']
    em = bpy.data.materials.new('em'); em.use_nodes = True; n2 = em.node_tree; n2.nodes.clear(); o2 = n2.nodes.new('ShaderNodeOutputMaterial'); e2 = n2.nodes.new('ShaderNodeEmission')
    e2.inputs['Color'].default_value = (1, 1, 1, 1); e2.inputs['Strength'].default_value = 1.0; n2.links.new(e2.outputs[0], o2.inputs[0])
    ob.data.materials.clear(); ob.data.materials.append(em); wall.hide_render = True
    w_.node_tree.nodes['Background'].inputs[0].default_value = (0, 0, 0, 1)
    sc.cycles.samples = 8; sc.cycles.use_denoising = False
    sc.render.filepath = os.path.join(OUT, f'study_{a.id}_mask_raw.png'); bpy.ops.render.render(write_still=True)
    from PIL import Image
    im = np.asarray(Image.open(sc.render.filepath).convert('L')); Image.fromarray(((im > 100) * 255).astype(np.uint8)).save(os.path.join(OUT, f'study_{a.id}_mask.png')); os.remove(sc.render.filepath)
