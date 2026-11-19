"""Round-13 specs: H13 (r12s H + S2 ball, refined, body scaled to air out the shelves inside 914 x 914) and E1 (same refinements, body NOT scaled, arms extended past 914 mm wide).
Derived from the r11 / r12s generators (studies_r11.py kept in lineage): the same skeleton, seeds, density set D2, fang set M1, eye sets and patch packing; everything below is a parametrised copy.
Coordinates mm: x right, y up, z out of wall. s = body-group scale (trunk, maw, patch, cluster, cascade, mask centre); shelves, arms (thickness), ball (D 180) and whip are NOT scaled.
Changes vs r12s H+S2 (each one axis): K4 grown plates (lobed edge, 5.5 mm rim, root flare, under-plate ribs, per-plate pattern), whip forked off the limb, patch blend (k 34 -> 64, one albedo), staggered cascade, arms/plates re-placed for the scale / envelope."""
import numpy as np
from engine import curve, tent_r, spine_rfun, maw_sd

TH0 = 34.0
# ---------------- r11 skeleton numbers (unscaled)
SPINE0 = [(8, 262, 40, 106), (3, 150, 18, 124), (-3, 20, 12, 132), (0, -110, 10, 116), (-4, -190, 8, 88), (-8, -245, 8, 44)]
MAW0 = dict(c=(10, -15), w=150, h=316, tilt=0.05, jag=0.11)
XC0 = lambda y: float(np.interp(y, [-250, -110, 20, 150, 262], [2, 0, -3, 3, 8]))
HALF0 = lambda y: float(np.interp(y, [-250, -110, 20, 150, 262], [88, 116, 132, 124, 106]))
PATCH_C0 = (8.0, 262.0); ROOT_XY0 = (0.0, 168.0); BALL_OFF = (-40.0, -14.0)
ROOTS0 = dict(S1_UL=(-105, 150), S2_UR=(70, 60), S3_LL=(-70, -100))
TOPS = dict(S1_UL=285, S2_UR=150, S3_LL=-190)

VARIANTS = {
    'H13': dict(s=0.84, x_out=452.0),      # body scale 0.84, plates' outer edge 452 (914 envelope, hard clip 457)
    'E1': dict(s=1.00, x_out=598.0),       # body unscaled, plates' outer edge 598 (overall width ~1200, hard clip 600)
}

# ---------------- K4 plate spec (grown palm): planform lobes + front scallops, rim 5.5 mm, belly, root flare, rib angles (deg, planform angle about the plate centre, 90 = front / +z)
PLATES = dict(
    S1_UL=dict(a=110.0, b=112.0, cz=117.0, seed=1, lobes=[(3, 0.050, 0.4), (5, 0.040, 2.1), (7, 0.028, 4.0)], scallop=(4.0, 0.085, 0.3), Tc=66.0, Tf=34.0, Rf=92.0, rib_n=5),
    S2_UR=dict(a=112.0, b=108.0, cz=113.0, seed=2, lobes=[(2, 0.060, 1.2), (4, 0.045, 5.0), (6, 0.034, 0.9), (9, 0.020, 3.3)], scallop=(3.5, 0.095, 1.7), Tc=74.0, Tf=38.0, Rf=98.0, rib_n=7),
    S3_LL=dict(a=108.0, b=114.0, cz=119.0, seed=3, lobes=[(3, 0.052, 5.6), (4, 0.038, 1.0), (8, 0.026, 2.6)], scallop=(5.0, 0.080, 4.4), Tc=82.0, Tf=42.0, Rf=104.0, rib_n=4),
)
T_EDGE = 5.5

