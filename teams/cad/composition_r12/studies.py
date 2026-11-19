"""Round-12 concepts C1-C10 (composition_r12). One compose() builds every concept from a spec dict (the variation table, variation_table.csv).
Skeleton / arms / webs / hangers / E2 / teeth code is r11 (= r10 A0 family) via studies_base.py. Axis codes: see README.
Coordinates mm: x right, y up, z out of the wall; envelope +-457."""
import csv, os
import numpy as np
from studies_base import *
from engine import curve, tent_r, maw_sd

AXES = ['holder', 'pose', 'grip', 'patch', 'mouth', 'whip', 'massive', 'cascade', 'lean']
TABLE = {   # concept -> axis values (see variation_table.csv for the long names)
 'C1': 'B F F M B L LL S U', 'C2': 'L T C T F R UR T R', 'C3': 'R S E A L U ML A L', 'C4': 'O P F M X E LL T U', 'C5': 'L W C A B U LL S R',
 'C6': 'B T E T L R ML A R', 'C7': 'R W F T X L UR T L', 'C8': 'O F C A F E ML S R', 'C9': 'B S F A B R LL A L', 'C10': 'R P E M L U UR T R'}
PATTERNS = {   # massive limb takes: shelf arms (name, shelf (cx, top), root on the trunk, R0 mm radius at root: 50 = 100 mm dia massive, 30 = 60 mm, 15 = 30 mm)
 'LL': dict(arms=[('S1_UL', (-335, 285), (-105, 150), 15.0), ('S2_UR', (335, 150), (70, 60), 30.0), ('S3_LL', (-335, -190), (-70, -100), 50.0)], right_top=150),
 'UR': dict(arms=[('S1_UL', (-335, 150), (-105, 150), 30.0), ('S2_UR', (335, 300), (85, 110), 50.0), ('S3_LL', (-335, -190), (-70, -100), 15.0)], right_top=300),
 'ML': dict(arms=[('S1_UL', (-335, 330), (-105, 150), 15.0), ('S2_UR', (335, 170), (70, 60), 30.0), ('S3_LL', (-340, -50), (-105, -20), 50.0)], right_top=170)}
LEAN_AMP = {'U': 0.0, 'L': -60.0, 'R': 60.0}      # top of the trunk shifts by this many mm (about 10 deg at the head)
bend = lambda amp, x, y: x + amp * float(np.clip((y + 245) / 507.0, 0, 1.15)) ** 1.5
def bend_slope(amp, y): return amp * 1.5 * float(np.clip((y + 245) / 507.0, 0.001, 1.15)) ** 0.5 / 507.0

def write_table(path):
    names = {'holder': {'B': 'from below', 'L': 'from left', 'R': 'from right', 'O': 'arching over the head'}, 'pose': {'F': 'facing', 'T': 'turned 33 deg away', 'S': 'strongly tilted 32 deg', 'W': 'held low beside the maw', 'P': 'partly lowered (taken off)'},
             'grip': {'F': 'rim fingers', 'C': 'tentacle coil', 'E': 'threaded through eye hole'}, 'patch': {'M': 'behind mask only', 'T': 'trail down trunk', 'A': 'also on holding tentacle'},
             'mouth': {'F': 'fangs', 'L': 'lamprey', 'B': 'both', 'X': 'larger maw 1.3x + fangs'}, 'whip': {'R': 'right curling down', 'L': 'left rising', 'U': 'curling under a shelf', 'E': 'to the envelope edge'},
             'massive': {'LL': 'lower-left', 'UR': 'upper-right', 'ML': 'mid-left'}, 'cascade': {'T': 'long trailing', 'S': 'short dense', 'A': 'asymmetric'}, 'lean': {'U': 'upright', 'L': 'leaning left', 'R': 'leaning right'}}
    with open(path, 'w', newline='') as fh:
        w = csv.writer(fh); w.writerow(['concept'] + AXES + [a + '_name' for a in AXES])
        for k, v in TABLE.items():
            vals = v.split(); w.writerow([k] + vals + [names[a][x] for a, x in zip(AXES, vals)])

