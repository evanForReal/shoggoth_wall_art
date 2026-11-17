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
MASK = dict(c=(8, 262), D=200, z=74, dz=26)
MAW = dict(c=(10, -15), w=150, h=316, tilt=0.05, jag=0.11)
# trunk spine = r07 G1a spine, radii as r07 (head 138->128, ends earlier: the cascade replaces the pelvis column)
SPINE = [(8, 262, 40, 106), (3, 150, 18, 124), (-3, 20, 12, 132), (0, -110, 10, 116), (-4, -190, 8, 88), (-8, -245, 8, 44)]
R07_HALF = lambda y: float(np.interp(y, [-250, -110, 20, 150, 262], [88, 116, 132, 124, 106]))   # r08c trunk half-width (narrower, taller; r07 was 100/156/184/172/138)
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
    H['H4'] = dict(pts=[(20, -210, 24), (60, -300, 32), (120, -372, 40), (200, -418, 46), (276, -440, 50)], R0=36, n=2, seed=2.0)
    H['H6'] = dict(pts=[(54, -196, 24), (96, -262, 32), (120, -336, 40), (112, -400, 46)], R0=26, n=2, seed=0.4)
    H['H5'] = dict(pts=[(80, -118, 28), (178, -150, 38), (282, -176, 48), (372, -222, 56), (425, -292, 58), (428, -368, 58), (402, -428, 58)], R0=46, n=4, curl=dict(turn=2.8, rad=18, sgn=-1), seed=1.4)  # heavy sweeping trail, hooked end (r07 T2 band)
    H['H9'] = dict(pts=[(106, -150, 22), (214, -190, 30), (306, -246, 38), (352, -318, 44)], R0=15, n=1, seed=1.9)
    return H
HSEL = {'a': ['H1', 'H2', 'H3', 'H4', 'H5', 'H6'], 'b': ['H1', 'H7', 'H2', 'H3', 'H4', 'H5', 'H6', 'H8'], 'c': ['H1', 'H7', 'H2', 'H3', 'H8', 'H4', 'H5', 'H6', 'H9']}

# ---------------- crown: THICK tapering root tines fused into the head, rising/arching up and outward (no curls, no twist); sparse short branches
def crown(n, seed, branches):
    """asymmetric spire cluster: thick tines rooted behind/beside the mask in the head, rising vertically with a slight outward lean and a gentle S, different heights."""
    rng = np.random.default_rng(seed); out = []
    # (base x,y), (tip x,y), R0, bow
    T = [((-102, 232), (-176, 362), 29, 12), ((-42, 300), (-66, 452), 29, -10), ((38, 310), (62, 428), 25, 9), ((98, 296), (150, 408), 26, -9), ((116, 228), (190, 322), 22, 8),
         ((-132, 212), (-196, 300), 20, -8), ((70, 330), (116, 440), 18, 7)][:n]
    for i, (b0, t0, R0, bow) in enumerate(T):
        b0 = np.array(b0, float) + rng.uniform(-4, 4, 2); t0 = np.array(t0, float) + rng.uniform(-6, 6, 2); d = t0 - b0; nr = np.array([-d[1], d[0]]) / np.linalg.norm(d)
        p1 = b0 + d * 0.35 + nr * bow; p2 = b0 + d * 0.7 - nr * bow * 0.6
        out.append(dict(name=f'C{i}', pts=[(b0[0], b0[1], 50), (p1[0], p1[1], 80), (p2[0], p2[1], 72), (t0[0], t0[1], 52)], R0=float(R0 * 1.15), n=1, seed=0.0, th=float(i), p=0.8, r_tip=4.6, lump=0.04, nodes=1))
    mains = list(out)
    for j in range(branches):
        base = mains[[1, 3, 0, 2, 4, 1][j % 6]]; P = np.array(base['pts']); sg = 1 if j % 2 == 0 else -1
        q = P[1] + (P[2] - P[1]) * 0.6; dirv = P[3, :2] - P[0, :2]; dirv /= np.linalg.norm(dirv); ang = np.radians(30 + 4 * j) * sg
        d2 = np.array([dirv[0] * np.cos(ang) - dirv[1] * np.sin(ang), dirv[0] * np.sin(ang) + dirv[1] * np.cos(ang)]); L = 46 + 8 * j
        e = q[:2] + d2 * L
        if e[1] > 454 or abs(e[0]) > 200: continue
        m_ = q[:2] + d2 * L * 0.5 + np.array([-d2[1], d2[0]]) * 5 * sg
        out.append(dict(name=f'B{j}', pts=[(q[0], q[1], 76), (m_[0], m_[1], 70), (e[0], e[1], 54)], R0=float(11 + (j % 3)), n=1, seed=0.0, th=base['th'], p=0.9, r_tip=4.6, lump=0.03, nodes=1))
    return out
