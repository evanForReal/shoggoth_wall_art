"""Round-08b studies: r07 G1a SKELETON kept (trunk spine, 3 shelf arms with identical roots/paths/shelf positions), changed only:
lower body (hanging root cascade), head top (mask embedded, crown of strands/membrane, no hood), limbs as split/rejoin strand bundles,
organic flow-aligned tear webs, smaller vertical maw, shelves gripped by root fingers. Three densities: a restrained, b medium, c dense lace.
Coordinates mm: x right, y up, z out of wall; envelope +-457."""
import numpy as np
S = {}

# ---------------- r07 G1a skeleton (copied verbatim from composition_r07/studies.py: shelf(), arm(), tail())
def shelf(cx, top, cz=122, a=124, b=122, seed=1): return dict(cx=cx, top=top, cz=cz, a=a, b=b, seed=seed)
def tail(cx, ytop_att, sg=1): return [(cx + sg * 55, ytop_att, 108), (cx + sg * 95, ytop_att - 3, 112), (cx + sg * 113, ytop_att + 14, 112)]
def arm(name, sh, root, r0=52):
    cx, top = sh['cx'], sh['top']; ya = top - 44; sd = 1 if cx > root[0] else -1; ap = (cx - sd * 135, ya)
    p1 = (root[0] + 0.32 * (ap[0] - root[0]), root[1] + (ya - root[1]) * 0.15); p2 = (root[0] + 0.68 * (ap[0] - root[0]), root[1] + (ya - root[1]) * 0.75)
    return dict(name=name, R0=r0, shelf=sh, root=root, ap=ap, sd=sd, ya=ya, limb=True,
                pts=[(root[0], root[1], 35), (p1[0], p1[1], 55), (p2[0], p2[1], 75), (ap[0], ap[1], 90), (cx, ya, 100)] + tail(cx, ya, sd))
ARMS = lambda: (arm('S1_UL', shelf(-335, 285), (-105, 150)), arm('S2_UR', shelf(335, 150, seed=2), (70, 60)), arm('S3_LL', shelf(-335, -190, seed=3), (-70, -100)))
MASK = dict(c=(8, 262), D=200, z=88, dz=28)
MAW = dict(c=(0, -20), w=166, h=290, tilt=0.0)
# trunk spine = r07 G1a spine, radii as r07 (head 138->128, ends earlier: the cascade replaces the pelvis column)
SPINE = [(8, 262, 48, 112), (3, 150, 18, 166), (-3, 20, 12, 178), (0, -110, 10, 150), (-4, -190, 8, 100), (-8, -245, 8, 46)]
R07_HALF = lambda y: float(np.interp(y, [-250, -110, 20, 150, 262], [100, 156, 184, 172, 138]))   # r07 G1a trunk half-width
XC = lambda y: float(np.interp(y, [-250, -110, 20, 150, 262], [2, 0, -3, 3, 8]))

def curl_end(pts, turn, rad=26, n=5, sgn=1):
    """append a spiral hook (in-plane curl) after the last point; turn in radians swept."""
    p = np.array(pts, float); d = p[-1, :2] - p[-2, :2]; d /= np.linalg.norm(d); a0 = np.arctan2(d[1], d[0]); out = list(map(tuple, p))
    c = p[-1, :2] + sgn * rad * np.array([-d[1], d[0]]); ph0 = np.arctan2(p[-1, 1] - c[1], p[-1, 0] - c[0])
    for i in range(1, n + 1):
        u = i / n; ph = ph0 + sgn * turn * u; r_ = rad * (1 - 0.45 * u)
        out.append((c[0] + r_ * np.cos(ph), c[1] + r_ * np.sin(ph), p[-1, 2] + 6 * u))
    return out