# ---------------------------------------------------------------- pieces
def maw_for(code, amp):
    m = dict(MAW)
    if code == 'X': m.update(c=(10, 5), w=195, h=400)
    m['c'] = (m['c'][0] + bend(amp, 0, m['c'][1]), m['c'][1]); m['tilt'] = m['tilt'] - bend_slope(amp, m['c'][1])
    return m

def skeleton(amp, maw, pat, maw_code):
    sp = [(bend(amp, x, y), y, z, r) for x, y, z, r in SPINE]
    P = PATTERNS[pat]; arms = []; shift = {'X': 28.0}.get(maw_code, 0.0)
    for q, (nm, (cx, top), root, r0) in enumerate(P['arms']):
        rx = root[0] + (np.sign(root[0]) * shift if root[0] != 0 else 0); rx = bend(amp, rx, root[1]); a = arm(nm, shelf(cx, top, seed=q + 1), (rx, root[1])); a['R0w'] = r0; arms.append(a)
    if amp == 0.0: xc, half = XC, R07_HALF
    else: xc, half, _ = flank_fns(sp)
    return dict(spine=sp, maw=maw, xc=xc, half=half, arms=arms, H=hangers(), wings=[(235, 0.46, 45), (255, 0.62, 50), (150, 0.46, 40)], right_top=P['right_top'])

def cascade_set(Hs, code, sgn):
    Hs = {k: dict(v) for k, v in Hs.items()}; hsel = ['H1', 'H7', 'H2', 'H3', 'H8', 'H4', 'H5', 'H6', 'H9']; pairs = list(DENS['D2']['pairs'])
    if code == 'S':      # short dense: every strand scaled to 0.62 about its root, thicker, three extra stubby strands
        for k, h in Hs.items():
            p0 = np.array(h['pts'][0][:2]); h['pts'] = [(p0[0] + 0.62 * (x - p0[0]), p0[1] + 0.62 * (y - p0[1]), z) for x, y, z in h['pts']]; h['R0'] *= 1.10
            if 'curl' in h: h['curl'] = dict(h['curl'], rad=h['curl']['rad'] * 0.8)
        Hs['H10'] = dict(pts=[(-20, -215, 24), (-48, -262, 30), (-62, -322, 36)], R0=30, n=2, seed=0.3); Hs['H11'] = dict(pts=[(30, -215, 24), (58, -268, 30), (84, -326, 36)], R0=28, n=2, seed=0.8)
        Hs['H12'] = dict(pts=[(8, -232, 24), (14, -292, 30), (2, -348, 36)], R0=32, n=2, seed=1.2); hsel += ['H10', 'H11', 'H12']; pairs += [('H10', 'H2', 3, 3), ('H11', 'H6', 3, 3), ('H12', 'H3', 3, 3), ('H10', 'H12', 3, 3), ('H12', 'H11', 3, 3)]
    if code == 'A':      # asymmetric: lower parts of every strand swept to one side (sgn +1 right, -1 left), the strands of the other side thinned out
        for k, h in Hs.items():
            h['pts'] = [(x + sgn * 0.55 * max(-200 - y, 0), y, z) for x, y, z in h['pts']]
        drop = ['H7', 'H2'] if sgn > 0 else ['H9', 'H6']; hsel = [h for h in hsel if h not in drop]
    return Hs, hsel, pairs

def whip_path(code, sk, arms):
    Tr = sk['right_top']; d = Tr - 150
    if code == 'R': base = [(262, 104, 100), (330, 96, 104), (398, 86, 108), (436, 60, 104), (444, 14, 98), (432, -38, 92), (402, -82, 88), (360, -104, 86), (322, -92, 88), (304, -64, 92), (318, -40, 96), (338, -44, 100)]; return [(x, y + d, z) for x, y, z in base], 19.0
    if code == 'U': return [(262, Tr - 46, 100), (285, Tr - 85, 98), (320, Tr - 112, 96), (365, Tr - 125, 94), (410, Tr - 120, 92), (432, Tr - 148, 90), (420, Tr - 178, 90), (388, Tr - 186, 90), (366, Tr - 166, 92), (380, Tr - 146, 94), (402, Tr - 152, 96)], 19.0
    if code == 'E': return [(262, Tr - 46, 100), (340, Tr - 62, 100), (412, Tr - 92, 98), (446, Tr - 160, 94), (452, -60, 90), (450, -220, 88), (440, -380, 86), (410, -438, 84), (340, -450, 84), (250, -446, 84), (170, -434, 86), (126, -410, 90), (122, -386, 92), (142, -372, 94)], 21.0
    if code == 'L':
        a = [x for x in arms if x['name'] == 'S1_UL'][0]; c, t, _ = curve(a['pts'], 3.0); i = int(np.argmin(abs(t - 0.35))); x0, y0, z0 = c[i]; top = min(y0 + 245, 436)
        pts = [(x0, y0, z0 - 10), (x0 - 8, y0 + 62, 74), (x0 - 24, y0 + 124, 78), (x0 - 40, (y0 + top) / 2 + 20, 80), (x0 - 52, top, 78)]
        return curl_end(pts, 2.6, 16, 5, -1), 14.0