def meridians(n_side, seed):
    """vertical strand ribbing over the trunk, parallel to the axis, flowing around the maw into the cascade. returns xy polylines."""
    rng = np.random.default_rng(seed); out = []; ys = np.linspace(172, -190, 16)
    mh = lambda y: (MAW['w'] / 2 * np.sin(np.pi * np.clip((y - (MAW['c'][1] - MAW['h'] / 2)) / MAW['h'], 0, 1) ** 0.82) ** 0.75 + 20) if (MAW['c'][1] - MAW['h'] / 2 - 8 < y < MAW['c'][1] + MAW['h'] / 2 + 8) else 0.0
    for sd in (-1, 1):
        for j in range(n_side):
            f = (j + 0.5 + rng.uniform(-0.15, 0.15)) / n_side; ph = rng.uniform(0, 6.28); y0 = 172 - rng.uniform(0, 30); y1 = -190 * rng.uniform(0.8, 1.0)
            pts = []
            for y in ys:
                if y > y0 or y < y1: continue
                W = R07_HALF(y) - 8; m = mh(y); pts.append((XC(y) + sd * (m + f * max(W - m, 6)) + 3 * np.sin(y / 60 + ph), y))
            if len(pts) >= 4: out.append(pts)
    return out

# ---------------- web helpers: every web edge is a strand (attachment) or a catenary sag between two attachment points
def catenary(p0, p1, sag, ref):
    p0 = np.array(p0, float); p1 = np.array(p1, float); ref = np.array(ref, float); d = p1 - p0; n = np.array([-d[1], d[0]]); n /= np.linalg.norm(n) + 1e-9
    if np.dot(n, ref - (p0 + p1) / 2) < 0: n = -n
    return [tuple(p0 + d * u + n * sag * 4 * u * (1 - u)) for u in np.linspace(0, 1, 14)[1:]]
def sheet(A, B, ref, sag=0.3, seed=0):
    """web between strand paths A and B (xyz control points, near ends = roots): sides ride the strands, free end edge = one catenary between the two tips."""
    from engine import curve
    ca = curve(A, 6.0)[0]; cb = curve(B, 6.0)[0]; chord = np.linalg.norm(np.array(A[-1][:2]) - np.array(B[-1][:2]))
    poly = [tuple(p[:2]) for p in ca] + catenary(ca[-1][:2], cb[-1][:2], sag * chord, ref) + [tuple(p[:2]) for p in cb[::-1]]
    return dict(poly=poly, anchors=[[tuple(p) for p in ca[::3]], [tuple(p) for p in cb[::3]]])
def wing(a, e_drop, kfar=0.55, sag=0.30, drip_dx=10.0, name='D'):
    """arm <-> trunk web strung between 3 strands: the arm underside, a short drip strand hanging from the arm, and a trunk-flank strand; free edge = catenary drip-tip -> flank.
    returns (web dict, drip strand item)."""
    from engine import curve, tent_r
    sd = a['sd']; ca, ta, _ = curve(a['pts'], 3.0); Ra = tent_r(ta, a['R0'], 6.0, 0.75); sel = (ta > 0.12) & (ta < kfar); arm = ca[sel][::3]; Rr = Ra[sel][::3]
    tg = np.gradient(arm[:, :2], axis=0); tg /= np.linalg.norm(tg, axis=1)[:, None]; nr = np.stack([-tg[:, 1], tg[:, 0]], 1)
    if nr[:, 1].mean() > 0: nr = -nr
    low = arm[:, :2] + nr * (0.85 * Rr)[:, None]; e = low[-1]
    D = [(e[0], e[1], 70), (e[0] + sd * drip_dx * 0.5 - sd * 6, e[1] - 0.22 * e_drop, 62), (e[0] - sd * drip_dx * 0.55, e[1] - 0.42 * e_drop, 55), (e[0] - sd * drip_dx, e[1] - 0.58 * e_drop, 48)]
    dc = curve(D, 6.0)[0]; yr = low[0, 1]; yf = yr - 1.15 * e_drop; ys = np.linspace(yr, yf, 7); flank = [(XC(y) + sd * (R07_HALF(y) - 6), y) for y in ys]
    cat = catenary(dc[-1, :2], flank[-1], sag * np.linalg.norm(dc[-1, :2] - np.array(flank[-1])), (0.5 * (dc[0, 0] + XC(0)), dc[0, 1] - 0.3 * e_drop))
    poly = [tuple(p) for p in low] + [tuple(p[:2]) for p in dc[1:]] + cat + [tuple(p) for p in flank[::-1][1:]]
    web = dict(poly=poly, anchors=[[(p[0], p[1], p[2] - 8) for p in arm], [tuple(p) for p in dc[::2]], [(x, y, 46 - 0.04 * abs(y)) for x, y in flank]])
    return web, dict(name=name, pts=D, R0=14.0, n=1, seed=0.0, p=0.8, r_tip=4.6, lump=0.04, nodes=1, drip=True)