# ---------------- hanging cascade: up to 9 strands, asymmetric, none paired. Outer reach follows r07 G1a's lower envelope; strands differ in thickness, length, curl.
def hangers():
    H = {}
    H['H1'] = dict(pts=[(-40, -228, 24), (-105, -300, 30), (-190, -352, 36), (-285, -392, 42), (-365, -425, 46), (-418, -444, 48)], R0=54, n=3, curl=dict(turn=2.7, rad=20, sgn=1), seed=0.6)      # long trailing, hooked tip
    H['H7'] = dict(pts=[(-75, -160, 22), (-150, -210, 30), (-235, -262, 38), (-312, -318, 44), (-352, -378, 48)], R0=24, n=1, seed=1.1)                                                     # thin, shorter, parallel above H1
    H['H2'] = dict(pts=[(-44, -205, 24), (-70, -285, 30), (-84, -365, 38), (-70, -444, 44)], R0=30, n=2, seed=1.6)
    H['H3'] = dict(pts=[(-6, -226, 26), (-16, -292, 34), (-6, -352, 42)], R0=36, n=1, curl=dict(turn=3.2, rad=16, sgn=-1), seed=0.9)                                                       # short heavy, spiral tip
    H['H8'] = dict(pts=[(-26, -240, 22), (6, -318, 30), (34, -380, 38), (22, -446, 42)], R0=17, n=1, seed=0.2)
    H['H4'] = dict(pts=[(20, -210, 24), (60, -300, 32), (120, -372, 40), (205, -418, 46), (300, -442, 50), (372, -452, 52)], R0=50, n=2, curl=dict(turn=2.4, rad=14, sgn=1), seed=2.0)           # trails along the bottom edge (r07 T3 band)
    H['H6'] = dict(pts=[(54, -196, 24), (96, -262, 32), (120, -336, 40), (112, -400, 46)], R0=26, n=2, seed=0.4)
    H['H5'] = dict(pts=[(80, -118, 28), (178, -150, 38), (282, -176, 48), (372, -222, 56), (425, -292, 58), (428, -368, 58), (402, -428, 58)], R0=64, n=4, curl=dict(turn=2.8, rad=18, sgn=-1), seed=1.4)  # heavy sweeping trail, hooked end (r07 T2 band)
    H['H9'] = dict(pts=[(106, -150, 22), (214, -190, 30), (306, -246, 38), (352, -318, 44)], R0=20, n=1, seed=1.9)
    return H
HSEL = {'a': ['H1', 'H2', 'H3', 'H4', 'H5', 'H6'], 'b': ['H1', 'H7', 'H2', 'H3', 'H4', 'H5', 'H6', 'H8'], 'c': ['H1', 'H7', 'H2', 'H3', 'H8', 'H4', 'H5', 'H6', 'H9']}

# ---------------- crown: root strands fanning out from behind the mask (rising and spreading), cobweb veil between their tips (concave scalloped free edge)
def crown(n, seed, rmin=14, rmax=26):
    rng = np.random.default_rng(seed); cx, cy = MASK['c']; out = []
    ths = np.sort(np.linspace(-24, 204, n) + rng.uniform(-7, 7, n))
    for i, th in enumerate(ths):
        th_r = np.radians(th); top = max(0.0, np.sin(th_r)); r1 = 124 + 28 * top ** 0.7 + rng.uniform(-6, 14); drift = np.radians(rng.uniform(14, 42)); pts = []
        for u in (0.0, 0.35, 0.7, 1.0):
            r_ = 100 + (r1 - 100) * u; a_ = th_r + drift * u ** 1.3; pts.append((cx + r_ * np.cos(a_), cy + r_ * np.sin(a_), 78 - 22 * u + 7 * (i % 3)))
        out.append(dict(name=f'C{i}', pts=pts, R0=float(rng.uniform(rmin, rmax)) * (0.85 + 0.35 * top), n=1, seed=float(rng.uniform(0, 6)), th=float(th), p=0.5, r_tip=7.0))
    return out
def crown_veil(cr, seed, sag=14):
    rng = np.random.default_rng(seed); cx, cy = MASK['c']; ordc = sorted(cr, key=lambda c: c['th'])
    poly = [tuple(p[:2]) for p in ordc[0]['pts']]
    for A, B in zip(ordc[:-1], ordc[1:]):
        poly += scallop(A['pts'][-1][:2], B['pts'][-1][:2], (cx, cy), sag, 1, rng)
    poly += [tuple(p[:2]) for p in ordc[-1]['pts'][::-1]]
    a0, a1 = np.radians(ordc[-1]['th']), np.radians(ordc[0]['th']); poly += [(cx + 96 * np.cos(a), cy + 96 * np.sin(a)) for a in np.linspace(a0, a1, 12)]
    return dict(poly=poly, anchors=[[(p[0], p[1], p[2] - 6) for p in c['pts']] for c in cr])