def build_whip(code, sk, arms):
    pts, R0 = whip_path(code, sk, arms); return dict(name='W_whip', pts=pts, R0=R0, p=0.5, r_tip=5.0, smooth=True, limb=True, whip=True, k=12.0)

def pose_spec(pc, holder, pose, amp, maw):
    """mask frame + boss + root preference for one concept. pc = patch centre (bent)."""
    side = {'L': -1, 'R': 1}.get(holder, 0); H = dict(D=200.0, dz=17.0, rim=8.0, gap=85.0)
    boss = {'B': (0.0, -36.0), 'L': (-38.0, -8.0), 'R': (38.0, -8.0), 'O': (0.0, 38.0)}[holder]
    yaw = pitch = roll = 0.0; c = np.array(pc, float)
    if pose == 'F': c = c + np.array([-24 * (1 if side <= 0 else -1) * 0.6, -8]); roll = 8.0 * (1 if side <= 0 else -1)
    elif pose == 'T': c = c + np.array([-30 * (1 if side <= 0 else -1) * 0.6, -14]); yaw = 33.0 * (1 if side <= 0 else -1)
    elif pose == 'S': c = c + np.array([-30 * (1 if side <= 0 else -1) * 0.6, -20]); roll = 22.0 * (1 if side <= 0 else -1); pitch = 24.0
    elif pose == 'P': c = c + np.array([4.0, -100.0]); roll = 8.0 * (1 if side <= 0 else -1); pitch = 14.0
    elif pose == 'W': sx = side if side != 0 else -1; c = np.array([sx * 125.0, 55.0]); roll = 10.0 * sx
    H.update(c=tuple(c), yaw=yaw, pitch=pitch, roll=roll, boss=boss)
    px, py = c
    H['root_pref'] = {'B': (px + 30, py - 85), 'L': (px - 78, py - 30), 'R': (px + 78, py - 30), 'O': (px + 12, py + 78)}[holder]; H['root_r'] = 55
    if pose == 'W': H['boss'] = (0.0, 40.0); H['root_pref'] = (bend(amp, sx * 62.0, 205.0), 205.0); H['root_r'] = 50
    return H