def plate_rho_fn(P):
    """planform boundary radius rho(theta) of a grown plate: superellipse n = 2.3 x lobes x front scallops (theta = atan2(dz, dx); 90 deg = front)."""
    a, b = P['a'], P['b']; lobes = P['lobes']; sn, sa, sp = P['scallop']
    def rho(th):
        th = np.asarray(th, float); base = 1.0 / ((np.abs(np.cos(th)) / a) ** 2.3 + (np.abs(np.sin(th)) / b) ** 2.3) ** (1 / 2.3)
        sc = 1.0 + sum(A * np.sin(k * th + ph) for k, A, ph in lobes)
        w = np.exp(-((np.arctan2(np.sin(th - np.pi / 2), np.cos(th - np.pi / 2))) / np.radians(62)) ** 2)      # front arc weight
        sc = sc * (1.0 + sa * w * (2 * np.abs(np.sin(sn * (th - np.pi / 2) + sp)) - 1.0))
        return base * sc
    return rho

def plate_geom(P, sd):
    """closed forms for the plate: rho(th), thickness t(x, z), entry point E on the limb side."""
    rho = plate_rho_fn(P); cx, cz, top = P['cx'], P['cz'], P['top']; th_in = 0.0 if sd < 0 else np.pi
    xe = cx + np.cos(th_in) * (float(rho(th_in)) - 10.0); ze = cz - 22.0
    def thick(X, Z):
        dx, dz = X - cx, Z - cz; r = np.hypot(dx, dz); q = np.clip(r / rho(np.arctan2(dz, dx)), 0, 1)
        dE = np.hypot(X - xe, Z - ze)
        return T_EDGE + (P['Tc'] - T_EDGE) * (1 - q ** 2.2) ** 0.85 + P['Tf'] * np.exp(-(dE / P['Rf']) ** 2)
    return dict(rho=rho, thick=thick, E=(xe, ze), th_in=th_in)

# ---------------- arms
def arm(name, sh, root):
    cx, top = sh['cx'], sh['top']; ya = top - 44; sd = 1 if cx > root[0] else -1; ap = (cx - sd * 135, ya)
    p1 = (root[0] + 0.32 * (ap[0] - root[0]), root[1] + (ya - root[1]) * 0.15); p2 = (root[0] + 0.68 * (ap[0] - root[0]), root[1] + (ya - root[1]) * 0.75)
    tl = [(cx + sd * 55, ya, 108), (cx + sd * 95, ya - 3, 112), (cx + sd * 113, ya + 14, 112)]
    return dict(name=name, shelf=sh, root=root, ap=ap, sd=sd, ya=ya, limb=True, pts=[(root[0], root[1], 35), (p1[0], p1[1], 55), (p2[0], p2[1], 75), (ap[0], ap[1], 90), (cx, ya, 100)] + tl)

def make_arms(s, x_out):
    out = []
    for nm in ('S1_UL', 'S2_UR', 'S3_LL'):
        P = dict(PLATES[nm]); top = TOPS[nm]; sg = -1 if nm != 'S2_UR' else 1
        rho = plate_rho_fn(P); r_out = float(rho(np.pi if sg < 0 else 0.0))      # outer-edge radius along x
        P.update(top=top, cx=sg * (x_out - r_out)); root = (ROOTS0[nm][0] * s, ROOTS0[nm][1] * s)
        a = arm(nm, P, root); a['geom_sd'] = a['sd']; out.append(a)
    return out

def arm_len(a): return float(curve(a['pts'], 3.0)[2])