def meridians(n_side, seed):
    """long surface strands flowing down the trunk, bending around the maw, into the cascade. returns xy polylines."""
    rng = np.random.default_rng(seed); out = []; ys = np.linspace(168, -185, 14); mh = lambda y: (MAW['w'] / 2 * np.sin(np.pi * np.clip((y - (MAW['c'][1] - MAW['h'] / 2)) / MAW['h'], 0, 1) ** 0.82) ** 0.75 + 24) if (MAW['c'][1] - MAW['h'] / 2 - 10 < y < MAW['c'][1] + MAW['h'] / 2 + 10) else 0.0
    for sd in (-1, 1):
        for j in range(n_side):
            f = (j + 0.55 + rng.uniform(-0.2, 0.2)) / (n_side + 0.3); ph = rng.uniform(0, 6.28); ln = rng.uniform(0.72, 1.0); y0 = 168 - rng.uniform(0, 40)
            pts = []
            for y in ys:
                if y > y0 or y < -185 * ln: continue
                W = R07_HALF(y) - 44; m = mh(y); pts.append((XC(y) + sd * (m + f * (W - m)) + 6 * np.sin(y / 55 + ph), y))
            if len(pts) >= 4: out.append(pts)
    return out
def trunk_band(sd, y_hi, y_lo):
    mh = lambda y: (MAW['w'] / 2 * np.sin(np.pi * np.clip((y - (MAW['c'][1] - MAW['h'] / 2)) / MAW['h'], 0, 1) ** 0.82) ** 0.75 + 30) if (MAW['c'][1] - MAW['h'] / 2 - 10 < y < MAW['c'][1] + MAW['h'] / 2 + 10) else 30.0
    ys = np.linspace(y_hi, y_lo, 12); inn = [(XC(y) + sd * (mh(y) - 12), y) for y in ys]; out = [(XC(y) + sd * (R07_HALF(y) - 10), y) for y in ys]
    return dict(poly=inn + out[::-1], anchors=[[(p[0], p[1], 40) for p in inn], [(p[0], p[1], 40) for p in out]])
def flank_web(sd, y_hi, y_lo, seed, inset=62, cusps=3):
    rng = np.random.default_rng(seed); ys = np.linspace(y_hi, y_lo, 9); inner = [(XC(y) + sd * (R07_HALF(y) - inset), y) for y in ys]
    o0 = (XC(y_lo) + sd * (R07_HALF(y_lo) - 6), y_lo); o1 = (XC(y_hi) + sd * (R07_HALF(y_hi) - 6), y_hi)
    edge = scallop(o1, o0, (XC(0), (y_hi + y_lo) / 2), 9, cusps, rng)
    poly = inner + edge
    return dict(poly=poly, anchors=[[(p[0], p[1], 42) for p in inner], [(XC(y) + sd * (R07_HALF(y) - 8), y, 33) for y in ys]])

# ---------------- web polygon helpers
def scallop(p0, p1, ref, depth, cusps, rng):
    """free edge from p0 to p1: `cusps` concave arcs bowed toward `ref` (strand tips = cusps)."""
    p0 = np.array(p0, float); p1 = np.array(p1, float); ref = np.array(ref, float); out = []
    ts = np.sort(np.r_[0, rng.uniform(0.15, 0.85, max(cusps - 1, 0)), 1])
    for a, b in zip(ts[:-1], ts[1:]):
        for u in np.linspace(0, 1, 6)[:-1]:
            t_ = a + (b - a) * u; pt = p0 + (p1 - p0) * t_; dv = ref - pt; dv /= np.linalg.norm(dv) + 1e-9
            out.append(tuple(pt + dv * depth * np.sin(np.pi * u) ** 0.8 * (b - a) * 2.2))
    out.append(tuple(p1)); return out