def compose(cid):
    ho, po, gr, pa, mo, wh, ma, ca, le = TABLE[cid].split(); amp = LEAN_AMP[le]
    maw = maw_for(mo, amp); sk = skeleton(amp, maw, ma, mo); arms = sk['arms']
    PC = (bend(amp, 8.0, 262.0), 262.0)
    H = pose_spec(PC, ho, po, amp, maw); H['grip'] = gr
    pcen = PC if po != 'W' else tuple(np.array(H['c']) + np.array([40 if H['c'][0] < 0 else -40, 5]))
    for a in arms: a.update(n=1, smooth=True, R0=a['R0w'], p=0.6, r_tip=6.0, seed=0.4 + 1.3 * arms.index(a), nodes=NODES)
    for a in arms:
        if a['R0w'] >= 30.0: a['eyerow'] = 9 if a['R0w'] >= 50 else 7
    sgn = {'U': 1, 'L': 1, 'R': -1}[le]; Hs, hsel, pairs = cascade_set(sk['H'], ca, sgn)
    if wh == 'E': hsel = [h for h in hsel if h not in ('H5', 'H9')]
    hang = []
    for nm in hsel:
        h = dict(Hs[nm]); pts = h['pts']
        if 'curl' in h: c_ = h.pop('curl'); pts = curl_end(pts, c_['turn'], c_['rad'], 6, c_['sgn'])
        hang.append(dict(name=nm, pts=pts, R0=h['R0'], n=h['n'], seed=h['seed'], nodes=2, limb=True, hang=True, p=0.7, raw=Hs[nm]['pts']))
    byname = {h['name']: h for h in hang}; P = DENS['D2']; webs = []; Wf = lambda **k: dict(holes=P['hole'], hlen=P['hlen'], asp=P['asp'], th=9.0, rim=10.0, **k); drips = []
    for k_, (a_, (ed, kf, dx)) in enumerate(zip(arms, sk['wings'])):
        w_, dr_ = wing(a_, ed * 1.0, sk['xc'], sk['half'], kfar=kf, drip_dx=dx, name=f'D{k_}'); webs.append(Wf(seed=20 + k_, **w_)); drips.append(dr_)
    for i, (n1, n2, k1, k2) in enumerate(pairs):
        if n1 not in byname or n2 not in byname: continue
        A_, B_ = byname[n1]['raw'][:k1 + 1], byname[n2]['raw'][:k2 + 1]; webs.append(Wf(seed=30 + i, **sheet(A_, B_, (0, -120), sag=0.30, seed=i)))
    items = arms + hang + [build_whip(wh, sk, arms)] + drips
    E, B = ([], [])
    e2 = (pa in 'MA' and ma != 'ML' and not (po == 'W' and ho == 'L') and not (po == 'W' and ho == 'B'))
    if e2: E, B = eyes_E2(); E = [dict(e, x=bend(amp, e['x'], e['y'])) for e in E]; B = [dict(b, c=(bend(amp, b['c'][0], b['c'][1]), b['c'][1])) for b in B]
    patch = dict(c=tuple(pcen), a=108 if po != 'W' else 96, b=108 if po != 'W' else 96, z=62, h=44, kind=pa, n_eyes=12, sizes=[50, 42, 36, 32, 30, 26, 24, 22, 20, 18, 16, 15], rmax=90.0 if po != 'W' else 84.0)
    if pa == 'T':
        sd_ = 1 if (ho == 'L') else -1       # trail runs down the flank opposite the holder (left unless the holder is on the left)
        patch['trail'] = dict(path=[(bend(amp, sd_ * x, y), y) for x, y in [(88, 215), (106, 168), (118, 118), (124, 62), (122, 6), (114, -48), (104, -100)]], n=11, sizes=[34, 30, 28, 26, 24, 22, 20, 18, 17, 16, 14])
    held = dict(H)
    d = dict(id=cid, name=cid + ' ' + TABLE[cid], gesture='variation ' + TABLE[cid], seed=SEED, spine4=sk['spine'], mask=dict(c=H['c'], D=200.0, z=0, dz=17.0), held=held, patch=patch, maw=maw, items=items, webs=webs, tears=[], dens='D2',
             eyes=E, bulges=B, skel_note='', holder_eyes=(pa == 'A'), lean=le, amp=amp, concept=dict(zip(AXES, TABLE[cid].split())))
    if amp == 0.0: d['hair'] = meridians_A(RIBN, 9 + ord('b'), maw)
    else: d['hair'] = meridians_gen(sk['spine'], maw, RIBN, 9 + ord('b'), PC)
    if mo in 'FX': d['teeth_cfg'] = TEETH_M1
    if mo == 'L': d['lamprey'] = dict(rows=4, inset=(3.0, 11.0, 19.0, 27.0), spacing=(13.0, 12.0, 11.0, 10.0))
    if mo == 'B': d['lamprey'] = dict(rows=4, inset=(3.0, 11.0, 19.0, 27.0), spacing=(13.0, 12.0, 11.0, 10.0)); d['teeth_cfg'] = dict(front=34, back=0, fangs=TEETH_M1['fangs'], fangs_only=True)
    return d

STUDIES = {k: None for k in TABLE}
def get(cid): return compose(cid)
if __name__ == '__main__':
    write_table(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'variation_table.csv')); print(open('variation_table.csv').read()[:600])