# ---------------- cascade (r11 hangers, staggered: start points along ~170 mm of the trunk bottom, lengths 0.78-1.0 x, R8)
def hangers0():
    H = {}
    H['H1'] = dict(pts=[(-40, -228, 24), (-105, -300, 30), (-190, -352, 36), (-285, -392, 42), (-365, -425, 46), (-418, -444, 48)], R0=54, n=3, curl=dict(turn=2.7, rad=20, sgn=1), seed=0.6)
    H['H7'] = dict(pts=[(-75, -160, 22), (-150, -210, 30), (-235, -262, 38), (-312, -318, 44), (-352, -378, 48)], R0=24, n=1, seed=1.1)
    H['H2'] = dict(pts=[(-44, -205, 24), (-70, -285, 30), (-84, -365, 38), (-70, -444, 44)], R0=30, n=2, seed=1.6)
    H['H3'] = dict(pts=[(-6, -226, 26), (-16, -292, 34), (-6, -352, 42)], R0=36, n=1, curl=dict(turn=3.2, rad=16, sgn=-1), seed=0.9)
    H['H8'] = dict(pts=[(-26, -240, 22), (6, -318, 30), (34, -380, 38), (22, -446, 42)], R0=17, n=1, seed=0.2)
    H['H4'] = dict(pts=[(20, -210, 24), (60, -300, 32), (120, -372, 40), (200, -418, 46), (276, -440, 50)], R0=36, n=2, seed=2.0)
    H['H6'] = dict(pts=[(54, -196, 24), (96, -262, 32), (120, -336, 40), (112, -400, 46)], R0=26, n=2, seed=0.4)
    H['H5'] = dict(pts=[(80, -118, 28), (178, -150, 38), (282, -176, 48), (372, -222, 56), (425, -292, 58), (428, -368, 58), (402, -428, 58)], R0=46, n=4, curl=dict(turn=2.8, rad=18, sgn=-1), seed=1.4)
    H['H9'] = dict(pts=[(106, -150, 22), (214, -190, 30), (306, -246, 38), (352, -318, 44)], R0=15, n=1, seed=1.9)
    return H
# new start (x, y) and length factor per hanger; the rest of each path is the old path rescaled about the new start
STAGGER = dict(H1=((-38, -250), 0.94), H7=((-75, -160), 0.82), H2=((-62, -188), 0.97), H3=((-16, -218), 0.78), H8=((-14, -284), 0.90), H4=((30, -246), 0.93), H6=((62, -176), 0.86), H5=((80, -118), 1.0), H9=((106, -150), 0.80))
def hangers(s):
    H = hangers0(); out = {}
    for nm, h in H.items():
        (nx, ny), f = STAGGER[nm]; p0 = np.array(h['pts'][0][:2], float); pts = [(nx, ny, h['pts'][0][2])]
        for p in h['pts'][1:]:
            q = np.array([nx, ny]) + f * (np.array(p[:2], float) - p0); pts.append((float(np.clip(q[0], -450, 450)), float(np.clip(q[1], -450, 450)), p[2]))
        d = dict(h); d['pts'] = [(x * s, y * s, z * s) for x, y, z in pts]; d['R0'] = h['R0'] * s; d['f'] = f; d['start'] = (nx * s, ny * s); out[nm] = d
    return out

def meridians(s, seed):
    """r11 meridians_A, evaluated on the unscaled skeleton then scaled (same random draws)."""
    rng = np.random.default_rng(seed); out = []; ys = np.linspace(172, -190, 16)
    mh = lambda y: (MAW0['w'] / 2 * np.sin(np.pi * np.clip((y - (MAW0['c'][1] - MAW0['h'] / 2)) / MAW0['h'], 0, 1) ** 0.82) ** 0.75 + 20) if (MAW0['c'][1] - MAW0['h'] / 2 - 8 < y < MAW0['c'][1] + MAW0['h'] / 2 + 8) else 0.0
    for sd in (-1, 1):
        for j in range(2):
            f = (j + 0.5 + rng.uniform(-0.15, 0.15)) / 2; ph = rng.uniform(0, 6.28); y0 = 172 - rng.uniform(0, 30); y1 = -190 * rng.uniform(0.8, 1.0); pts = []
            for y in ys:
                if y > y0 or y < y1: continue
                W = HALF0(y) - 8; m = mh(y); pts.append(((XC0(y) + sd * (m + f * max(W - m, 6)) + 3 * np.sin(y / 60 + ph)) * s, y * s))
            if len(pts) >= 4: out.append(pts)
    return out