def sheet(A, B, i0, i1, j0, j1, bite=0.0, cusps=2, seed=0, ref=None, depth=18):
    """polygon between strand paths A[i0:i1] and B[j0:j1] (xy), free end edge scalloped toward the root."""
    rng = np.random.default_rng(seed); a = [tuple(p) for p in A[i0:i1]]; b = [tuple(p) for p in B[j0:j1]]
    ref = ref if ref is not None else ((a[0][0] + b[0][0]) / 2, (a[0][1] + b[0][1]) / 2)
    edge = scallop(a[-1][:2], b[-1][:2], ref, depth, cusps, rng)
    return dict(poly=[p[:2] for p in a] + edge + [p[:2] for p in b[::-1]], anchors=[a, b])
def under_arm(a, drop=30, e_drop=150, seed=0, depth=22, cusps=3, ext=0):
    (rx, ry), (ax, ay), sd = a['root'], a['ap'], a['sd']; p1 = a['pts'][1]; rng = np.random.default_rng(seed)
    O = (ax + sd * 50, ay - drop - 4); E = (sd * (176 + ext), ry - e_drop); T0 = (sd * 150, ry + 10)
    edge = scallop(O, E, ((O[0] + E[0]) / 2 - sd * 60, (O[1] + E[1]) / 2 + 60), depth, cusps, rng)
    poly = [T0, (p1[0], p1[1] - 14), (ax, ay - drop), O] + edge + [(sd * 140, ry - e_drop + 30), (sd * 140, ry - 20)]
    anch = [[(p1[0], p1[1] - 10, 45), (ax, ay - 12, 82), (O[0], O[1] + 8, 92)], [(E[0], E[1], 55), ((O[0] + E[0]) / 2 - sd * 30, (O[1] + E[1]) / 2 + 10, 72), (O[0], O[1] + 8, 92)]]
    return dict(poly=poly, anchors=anch)

DENS = {'a': dict(n_arm=4, crown_n=6, crown_r=(15, 24), hole=0.34, hlen=80, asp=0.20, nodes=2, wings=(0.9, 1.0), band=0.0, ext=34, seed=11),
        'b': dict(n_arm=5, crown_n=9, crown_r=(15, 26), hole=0.30, hlen=70, asp=0.22, nodes=3, wings=(1.15, 1.2), band=0.16, ext=56, seed=12),
        'c': dict(n_arm=7, crown_n=13, crown_r=(15, 27), hole=0.24, hlen=58, asp=0.24, nodes=4, wings=(1.15, 1.2), band=0.14, ext=52, seed=13)}

