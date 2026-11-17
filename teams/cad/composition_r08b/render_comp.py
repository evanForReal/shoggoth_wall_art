#!/usr/bin/env python3
"""bpy Cycles render of an r08 study: python3 render_comp.py ID [--views front,tq] [--mask] [--samples N]
Same camera + lights for every study. Shader: vertex-colour palette by part kind, bump/colour grain by procedural noise (no geometry grain)."""
import sys, os, json, argparse
import numpy as np
import bpy, mathutils
ap = argparse.ArgumentParser(); ap.add_argument('id'); ap.add_argument('--views', default='front'); ap.add_argument('--samples', type=int, default=28); ap.add_argument('--mask', action='store_true')
a = ap.parse_args()
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.join(HERE, 'build'); OUT = os.path.join(HERE, 'renders'); os.makedirs(OUT, exist_ok=True)
d = np.load(f'{B}/{a.id}.npz'); v = d['v'].astype(np.float64); f = d['f'].astype(np.int64); mk = d['mk']; dm = d['dm']; fv = d['fv']; kind = d['kind']
nv = len(v); z = v[:, 2]
def sstep(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)
PAL = {0: (0.26, 0.20, 0.15), 1: (0.26, 0.20, 0.15), 2: (0.34, 0.27, 0.19), 3: (0.38, 0.32, 0.23), 4: (0.42, 0.36, 0.27), 5: (0.31, 0.24, 0.17), 6: (0.86, 0.83, 0.72)}
PALD = {k_: (lambda c_: tuple(np.array(c_) * 0.62 + 0.38 * (0.3 * c_[0] + 0.59 * c_[1] + 0.11 * c_[2])) if k_ != 6 else c_)(v_) for k_, v_ in PAL.items()}   # desaturated ochre/umber (r08b)
col = np.array([PALD.get(int(k), PALD[1]) for k in kind])
col = col * (0.80 + 0.30 * sstep(z / 200.0))[:, None]
dark = 1 - sstep(dm / 36.0); col = col * (1 - 0.90 * dark)[:, None] + np.array([0.012, 0.008, 0.006])[None] * (0.90 * dark)[:, None]
mw = (1 - sstep((mk + 1.5) / 3.0)); mc = np.array(PAL[6]); col = col * (1 - mw[:, None]) + mc[None] * mw[:, None]
fd = 1 - sstep((fv + 0.5) / 1.5); col = col * (1 - fd[:, None]) + np.array([0.006, 0.004, 0.003])[None] * fd[:, None]     # carved smiley recesses near-black
col = np.clip(col, 0, 1) ** 2.2
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; S = 0.001
me = bpy.data.meshes.new('piece'); me.vertices.add(nv); me.vertices.foreach_set('co', (v * S).astype(np.float32).ravel())
me.loops.add(len(f) * 3); me.loops.foreach_set('vertex_index', f.astype(np.int32).ravel()); me.polygons.add(len(f))
me.polygons.foreach_set('loop_start', np.arange(0, len(f) * 3, 3, dtype=np.int32)); me.polygons.foreach_set('loop_total', np.full(len(f), 3, np.int32)); me.update(calc_edges=True)
me.polygons.foreach_set('use_smooth', np.ones(len(f), bool))
ca = me.color_attributes.new('Col', 'FLOAT_COLOR', 'POINT'); ca.data.foreach_set('color', np.concatenate([col, np.ones((nv, 1))], 1).astype(np.float32).ravel())
ob = bpy.data.objects.new('piece', me); sc.collection.objects.link(ob)
mat = bpy.data.materials.new('flesh'); mat.use_nodes = True; nt = mat.node_tree; nt.nodes.clear(); N = nt.nodes; Lk = nt.links.new
out = N.new('ShaderNodeOutputMaterial'); bs = N.new('ShaderNodeBsdfPrincipled'); vc = N.new('ShaderNodeVertexColor'); vc.layer_name = 'Col'
tc = N.new('ShaderNodeTexCoord'); n1 = N.new('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value = 140.0; n1.inputs['Detail'].default_value = 7.0; n1.inputs['Roughness'].default_value = 0.62
n2 = N.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = 9.0; n2.inputs['Detail'].default_value = 3.0
Lk(tc.outputs['Object'], n1.inputs['Vector']); Lk(tc.outputs['Object'], n2.inputs['Vector'])
bump = N.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.55; bump.inputs['Distance'].default_value = 0.0025; Lk(n1.outputs['Fac'], bump.inputs['Height'])
mix = N.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'; mix.inputs['Factor'].default_value = 0.55
ramp = N.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color = (0.55, 0.50, 0.45, 1); ramp.color_ramp.elements[1].color = (1.15, 1.08, 1.0, 1)
mix2 = N.new('ShaderNodeMath'); mix2.operation = 'ADD'; Lk(n1.outputs['Fac'], mix2.inputs[0]); Lk(n2.outputs['Fac'], mix2.inputs[1]); mix2.inputs[1].default_value = 0.0
mm = N.new('ShaderNodeMath'); mm.operation = 'MULTIPLY'; mm.inputs[1].default_value = 0.5; Lk(mix2.outputs[0], mm.inputs[0]); Lk(mm.outputs[0], ramp.inputs['Fac'])
Lk(vc.outputs['Color'], mix.inputs['A']); Lk(ramp.outputs['Color'], mix.inputs['B'])
ao = N.new('ShaderNodeAmbientOcclusion'); ao.inputs['Distance'].default_value = 0.05; Lk(mix.outputs['Result'], ao.inputs['Color']); Lk(ao.outputs['Color'], bs.inputs['Base Color'])
Lk(bump.outputs['Normal'], bs.inputs['Normal']); bs.inputs['Roughness'].default_value = 0.88
if 'Specular IOR Level' in bs.inputs: bs.inputs['Specular IOR Level'].default_value = 0.08
Lk(bs.outputs['BSDF'], out.inputs['Surface']); ob.data.materials.append(mat)
bpy.ops.mesh.primitive_plane_add(size=6.0, location=(0, 0, -0.0004)); wall = bpy.context.object
wm = bpy.data.materials.new('wall'); wm.use_nodes = True; wb = wm.node_tree.nodes['Principled BSDF']
wb.inputs['Base Color'].default_value = (0.0056, 0.0049, 0.0043, 1); wb.inputs['Roughness'].default_value = 1.0; wb.inputs['Specular IOR Level'].default_value = 0.0; wall.data.materials.append(wm)
w_ = bpy.data.worlds.new('w'); sc.world = w_; w_.use_nodes = True; w_.node_tree.nodes['Background'].inputs[0].default_value = (0.0008, 0.0008, 0.0008, 1)
def look(loc, tgt):
    zz = (mathutils.Vector(loc) - mathutils.Vector(tgt)).normalized(); xx = mathutils.Vector((0, 1, 0)).cross(zz).normalized(); yy = zz.cross(xx)
    return mathutils.Matrix(((xx[0], yy[0], zz[0]), (xx[1], yy[1], zz[1]), (xx[2], yy[2], zz[2]))).to_euler()
def light(name, kind_, loc, tgt, power, color, size=0.5, spot=None):
    l = bpy.data.lights.new(name, kind_); l.energy = power; l.color = color
    if kind_ == 'AREA': l.size = size
    if kind_ == 'SPOT': l.spot_size = np.deg2rad(spot); l.spot_blend = 0.85
    o = bpy.data.objects.new(name, l); sc.collection.objects.link(o); o.location = loc; o.rotation_euler = look(loc, tgt)
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = a.samples; sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 1200, 900; sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_depth = '8'
sc.view_settings.view_transform = 'Standard'
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera = cam
VIEWS = {'front': dict(loc=(0, 0, 2.0), tgt=(0, 0, 0), ortho=1.41), 'tq': dict(loc=(0.85, 0.35, 1.7), tgt=(0, 0, 0.05), lens=42)}
WARM = (1.0, 0.88, 0.72)
def setup_lights():
    for o_ in [o_ for o_ in sc.objects if o_.type == 'LIGHT']: bpy.data.objects.remove(o_)
    light('down', 'AREA', (-0.45, 0.95, 0.75), (0, -0.02, 0.05), 150, WARM, 1.3)       # c01-like warm downlight from upper left, soft
    light('down2', 'AREA', (0.55, 0.95, 0.55), (0, 0.0, 0.05), 28, WARM, 0.8)
    light('fill', 'AREA', (0.9, -0.5, 1.2), (0, 0, 0.05), 5, (0.75, 0.8, 1.0), 1.0)
for nm in a.views.split(','):
    cfg = VIEWS[nm]; setup_lights(); cam.location = cfg['loc']; cam.rotation_euler = look(cfg['loc'], cfg['tgt'])
    if 'ortho' in cfg: cam.data.type = 'ORTHO'; cam.data.ortho_scale = cfg['ortho']
    else: cam.data.type = 'PERSP'; cam.data.lens = cfg['lens']
    sc.render.filepath = f'{OUT}/study_{a.id}_{nm}.png'; bpy.ops.render.render(write_still=True); print('rendered', nm, flush=True)
    from PIL import Image as _I; _I.open(sc.render.filepath).convert('RGB').save(sc.render.filepath, optimize=True, compress_level=9)
if a.mask:
    for o_ in [o_ for o_ in sc.objects if o_.type == 'LIGHT']: bpy.data.objects.remove(o_)
    cfg = VIEWS['front']; cam.location = cfg['loc']; cam.rotation_euler = look(cfg['loc'], cfg['tgt']); cam.data.type = 'ORTHO'; cam.data.ortho_scale = cfg['ortho']
    em = bpy.data.materials.new('em'); em.use_nodes = True; n2_ = em.node_tree; n2_.nodes.clear(); o2 = n2_.nodes.new('ShaderNodeOutputMaterial'); e2 = n2_.nodes.new('ShaderNodeEmission')
    e2.inputs['Color'].default_value = (1, 1, 1, 1); n2_.links.new(e2.outputs[0], o2.inputs[0]); ob.data.materials.clear(); ob.data.materials.append(em); wall.hide_render = True
    w_.node_tree.nodes['Background'].inputs[0].default_value = (0, 0, 0, 1); sc.cycles.samples = 8; sc.cycles.use_denoising = False
    sc.render.filepath = f'{OUT}/study_{a.id}_mask_raw.png'; bpy.ops.render.render(write_still=True)
    from PIL import Image
    im = np.asarray(Image.open(sc.render.filepath).convert('L')); Image.fromarray(((im > 100) * 255).astype(np.uint8)).save(f'{OUT}/study_{a.id}_mask.png'); os.remove(sc.render.filepath)