def catenary(p0, p1, sag, ref):
    p0 = np.array(p0, float); p1 = np.array(p1, float); ref = np.array(ref, float); d = p1 - p0; n = np.array([-d[1], d[0]]); n /= np.linalg.norm(n) + 1e-9
    if np.dot(n, ref - (p0 + p1) / 2) < 0: n = -n
    return [tuple(p0 + d * u + n * sag * 4 * u * (1 - u)) for u in np.linspace(0, 1, 14)[1:]]
def sheet(A, B, ref, sag=0.3, seed=0):
    ca = curve(A, 6.0)[0]; cb = curve(B, 6.0)[0]; chord = np.linalg.norm(np.array(A[-1][:2]) - np.array(B[-1][:2]))
    poly = [tuple(p[:2]) for p in ca] + catenary(ca[-1][:2], cb[-1][:2], sag * chord, ref) + [tuple(p[:2]) for p in cb[::-1]]
    return dict(poly=poly, anchors=[[tuple(p) for p in ca[::3]], [tuple(p) for p in cb[::3]]])
def wing(a, e_drop, xc, half, k0, kfar, drip_dx, name='D', s=1.0):
    """r11 wing(): lace web hanging under the arm's trunk-side stretch (arc fraction k0..kfar of the arm path) to the trunk flank; k0 / kfar rescaled so the web covers the same absolute stretch as r11."""
    sd = a['sd']; ca, ta, _ = curve(a['pts'], 3.0); Ra = tent_r(ta, a['R0'], 6.0, a.get('p', 0.75)); sel = (ta > k0) & (ta < kfar); arm_ = ca[sel][::3]; Rr = Ra[sel][::3]
    tg = np.gradient(arm_[:, :2], axis=0); tg /= np.linalg.norm(tg, axis=1)[:, None]; nr = np.stack([-tg[:, 1], tg[:, 0]], 1)
    if nr[:, 1].mean() > 0: nr = -nr
    low = arm_[:, :2] + nr * (0.85 * Rr)[:, None]; e = low[-1]
    D = [(e[0], e[1], 70 * s), (e[0] + sd * drip_dx * 0.5 - sd * 6, e[1] - 0.22 * e_drop, 62 * s), (e[0] - sd * drip_dx * 0.55, e[1] - 0.42 * e_drop, 55 * s), (e[0] - sd * drip_dx, e[1] - 0.58 * e_drop, 48 * s)]
    dc = curve(D, 6.0)[0]; yr = low[0, 1]; yf = yr - 1.15 * e_drop; ys = np.linspace(yr, yf, 7); flank = [(xc(y) + sd * (half(y) - 6 * s), y) for y in ys]
    cat = catenary(dc[-1, :2], flank[-1], 0.30 * np.linalg.norm(dc[-1, :2] - np.array(flank[-1])), (0.5 * (dc[0, 0] + xc(0)), dc[0, 1] - 0.3 * e_drop))
    poly = [tuple(p) for p in low] + [tuple(p[:2]) for p in dc[1:]] + cat + [tuple(p) for p in flank[::-1][1:]]
    web = dict(poly=poly, anchors=[[(p[0], p[1], p[2] - 8) for p in arm_], [tuple(p) for p in dc[::2]], [(x, y, (46 - 0.04 * abs(y / s)) * s) for x, y in flank]])
    return web, dict(name=name, pts=D, R0=14.0, n=1, seed=0.0, p=0.8, r_tip=4.6, lump=0.04, nodes=1, drip=True)

DENS_D2 = dict(hsel=['H1', 'H7', 'H2', 'H3', 'H8', 'H4', 'H5', 'H6', 'H9'], pairs=[('H1', 'H7', 4, 4), ('H1', 'H2', 3, 4), ('H2', 'H3', 3, 3), ('H3', 'H8', 3, 4), ('H8', 'H4', 4, 4), ('H4', 'H6', 4, 4), ('H5', 'H9', 3, 3), ('H7', 'H2', 3, 3), ('H6', 'H9', 3, 2)],
               hole=0.26, hlen=70, asp=0.22, wing=(1.0, 0.9))
