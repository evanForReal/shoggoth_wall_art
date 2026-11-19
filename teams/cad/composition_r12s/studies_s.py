"""r12s specs: H + ball (S1-S3) on the r11 H build, and r12 concepts C1..C10 with a ball mask. Ball sizing = measured against relief <= 300 (README)."""
import numpy as np, importlib
BALLS = {   # D (mm, equatorial), depth/D ratio (front-back axis / D), gap = lowest back point of the ball above the flesh peak under it (mm)
 'S1': dict(D=120.0, ratio=1.0, gap=60.0), 'S2': dict(D=180.0, ratio=0.60, gap=66.0), 'S3': dict(D=200.0, ratio=0.45, gap=80.0)}
def ball_held(base, name, grip=None, **over):
    b = BALLS[name]; a = b['D'] / 2; s = a / 100.0; h = dict(base)
    bu, bv = h.get('boss', (0.0, -36.0)); h.update(shape='ball', D=b['D'], ratio=b['ratio'], dz=b['ratio'] * a, rim=0.0, gap=over.pop('gap', b['gap']), boss=(bu * s, bv * s), pad_inset=14.0, seat_max_deg=35.0, ball=name)
    if grip: h['grip'] = grip
    h['boss_search'] = over.pop('boss_search', False)
    h.update(over); return h
def h_ball(name):
    r11 = importlib.import_module('studies_r11'); S = dict(r11.S['H']); S['id'] = name; S['name'] = 'H + ' + name
    S['held'] = ball_held(dict(c=(-32.0, 248.0), roll=15.0, pitch=0.0, yaw=0.0, boss=(0.0, -36.0), root_pref=(0.0, 168.0), root_r=48, grip='F', clear_margin=7.0, clear_start=45), name)
    return S
def concept(cid, name):
    r12 = importlib.import_module('studies_r12'); S = r12.compose(cid); S['id'] = f'{cid}_{name}'; h0 = S['held']; gr = {'F': 'F', 'C': 'C', 'E': 'E'}[h0['grip']]
    S['held'] = ball_held(h0, name, grip=gr, gap=(BALLS[name]['gap']), boss_search=True, root_r=max(h0.get('root_r', 55), 70), clear_margin=7.0, clear_start=45)
    return S
def get(sid):
    if sid in BALLS: return h_ball(sid)
    cid, name = sid.split('_'); return concept(cid, name)
