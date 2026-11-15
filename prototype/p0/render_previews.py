#!/usr/bin/env python3
"""Preview PNGs to prototype/p0/reports/previews/: all skin styles, architecture cutaways, joint closeups.
    python prototype/p0/render_previews.py"""
import json, os, sys
import numpy as np
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from model.structural.underlay import build_underlay
from model.aesthetic.skin import skin, STYLES
from model.aesthetic.render import sheet, PALETTES
from model.mtools import to_trimesh, clean_mesh, to_manifold, box

P = os.path.join(ROOT, "prototype/p0")
p = json.load(open(os.path.join(P, "params.json")))
D = os.path.join(P, "reports/previews"); os.makedirs(D, exist_ok=True)
res = None
for arch in p["architectures_available"]:
    r = build_underlay(p, architecture=arch)
    res = res or r
    u = r["underlay"]
    cut = u ^ box((200, 0, -150 + 28), (900, 900, 300))   # keep z <= 28: horizontal section through the span
    sheet([(clean_mesh(to_trimesh(cut)), PALETTES["underlay"])], os.path.join(D, f"section_{arch}.png"),
          views=("top", "iso"), title=f"underlay {arch}, cut at z=28 (inside view)")
env = to_trimesh(res["envelope"])
for st in STYLES:
    sk = skin(env, p["skin"]["seed"], st, res["keepouts"], p["skin"]["max_proud"], p["skin"]["min_proud"],
              p["skin"]["edge_len"], p["skin"]["inset"])
    sheet([(sk, PALETTES[st])], os.path.join(D, f"skin_{st}.png"), views=("iso", "top"), title=f"skin style {st} (seed {p['skin']['seed']})")
    print("rendered", st, flush=True)