NARM, NODES, RIBN, SEED = 5, 3, 2, 12
WINGS = [(235, 0.46, 45), (255, 0.62, 50), (150, 0.46, 40)]
TEETH_M1 = dict(front=34, back=18, fangs=[3, 8, 14, 20, 27])

def eyes_E2(s):
    E = [dict(x=-128, y=96, G=34, lid='hood', pupil='slit', gaze=(0.2, 0.0), tilt=22), dict(x=-96, y=74, G=18, lid='ring', pupil='none', clouded=True, tilt=0),
         dict(x=-152, y=60, G=24, lid='turret', pupil='round', gaze=(-0.2, -0.2)), dict(x=-116, y=40, G=30, lid='ring', pupil='none', clouded=True, tilt=-10),
         dict(x=-84, y=26, G=16, lid='hood', pupil='round', gaze=(0.3, -0.1), tilt=-30), dict(x=-144, y=8, G=20, lid='ring', pupil='slit', gaze=(0.0, 0.2)),
         dict(x=-104, y=-10, G=26, lid='turret', pupil='slit', gaze=(0.0, 0.0)), dict(x=-72, y=-32, G=18, lid='ring', pupil='none', clouded=True)]
    for e in E: e['x'] *= s; e['y'] *= s; e['G'] = e['G'] * s
    return E, [dict(c=(-122 * s, 34 * s), a=52 * s, b=100 * s, z=36 * s, h=36 * s)]

def patch_eyes(s, seed=5):
    """12 mismatched eyes (15-50 mm) packed tight in a disc r 90 mm round PATCH_C (r11 generator, identical draws), then scaled by s about the origin (sizes too: the group is scaled WITH the body, not relative to it)."""
    rng = np.random.default_rng(seed); sizes = [50, 42, 36, 32, 30, 26, 24, 22, 20, 18, 16, 15]; lids = ['hood', 'ring', 'turret']; E = []
    for G in sizes:
        for _ in range(4000):
            r_ = 90 * np.sqrt(rng.uniform(0, 1)); th = rng.uniform(0, 6.283); x = PATCH_C0[0] + r_ * np.cos(th); y = PATCH_C0[1] + r_ * np.sin(th)
            a_, b_ = np.array(ROOT_XY0), np.array([-23.0, 213.0]); p_ = np.array([x, y]); u_ = np.clip(np.dot(p_ - a_, b_ - a_) / np.dot(b_ - a_, b_ - a_), 0, 1); dseg = np.linalg.norm(p_ - (a_ + u_ * (b_ - a_)))
            if dseg < G / 2 + 34: continue
            if all(np.hypot(x - e['x'], y - e['y']) >= 0.88 * (G + e['G']) / 2 for e in E): break
        else: raise RuntimeError('pack fail')
        E.append(dict(x=float(x), y=float(y), G=G, lid=lids[len(E) % 3], pupil=('slit' if len(E) % 3 != 1 else 'round'), clouded=bool(len(E) in (1, 4, 7, 9, 11)), tilt=float(rng.uniform(-35, 35)),
                      gaze=(float(rng.uniform(-.35, .35)), float(rng.uniform(-.35, .35))), swell=float(rng.uniform(1.25, 1.7)), pop=float(rng.uniform(0.40, 0.75)), veiny=True))
    for e in E: e['x'] *= s; e['y'] *= s; e['G'] = e['G'] * s
    return E