def make(d):
    P = DENS[d]; rng = np.random.default_rng(P['seed']); a1, a2, a3 = ARMS(); arms = [a1, a2, a3]
    for q, a in enumerate(arms): a.update(n=P['n_arm'], nodes=P['nodes'], seed=0.4 + 1.3 * q)
    Hs = hangers(); hang = []
    for nm in HSEL[d]:
        h = dict(Hs[nm]); pts = h['pts']; 
        if 'curl' in h: c_ = h.pop('curl'); pts = curl_end(pts, c_['turn'], c_['rad'], 6, c_['sgn'])
        hang.append(dict(name=nm, pts=pts, R0=h['R0'], n=h['n'], seed=h['seed'], nodes=2, limb=True, hang=True, p=0.7))
    cr = crown(P['crown_n'], 5 + ord(d), *P['crown_r'])
    for c_ in cr: c_.update(nodes=2, crown=True, p=0.75)
    byname = {h['name']: h for h in hang}; webs = []; W = lambda **k: dict(holes=P['hole'], hlen=P['hlen'] * 1.3, asp=P['asp'] * 1.15, th=10.0, rim=11.0, **k)
    # arm wings (arm to trunk): size scaled by density
    for i, a in enumerate((a1, a2)):
        w = under_arm(a, seed=i + 1, e_drop=((150 if a is a1 else 250) + 40) * P['wings'][0], drop=30, ext=(min(P['ext'], 34) if a is a1 else P['ext'])); webs.append(W(seed=20 + i, **w))
    w = under_arm(a3, seed=3, e_drop=70 * P['wings'][1], drop=34, ext=P['ext']); webs.append(W(seed=22, **w))
    if P['band'] > 0:      # membrane inside the arm bundles (between the split strands): fills the gaps, tears along the arm
        for i, a in enumerate(arms):
            from engine import curve as _cv, tent_r as _tr
            c_, t_, _ = _cv(a['pts'], 3.0); R_ = _tr(t_, a['R0'], 6.0, 0.75); sel = (t_ > 0.10) & (t_ < 0.52); cc = c_[sel][::4]; RR = R_[sel][::4] * 0.92
            tg = np.gradient(cc[:, :2], axis=0); tg /= np.linalg.norm(tg, axis=1)[:, None]; nr = np.stack([-tg[:, 1], tg[:, 0]], 1)
            Lp = cc[:, :2] + nr * RR[:, None]; Rp = cc[:, :2] - nr * RR[:, None]
            webs.append(dict(poly=[tuple(p) for p in Lp] + [tuple(p) for p in Rp[::-1]], anchors=[[(p[0], p[1], p[2] - 6) for p in cc]], holes=P['band'], hlen=60, asp=0.18, th=7.0, rim=7.0, seed=60 + i))
    # cascade curtains
    def hw(n1, n2, i0, i1, j0, j1, seed, cusps=2, depth=20):
        A, B = byname[n1]['pts'], byname[n2]['pts']; w = sheet(A, B, i0, i1, j0, j1, seed=seed, cusps=cusps, depth=depth, ref=(0, -120)); webs.append(W(seed=30 + seed, **w))
    pairs = {'a': [('H1', 'H2', 0, 3, 0, 3), ('H4', 'H6', 0, 3, 0, 3)],
             'b': [('H1', 'H7', 0, 4, 0, 3), ('H2', 'H3', 0, 4, 0, 3), ('H3', 'H8', 0, 3, 0, 4), ('H4', 'H6', 0, 4, 0, 4)],
             'c': [('H1', 'H7', 0, 5, 0, 4), ('H1', 'H2', 0, 4, 0, 4), ('H2', 'H3', 0, 4, 0, 3), ('H3', 'H8', 0, 3, 0, 4), ('H8', 'H4', 0, 4, 0, 4), ('H4', 'H6', 0, 4, 0, 4), ('H5', 'H9', 0, 3, 0, 3)]}
    for i, pr in enumerate(pairs[d]): hw(*pr, seed=i + 1, cusps=2 + (i % 2))
    # crown membranes between neighbouring crown strands
    if d != 'a': webs.append(W(seed=50, **crown_veil(cr, 3, sag=12 if d == 'b' else 16)))
    else: webs.append(W(seed=50, **crown_veil(cr[1:4], 3, sag=10)))
    tears = []
    ty = {'a': (110, -70), 'b': (125, -95), 'c': (140, -120)}[d]; th_ = {'a': 0.12, 'b': 0.17, 'c': 0.22}[d]
    for i, sd in enumerate((-1, 1)): tears.append(dict(seed=80 + i, holes=th_, hlen=110, asp=0.26, rim=13.0, minlig=14.0, **trunk_band(sd, ty[0], ty[1])))
    ribs = []
    mw = MAW
    hair = meridians({'a': 1, 'b': 2, 'c': 3}[d], 9 + ord(d))
    hair += [[(-98, 205), (-112, 168), (-98, 140), (-70, 116)], [(104, 208), (118, 170), (96, 142), (66, 118)]] + ([[(-122, 222), (-150, 180), (-150, 130)], [(130, 226), (152, 184), (150, 132)]] if d != 'a' else [])
    return dict(id=f'G1a_{d}', name=f'G1a-r08b ({d}): r07 skeleton, hanging cascade, embedded mask + root crown, strand bundles, tear webs', gesture='G1 vertical trunk (r07 G1a skeleton)', seed=P['seed'], spine4=SPINE,
                mask=MASK, maw=MAW, items=arms + hang + cr, webs=webs, tears=tears, hair=hair, dens=d)
for d in 'abc': S[f'G1a_{d}'] = make(d)
STUDIES = S
