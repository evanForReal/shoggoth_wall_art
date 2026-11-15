#!/usr/bin/env python3
"""P0 geometry entry point.  One command:

    python prototype/p0/generate.py [--params prototype/p0/params.json] [--out prototype/p0/out]
                                    [--architecture rib_ladder|lattice|spine_beam] [--joint dovetail_bolt|tongue_pin|socket_through_bolt]
                                    [--style calcified_webbing|bone_crust|flowstone|rust_blister|mummified_ochre] [--seed N]
                                    [--no-previews] [--variants] [--skin-only-swap]

Writes (under --out): underlay.stl skin.stl assembly.stl segments/seg_NN.stl segments/seg_NN_print.stl
segments.json joints.json geometry_manifest.json ; previews to prototype/p0/reports/previews/.
Units mm. Frame per docs/PROTOTYPE_SPEC.md.
"""
import argparse, hashlib, json, os, sys, time
import numpy as np
import trimesh

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from model.structural.underlay import build_underlay          # noqa: E402
from model.structural.segmenter import segment, print_orientation   # noqa: E402
from model.aesthetic.skin import skin, STYLES                  # noqa: E402
from model.aesthetic.render import sheet, PALETTES             # noqa: E402
from model.mtools import to_trimesh, to_manifold, union, clean_mesh   # noqa: E402

RHO = {"PETG": 1.27e-3, "PLA": 1.24e-3}   # g/mm^3


def sha(mesh):
    return hashlib.sha256(np.round(mesh.vertices, 4).tobytes() + mesh.faces.tobytes()).hexdigest()[:16]


def manifest(res, p):
    span = res["span"]
    s = np.linspace(0, span.L, 91)
    T, N, U = span.frame(s)
    A, B, R = span.ABR(s)
    Ai, Bi, Ri = span.ABR(s, p["shell_wall"])
    m = res["meta"]
    pf = m["pad_frame"]
    o = np.array(pf["origin"])
    shelf_center = [float(o[0]), float(o[1]), m["ztop"]]
    return dict(
        schema="p0-geometry-manifest-v1", units="mm", architecture=m["architecture"], joint_type=m["joint_type"],
        centerline=[dict(s=float(a), xyz=span.point(a)[0].round(3).tolist(), T=t.round(5).tolist(),
                         N=n.round(5).tolist(), U=u.round(5).tolist(), outer_ABR=[float(x), float(y), float(z)],
                         inner_ABR=[float(x2), float(y2), float(z2)])
                    for a, t, n, u, x, y, z, x2, y2, z2 in zip(s, T, N, U, A, B, R, Ai, Bi, Ri)],
        shelf=dict(plane_z=m["ztop"], center_xyz=shelf_center, frame=pf,
                   s_range=[span.s_pad0, span.s_pad1], flat_half_width=pf["n_half"],
                   load_point_LC1=shelf_center),
        tip_xyz=m["tip_xyz"], span_arc3d=m["span_arc3d"],
        anchor=dict(plate_mm=p["anchor_plate"]["size"], holes_yz=m["holes"], hole_d=p["anchor_plate"]["hole_d"],
                    plate_face_x=0.0, plate_back_x=p["anchor_plate"]["size"][2]),
        shell_wall=p["shell_wall"], material=p["material"],
        cut_stations=m["cut_stations"], joints=m["joints"],
        notes=["underlay is the load-bearing monolith (joint bulkhead plugs included, bolts/keys/sockets NOT modelled in it; "
               "see joints.json + segments)", "centerline arc s is plan-arc; span_arc3d is true 3D length"],
    )