def whip_pts(cx_ur, limb_c):
    """r10/r11 whip (T2, 516 mm, curl kept) re-rooted: forks off the S2_UR limb 60 mm toward the trunk of the old departure point (cx - 73 -> cx - 133) (B R4). Head waypoints re-shaped so the whip drops away below the plate
    instead of running along its underside; the tail (from old point 4 on) is the old shape translated rigidly; the head is tuned so the arc length equals the old whip's."""
    old = np.array([(262, 104, 100), (330, 96, 104), (398, 86, 108), (436, 60, 104), (444, 14, 98), (432, -38, 92), (402, -82, 88), (360, -104, 86), (322, -92, 88), (304, -64, 92), (318, -40, 96), (338, -44, 100)], float)
    L_old = curve(old, 1.5)[2]; xf = cx_ur - 133.0; ic = int(np.argmin(np.abs(limb_c[:, 0] - xf) + 1e5 * (limb_c[:, 0] > cx_ur - 60))); F = limb_c[ic]
    tail = old[3:] - old[0] + F      # rigid translation of the old shape, old[3] lands at F + (174, -44)
    best = None
    for g in np.linspace(0.6, 1.4, 81):      # head shape stretch (x) to match the length
        head = [F, F + np.array([38 * g, -36, 0]), F + np.array([100 * g, -62, 2.0]), F + np.array([150 * g, -72, 3.0])]
        pts = np.vstack([head, tail[1:]]); L = curve(pts, 1.5)[2]
        if best is None or abs(L - L_old) < abs(best[0] - L_old): best = (L, pts, g)
    return [tuple(p) for p in best[1]], dict(L_old=float(L_old), L_new=float(best[0]), fork=[float(v) for v in F], head_stretch=float(best[2]))

def curl_end(pts, turn, rad=26, n=5, sgn=1):
    p = np.array(pts, float); d = p[-1, :2] - p[-2, :2]; d /= np.linalg.norm(d); out = list(map(tuple, p))
    c = p[-1, :2] + sgn * rad * np.array([-d[1], d[0]]); ph0 = np.arctan2(p[-1, 1] - c[1], p[-1, 0] - c[0])
    for i in range(1, n + 1):
        u = i / n; ph = ph0 + sgn * turn * u; r_ = rad * (1 - 0.45 * u)
        out.append((c[0] + r_ * np.cos(ph), c[1] + r_ * np.sin(ph), p[-1, 2] + 6 * u))
    return out