DENS = {'b': dict(n_arm=5, tines=5, branches=3, hole=0.28, hlen=84, asp=0.20, nodes=3, wing=(1.0, 0.8), rib=2, seed=12),
        'c': dict(n_arm=7, tines=7, branches=6, hole=0.26, hlen=70, asp=0.22, nodes=4, wing=(1.0, 0.9), rib=3, seed=13)}
HSEL = {'b': ['H1', 'H7', 'H2', 'H3', 'H4', 'H5', 'H6', 'H8'], 'c': ['H1', 'H7', 'H2', 'H3', 'H8', 'H4', 'H5', 'H6', 'H9']}

def make(d):
    P = DENS[d]; rng = np.random.default_rng(P['seed']); a1, a2, a3 = ARMS(); arms = [a1, a2, a3]
    for q, a in enumerate(arms): a.update(n=P['n_arm'], nodes=P['nodes'], seed=0.4 + 1.3 * q)
    Hs = hangers(); hang = []
    for nm in HSEL[d]:
        h = dict(Hs[nm]); pts = h['pts']
        if 'curl' in h: c_ = h.pop('curl'); pts = curl_end(pts, c_['turn'], c_['rad'], 6, c_['sgn'])
        hang.append(dict(name=nm, pts=pts, R0=h['R0'], n=h['n'], seed=h['seed'], nodes=2, limb=True, hang=True, p=0.7, raw=Hs[nm]['pts']))
    cr = crown(P['tines'], 5 + ord(d), P['branches'])
    for c_ in cr: c_['crown'] = True
    byname = {h['name']: h for h in hang}; webs = []; W = lambda **k: dict(holes=P['hole'], hlen=P['hlen'], asp=P['asp'], th=9.0, rim=10.0, **k)
    drips = []
    for k_, (a_, ed, kf, dx) in enumerate(((a1, 235 * P['wing'][0], 0.46, 45), (a2, 255 * P['wing'][0], 0.62, 50), (a3, 150 * P['wing'][1], 0.46, 40))):
        w_, dr_ = wing(a_, ed, kfar=kf, drip_dx=dx, name=f'D{k_}'); webs.append(W(seed=20 + k_, **w_)); drips.append(dr_)
    pairs = {'b': [('H1', 'H7', 3, 3), ('H2', 'H3', 3, 3), ('H3', 'H8', 3, 4), ('H4', 'H6', 4, 4)],
             'c': [('H1', 'H7', 4, 4), ('H1', 'H2', 3, 4), ('H2', 'H3', 3, 3), ('H3', 'H8', 3, 4), ('H8', 'H4', 4, 4), ('H4', 'H6', 4, 4)]}[d]
    for i, (n1, n2, k1, k2) in enumerate(pairs):
        A, B = byname[n1]['raw'][:k1 + 1], byname[n2]['raw'][:k2 + 1]; webs.append(W(seed=30 + i, **sheet(A, B, (0, -120), sag=0.30, seed=i)))
    # crown: small catenary webs between neighbouring tines near their bases (c only)
    if d == 'c':
        mains = [c for c in cr if c['name'].startswith('C')]
        for i in (0, 2, 4):
            if i + 1 < len(mains):
                A, B = mains[i]['pts'][:3], mains[i + 1]['pts'][:3]; webs.append(W(seed=50 + i, **sheet(A, B, MASK['c'], sag=0.35, seed=i)))
    hair = meridians(P['rib'], 9 + ord(d))
    return dict(id=f'G1a_{d}', name=f'G1a-r08c ({d}): r07 skeleton, narrow ribbed trunk, root-tine crown, catenary webs, jagged maw', gesture='G1 vertical trunk (r07 G1a skeleton)', seed=P['seed'], spine4=SPINE,
                mask=MASK, maw=MAW, items=arms + hang + cr + drips, webs=webs, tears=[], hair=hair, dens=d)
for d in 'bc': S[f'G1a_{d}'] = make(d)
STUDIES = S