def generate(params_path, out, architecture=None, joint=None, style=None, seed=None, previews=True,
             write_skin=True, quiet=False):
    log = (lambda *a: None) if quiet else (lambda *a: print(*a, flush=True))
    p = json.load(open(params_path))
    t0 = time.time()
    os.makedirs(os.path.join(out, "segments"), exist_ok=True)
    arch = architecture or p["architecture"]
    jt = joint or p["joint"]["type"]
    sk_p = p["skin"]
    st = style or sk_p["style"]
    sd = seed if seed is not None else sk_p["seed"]

    res = build_underlay(p, architecture=arch, joint_type=jt)
    under = res["underlay"]
    u_mesh = clean_mesh(to_trimesh(under))
    u_mesh.export(os.path.join(out, "underlay.stl"))
    log(f"underlay {arch}/{jt}: {len(u_mesh.faces)} tris, vol {under.volume():.0f} mm3, {time.time()-t0:.1f}s")

    env_mesh = to_trimesh(res["envelope"])
    sk_mesh = skin(env_mesh, seed=sd, style=st, keepouts=res["keepouts"], max_proud=sk_p["max_proud"],
                   min_proud=sk_p["min_proud"], edge_len=sk_p["edge_len"], inset=sk_p["inset"])
    sk_man = to_manifold(sk_mesh)
    sk_mesh = clean_mesh(sk_mesh)
    sk_mesh.export(os.path.join(out, "skin.stl"))
    asm = under + sk_man
    asm_mesh = clean_mesh(to_trimesh(asm))
    asm_mesh.export(os.path.join(out, "assembly.stl"))
    log(f"skin {st}: {len(sk_mesh.faces)} tris, vol {sk_man.volume():.0f}; assembly {len(asm_mesh.faces)} tris, {time.time()-t0:.1f}s")

    segs, feats = segment(asm, res["span"], p, jt, p["joint"]["cut_stations"])
    seg_info = []
    bed = p["joint"]["bed_usable"]
    for s in segs:
        tm = clean_mesh(to_trimesh(s["man"]))
        fn = os.path.join(out, "segments", f"seg_{s['index']:02d}.stl")
        tm.export(fn)
        M, ext = print_orientation(tm)
        tp = tm.copy(); tp.apply_transform(M)
        tp.export(os.path.join(out, "segments", f"seg_{s['index']:02d}_print.stl"))
        seg_info.append(dict(index=s["index"], file=f"segments/seg_{s['index']:02d}.stl",
                             print_file=f"segments/seg_{s['index']:02d}_print.stl", s_lo=s["s_lo"], s_hi=s["s_hi"],
                             joint_lo=s["joint_lo"], joint_hi=s["joint_hi"], volume_mm3=float(tm.volume),
                             mass_g_solid=float(tm.volume * RHO[p["material"]]),
                             aabb_extents=(tm.bounds[1] - tm.bounds[0]).round(2).tolist(),
                             print_extents=np.round(ext, 2).tolist(), print_transform=M.round(6).tolist(),
                             fits_bed=bool(np.all(ext <= bed)), watertight=bool(tm.is_watertight),
                             triangles=int(len(tm.faces))))
        log(f"  seg {s['index']}: extents {np.round(ext)} fits={np.all(ext<=bed)} wt={tm.is_watertight}")
    json.dump(dict(bed_usable=bed, joint_type=jt, segments=seg_info), open(os.path.join(out, "segments.json"), "w"), indent=1)
    json.dump(dict(type=jt, bolt_hardware=[f["hardware"] for f in feats],
                   joints=[{**mm, "dims": {k: v for k, v in f["dims"].items() if k in ("n_key", "L", "bhA", "bhB", "clr", "Ai", "Bi", "Ri")}}
                           for mm, f in zip(res["meta"]["joints"], feats)]),
              open(os.path.join(out, "joints.json"), "w"), indent=1)
    man = manifest(res, p)
    man["mass"] = dict(underlay_g=float(under.volume() * RHO[p["material"]]),
                       skin_g_solid=float(sk_man.volume() * RHO[p["material"]]),
                       assembly_g_solid=float(asm.volume() * RHO[p["material"]]),
                       note="solid-density numbers; printed mass lower with infill. skin = non-structural added mass")
    man["hashes"] = dict(underlay=sha(u_mesh), skin=sha(sk_mesh), assembly=sha(asm_mesh))
    man["skin"] = dict(style=st, seed=sd, max_proud=sk_p["max_proud"])
    json.dump(man, open(os.path.join(out, "geometry_manifest.json"), "w"), indent=1)

    if previews:
        pdir = os.path.join(ROOT, "prototype", "p0", "reports", "previews")
        os.makedirs(pdir, exist_ok=True)
        sheet([(u_mesh, PALETTES["underlay"])], os.path.join(pdir, f"underlay_{arch}.png"), title=f"underlay {arch}")
        sheet([(asm_mesh, PALETTES.get(st, PALETTES["assembly"]))], os.path.join(pdir, f"assembly_{st}.png"),
              title=f"assembly: {arch} + skin {st} seed {sd}")
    log(f"done {time.time()-t0:.1f}s -> {out}")
    return dict(res=res, under=under, skin=sk_man, asm=asm, p=p, segs=seg_info, manifest=man)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--params", default=os.path.join(ROOT, "prototype/p0/params.json"))
    ap.add_argument("--out", default=os.path.join(ROOT, "prototype/p0/out"))
    ap.add_argument("--architecture"); ap.add_argument("--joint"); ap.add_argument("--style")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--no-previews", action="store_true")
    ap.add_argument("--skins-all", action="store_true",
                    help="also write skin-only STLs for every style to out/skins/ + skins.json (skin-swap test inputs)")
    ap.add_argument("--variants", action="store_true",
                    help="also write underlay-only variants (all architectures x joint types) to out/variants/")
    a = ap.parse_args()
    generate(a.params, a.out, a.architecture, a.joint, a.style, a.seed, previews=not a.no_previews)
    if a.skins_all:
        p = json.load(open(a.params)); sk_p = p["skin"]
        r = build_underlay(p, architecture=a.architecture, joint_type=a.joint)
        env = to_trimesh(r["envelope"]); sdir = os.path.join(a.out, "skins"); os.makedirs(sdir, exist_ok=True)
        tab = {}
        for st in STYLES:
            sk = skin(env, sk_p["seed"], st, r["keepouts"], sk_p["max_proud"], sk_p["min_proud"], sk_p["edge_len"], sk_p["inset"])
            sk = clean_mesh(sk); sk.export(os.path.join(sdir, f"skin_{st}.stl"))
            added = (r["underlay"] + to_manifold(sk)).volume() - r["underlay"].volume()
            tab[st] = dict(file=f"skins/skin_{st}.stl", skin_volume_mm3=float(sk.volume), added_volume_mm3=float(added),
                           added_mass_g_solid=float(added * RHO[p["material"]]))
            print("skin", st, tab[st]["added_mass_g_solid"], flush=True)
        json.dump(tab, open(os.path.join(a.out, "skins.json"), "w"), indent=1)
    if a.variants:
        p = json.load(open(a.params))
        vdir = os.path.join(a.out, "variants"); os.makedirs(vdir, exist_ok=True)
        for arch in p["architectures_available"]:
            for jt in p["joint"]["types_available"]:
                r = build_underlay(p, architecture=arch, joint_type=jt)
                clean_mesh(to_trimesh(r["underlay"])).export(os.path.join(vdir, f"underlay_{arch}__{jt}.stl"))
                print("variant", arch, jt, f"vol {r['underlay'].volume():.0f}", flush=True)


if __name__ == "__main__":
    main()