def compose(var):
    V = VARIANTS[var]; s = V['s']; arms = make_arms(s, V['x_out']); P = DENS_D2
    # reference r11 arm path lengths (unscaled roots, r11 plate positions) so the lace stretch under each arm stays the same absolute length
    ref = {}
    for nm, cx in (('S1_UL', -335.0), ('S2_UR', 335.0), ('S3_LL', -335.0)):
        ref[nm] = arm_len(arm(nm, dict(cx=cx, top=TOPS[nm]), ROOTS0[nm]))
    spine = [(x * s, y * s, z * s, r * s) for x, y, z, r in SPINE0]
    xc = lambda y: s * XC0(y / s); half = lambda y: s * HALF0(y / s)
    maw = dict(MAW0); maw.update(c=(MAW0['c'][0] * s, MAW0['c'][1] * s), w=MAW0['w'] * s, h=MAW0['h'] * s)
    for q, a in enumerate(arms): a.update(n=NARM, nodes=NODES, seed=0.4 + 1.3 * q)
    for a, R0 in zip(arms, (15.0, 30.0, 50.0)): a.update(n=1, smooth=True, R0=R0, p=0.6, r_tip=6.0)
    for a in arms:
        if a['name'] == 'S3_LL': a['eyerow'] = 9
        if a['name'] == 'S2_UR': a['eyerow'] = 7
    Hs = hangers(s); hang = []
    for nm in P['hsel']:
        h = dict(Hs[nm]); pts = h['pts']
        if 'curl' in h: c_ = h.pop('curl'); pts = curl_end(pts, c_['turn'], c_['rad'] * s, 6, c_['sgn'])
        hang.append(dict(name=nm, pts=pts, R0=h['R0'], n=h['n'], seed=h['seed'], nodes=2, limb=True, hang=True, p=0.7, raw=Hs[nm]['pts']))
    byname = {h['name']: h for h in hang}; webs = []; W = lambda **k: dict(holes=P['hole'], hlen=P['hlen'], asp=P['asp'], th=9.0, rim=10.0, **k); drips = []
    wsc = (P['wing'][0], P['wing'][0], P['wing'][1])
    for k_, (a_, (ed, kf, dx)) in enumerate(zip(arms, WINGS)):
        Ln = arm_len(a_); rr = ref[a_['name']] * s / Ln; w_, dr_ = wing(a_, ed * wsc[k_] * s, xc, half, 0.12 * rr, kf * rr, dx * s, name=f'D{k_}', s=s); webs.append(W(seed=20 + k_, **w_)); drips.append(dr_)
    for i, (n1, n2, k1, k2) in enumerate(P['pairs']):
        A, B = byname[n1]['raw'][:k1 + 1], byname[n2]['raw'][:k2 + 1]; webs.append(W(seed=30 + i, **sheet(A, B, (0, -120 * s), sag=0.30, seed=i)))
    items = arms + hang
    ur = [a for a in arms if a['name'] == 'S2_UR'][0]; limb_c = curve(ur['pts'], 1.5)[0]
    wp, winfo = whip_pts(ur['shelf']['cx'], limb_c)
    items.append(dict(name='W_whip', pts=wp, R0=19.0, p=0.5, r_tip=5.0, smooth=True, limb=True, whip=True, k=12.0, fork_x=winfo['fork'][0])); items += drips
    pc = (PATCH_C0[0] * s, PATCH_C0[1] * s); E, B = eyes_E2(s)
    held = dict(c=(pc[0] + BALL_OFF[0], pc[1] + BALL_OFF[1]), roll=15.0, pitch=0.0, yaw=0.0, boss=(0.0, -36.0), root_pref=(ROOT_XY0[0] * s, ROOT_XY0[1] * s), root_r=48, grip='F', clear_margin=7.0, clear_start=45)
    held = ball_held(held, 'S2')
    d = dict(id=var, name=f'{var}: r12s H+S2 + K4 grown plates + whip fork + patch blend + staggered cascade' + (' + body scale %.2f' % s if s != 1 else ' + arms extended, width ~1200'), gesture='G1 vertical trunk (r07 G1a skeleton); ball held on a tentacle over an eye patch',
             seed=SEED, spine4=spine, mask=dict(c=held['c'], D=held['D'], z=0, dz=held['dz']), held=held, patch=dict(c=pc, a=108 * s, b=108 * s, z=62 * s, h=44 * s, eyes=patch_eyes(s)), maw=maw, items=items, webs=webs, tears=[], dens='D2',
             eyes=E, bulges=B, scale=s, root_xy=(ROOT_XY0[0] * s, ROOT_XY0[1] * s), whip=winfo, stagger={k: dict(start=v['start'], f=v['f']) for k, v in Hs.items()}, ref_arm_len=ref, x_out=V['x_out'])
    d['hair'] = meridians(s, 9 + ord('b')); d['teeth_cfg'] = TEETH_M1
    return d

# ---------------- ball S2 (r12s studies_s.ball_held, unchanged numbers)
BALLS = {'S2': dict(D=180.0, ratio=0.60, gap=66.0)}
def ball_held(base, name, grip=None, **over):
    b = BALLS[name]; a = b['D'] / 2; sc = a / 100.0; h = dict(base)
    bu, bv = h.get('boss', (0.0, -36.0)); h.update(shape='ball', D=b['D'], ratio=b['ratio'], dz=b['ratio'] * a, rim=0.0, gap=over.pop('gap', b['gap']), boss=(bu * sc, bv * sc), pad_inset=14.0, seat_max_deg=35.0, ball=name)
    if grip: h['grip'] = grip
    h['boss_search'] = over.pop('boss_search', False); h.update(over); return h

def get(sid): return compose(sid)
