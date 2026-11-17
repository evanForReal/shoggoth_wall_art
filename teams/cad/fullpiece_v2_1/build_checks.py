#!/usr/bin/env python3
"""Merge DIR/<variant>_meta.json into engineering_checks.json (every README number must come from a key here). Usage: build_checks.py DIR"""
import sys, json, os
D = sys.argv[1]; out = {}
for v in ('hero', 'v1_liftedge', 'v2_tentacles5', 'v3_maw_big'):
    p = os.path.join(D, v + '_meta.json')
    if not os.path.exists(p): continue
    m = json.load(open(p))
    out[v] = dict(params=m['params'], engineering=m['engineering'], volume_cm3_solid=m['volume_cm3_solid'], mass_g_PETG_solid_upper_bound=m['mass_g_PETG_solid_upper_bound'],
                  shelves=m['shelves'], strut=m['strut'], mask=m['mask'], maw=m['maw'], eyes=m['eyes'], teeth=m['teeth'],
                  whips=m.get('whips'), arms=m.get('arms'), fingers=m.get('fingers'), membranes=m.get('membranes'))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'engineering_checks.json'), 'w'), indent=1)
print(list(out))
