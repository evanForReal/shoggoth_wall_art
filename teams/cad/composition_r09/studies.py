"""Round-09 studies (composition_r09). Body = r08c G1a_b trunk (ribbed, narrow, jagged maw, hanging lower body), no crown; 3 DISTINCT shelf tentacles
(massive R0 52 / medium R0 31 / whip R0 15), eyes in flesh sockets (mismatched, one clouded, one slit/blown, one on a tentacle root), blade teeth in the maw.
Coordinates mm: x right, y up, z out of the wall; envelope +-457."""
import numpy as np
from engine import curve
S = {}
def shelf(cx, top, cz=126, a=124, b=124, seed=1): return dict(cx=cx, top=top, cz=cz, a=a, b=b, seed=seed)
def zline(xy, z0=40.0, z1=104.0):
    n = len(xy); return [(p[0], p[1], z0 + (z1 - z0) * (i / max(n - 1, 1)) ** 0.8) for i, p in enumerate(xy)]
def grip(cx, top, sd, hook=True):
    """tail of a limb arriving from side `sd` (+1: from the left, running +x): level under the plate, then lifting at the outer rim."""
    ya = top - 44
    pts = [(cx - sd * 100, ya, 104), (cx - sd * 10, ya, 108), (cx + sd * 82, ya + 1, 112), (cx + sd * 116, ya + 22, 114)]
    if hook: pts += [(cx + sd * 112, top - 26, 114)]
    return pts
def body(mx, my, lean=0.0, head_r=118):
    dy = np.array([0, -112, -242, -372, -452, -507]); rad = [head_r, 124, 132, 116, 88, 44]; z = [40, 18, 12, 10, 8, 8]
    return [(mx + lean * (d / -507.0), my + d, zz, r) for d, zz, r in zip(dy, z, rad)]
def maw_for(mx, my, lean=0.0, tilt=0.05): return dict(c=(mx + 2 + lean * 277 / 507, my - 277), w=150, h=316, tilt=tilt, jag=0.11)
def ribs_for(mx, my, lean, n=2):
    out = []; ys = np.linspace(my - 90, my - 440, 12)
    for sd in (-1, 1):
        for j in range(n):
            f_ = (j + 0.5) / n; pts = []
            for y in ys:
                dy = my - y; half = float(np.interp(dy, [0, 112, 242, 372, 452], [100, 116, 124, 108, 80]))
                mh = (75 * np.sin(np.pi * np.clip((y - (my - 277 - 158)) / 316, 0, 1) ** 0.82) ** 0.75 + 22) if (my - 277 - 168 < y < my - 277 + 168) else 0.0
                x0 = mx + lean * (dy / 507.0); pts.append((x0 + sd * (mh + f_ * max(half - mh, 8)), y))
            pts = [p for p in pts if p[1] > my - 430]
            if len(pts) >= 4: out.append(pts)
    return out
def eyes_for(mx, my, side=1):
    """off-axis cluster hosted by a flesh swelling beside the mask; not on a horizontal axis."""
    bx, by = mx + side * 128, my - 68
    E = [dict(x=bx - side * 2, y=by + 8, G=64, lid='hood', pupil='slit', gaze=(0.18 * side, 0.1), tilt=-18 * side),
         dict(x=bx + side * 40, y=by - 62, G=40, lid='ring', pupil='none', clouded=True, tilt=20 * side),
         dict(x=bx + side * 6, y=by - 100, G=26, lid='turret', pupil='round', gaze=(-0.2 * side, -0.15)),
         dict(x=bx + side * 62, y=by + 52, G=22, lid='ring', pupil='none')]
    return E, [dict(c=(bx + side * 8, by - 18), a=58, b=96, z=38, h=44)]
def web(A, B, ref, sag=0.3, seed=0):
    from engine import curve as cv
    ca = cv(A, 6.0)[0]; cb = cv(B, 6.0)[0]; chord = np.linalg.norm(np.array(A[-1][:2]) - np.array(B[-1][:2]))
    p0, p1 = np.array(ca[-1][:2]), np.array(cb[-1][:2]); d = p1 - p0; n = np.array([-d[1], d[0]]); n /= np.linalg.norm(n) + 1e-9
    if np.dot(n, np.array(ref) - (p0 + p1) / 2) < 0: n = -n
    cat = [tuple(p0 + d * u + n * sag * chord * 4 * u * (1 - u)) for u in np.linspace(0, 1, 14)[1:]]
    return dict(poly=[tuple(p[:2]) for p in ca] + cat + [tuple(p[:2]) for p in cb[::-1]], anchors=[[tuple(p) for p in ca[::3]], [tuple(p) for p in cb[::3]]], seed=seed)
def hang(name, xy, R0, z0=24):
    return dict(name=name, pts=[(x, y, z0 + 6 * i) for i, (x, y) in enumerate(xy)], R0=R0, p=0.7, r_tip=6.0)

def assemble(id_, name, gest, mask_c, lean, limbs, hangs, eye_side, webs=(), seed=1):
    mx, my = mask_c; E, B = eyes_for(mx, my, eye_side)
    c_, t_, _ = curve(limbs[0]['pts'], 3.0); k_ = int(0.2 * (len(c_) - 1)); E.append(dict(x=float(c_[k_][0]), y=float(c_[k_][1]), G=36, lid='hood', pupil='slit', gaze=(0.1, -0.1), tilt=25, z=None))
    return dict(id=id_, name=name, gesture=gest, seed=seed, spine4=body(mx, my, lean), mask=dict(c=(mx, my), D=200, z=74, dz=26), maw=maw_for(mx, my, lean), limbs=limbs + hangs,
                webs=list(webs), ribs=ribs_for(mx, my, lean, 2), eyes=E, bulges=B, teeth=26, fang_angle=140.0 if eye_side > 0 else 40.0)

# ---- S1: weight ladder + asymmetric fan (body off to the left; massive low, medium mid, whip arcing high)
def s1():
    mx, my = -175, 262; sh_m = shelf(340, -330, seed=1); sh_d = shelf(340, 68, seed=2); sh_w = shelf(70, 446, seed=3)
    massive = dict(name='T_massive', R0=52, p=0.5, shelf=sh_m, suckers=11, s0=0.10, s1=0.78, fingers=6,
                   pts=zline([(-120, -130), (-20, -220), (100, -310), (190, -360), (225, -374)], 40, 100) + grip(340, -330, 1))
    medium = dict(name='T_medium', R0=31, p=0.55, shelf=sh_d, suckers=8, s0=0.10, s1=0.75, fingers=5,
                  pts=zline([(-90, 50), (0, 28), (100, 6), (190, 18), (225, 24)], 40, 100) + grip(340, 68, 1))
    whip = dict(name='T_whip', R0=15, p=0.5, shelf=sh_w, fingers=5, r_tip=5.0,
                pts=zline([(-95, 215), (-55, 285), (-35, 350)], 36, 90) + grip(70, 446, 1))
    hangs = [hang('H1', [(-190, -220), (-205, -300), (-190, -380), (-215, -440)], 28), hang('H2', [(-150, -240), (-130, -310), (-100, -360)], 17), hang('H3', [(-230, -190), (-290, -260), (-300, -330)], 14)]
    return assemble('S1', 'S1 weight ladder + asymmetric fan', 'body left, three tentacles fan right, bare wall left and between', (mx, my), -15, [massive, medium, whip], hangs, -1, seed=1)
# ---- S2: reach (body low-left, limbs climb a rising diagonal)
def s2():
    mx, my = -215, 120; sh1 = shelf(215, -230, seed=4); sh2 = shelf(345, 165, seed=5); sh3 = shelf(40, 360, seed=6)
    massive = dict(name='T_massive', R0=52, p=0.5, shelf=sh1, suckers=11, s0=0.10, s1=0.78, fingers=6,
                   pts=zline([(-120, -150), (-30, -215), (60, -262)], 40, 100) + grip(215, -230, 1))
    medium = dict(name='T_medium', R0=31, p=0.55, shelf=sh2, suckers=8, s0=0.10, s1=0.75, fingers=5,
                  pts=zline([(-100, 40), (-20, 100), (80, 132), (150, 128)], 40, 100) + grip(345, 165, 1))
    whip = dict(name='T_whip', R0=15, p=0.5, shelf=sh3, fingers=5, r_tip=5.0,
                pts=zline([(-108, 90), (-62, 190), (-42, 270), (-30, 316)], 36, 100) + grip(40, 360, 1))
    hangs = [hang('H1', [(-235, -250), (-250, -330), (-232, -440)], 24), hang('H2', [(-200, -270), (-175, -340), (-150, -400)], 15)]
    return assemble('S2', 'S2 reach: rising diagonal', 'body low-left, limbs climb right/up', (mx, my), -8, [massive, medium, whip], hangs, -1, seed=2)
# ---- S3: one dominant serpentine limb through all three shelves + two stubs
def s3():
    mx, my = 0, 262; shR = shelf(335, -56, seed=7); shL = shelf(-240, -330, seed=8); shT = shelf(-335, 330, seed=9)
    path = [(60, -50), (150, -80), (240, -100)]
    pts = zline(path, 40, 100) + [(235, -100, 104), (325, -100, 108), (400, -100, 112), (438, -135, 108), (432, -230, 100), (372, -320, 92), (270, -385, 88), (150, -410, 84), (40, -395, 90), (-20, -376, 100), (-100, -374, 106), (-190, -374, 110), (-280, -372, 112), (-350, -362, 110),
        (-410, -325, 106), (-432, -240, 102), (-436, -100, 100), (-434, 60, 98), (-430, 190, 98), (-420, 256, 100), (-385, 286, 104), (-330, 286, 108), (-250, 284, 112)]
    # (path is built level under each plate; fingers below)
    dom = dict(name='T_dominant', R0=54, p=0.42, shelf=shR, suckers=16, s0=0.06, s1=0.55, fingers=0, pts=pts, r_tip=9.0, k=18.0)
    stub1 = dict(name='T_stub_a', R0=26, p=0.7, pts=zline([(-90, 120), (-160, 90), (-210, 50), (-230, 10)], 36, 60), r_tip=7.0)
    stub2 = dict(name='T_stub_b', R0=20, p=0.7, pts=zline([(90, -170), (150, -230), (170, -300)], 30, 50), r_tip=6.0)
    d = assemble('S3', 'S3 serpentine: one dominant limb through three shelves', 'one limb loops right shelf, under the body, low-left shelf, up the left edge to the top-left shelf', (mx, my), 0, [dom, stub1, stub2], [], 1, seed=3)
    d['plates_extra'] = [shL, shT]; return d
# ---- S4: hanging (body high, limbs droop and hook up under shelves; shelves sit above the hooks, limbs stay out of every shelf's clear zone)
def s4():
    mx, my = 20, 300; shR = shelf(335, -200, seed=10); shLo = shelf(-320, -300, seed=11); shLm = shelf(-335, 150, seed=12)
    massive = dict(name='T_massive', R0=50, p=0.5, shelf=shR, suckers=11, s0=0.10, s1=0.70, fingers=6,
                   pts=[(100, 120, 40), (150, 0, 52), (170, -150, 64), (195, -300, 78), (250, -392, 90), (330, -405, 100), (385, -350, 108), (395, -290, 112), (385, -266, 114)])
    medium = dict(name='T_medium', R0=31, p=0.55, shelf=shLo, suckers=8, s0=0.10, s1=0.70, fingers=5,
                  pts=[(-80, 150, 40), (-100, 40, 52), (-130, -120, 66), (-170, -260, 80), (-205, -390, 92), (-270, -425, 100), (-330, -410, 106), (-350, -385, 110), (-345, -366, 112)])
    whip = dict(name='T_whip', R0=15, p=0.5, shelf=shLm, fingers=5, r_tip=5.0,
                pts=[(-90, 230, 36), (-150, 160, 52), (-215, 95, 68), (-290, 45, 84), (-340, 40, 96), (-360, 62, 104), (-362, 84, 108)])
    hangs = [hang('H1', [(30, -150), (60, -230), (40, -310)], 20), hang('H2', [(-30, -130), (-50, -190)], 14)]
    return assemble('S4', 'S4 hanging: limbs droop from a high body and hook up under the shelves', 'high body, drooping hooks', (mx, my), 5, [massive, medium, whip], hangs, 1, seed=4)
# ---- S5/S6: r08c G1a_b (A) body kept: ribbed trunk, hanging root cascade (thinned to 5 strands), 2 webs; crown removed; arms replaced by 3 distinct tentacles at A's shelf positions
def curl_end(pts, turn, rad=26, n=5, sgn=1):
    p = np.array(pts, float); d = p[-1, :2] - p[-2, :2]; d /= np.linalg.norm(d); out = list(map(tuple, p))
    c = p[-1, :2] + sgn * rad * np.array([-d[1], d[0]]); ph0 = np.arctan2(p[-1, 1] - c[1], p[-1, 0] - c[0])
    for i in range(1, n + 1):
        u = i / n; ph = ph0 + sgn * turn * u; r_ = rad * (1 - 0.45 * u); out.append((c[0] + r_ * np.cos(ph), c[1] + r_ * np.sin(ph), p[-1, 2] + 6 * u))
    return out
def catenary(p0, p1, sag, ref):
    p0 = np.array(p0, float); p1 = np.array(p1, float); ref = np.array(ref, float); d = p1 - p0; n = np.array([-d[1], d[0]]); n /= np.linalg.norm(n) + 1e-9
    if np.dot(n, ref - (p0 + p1) / 2) < 0: n = -n
    return [tuple(p0 + d * u + n * sag * 4 * u * (1 - u)) for u in np.linspace(0, 1, 14)[1:]]
XC5 = lambda y: float(np.interp(y, [-250, -110, 20, 150, 262], [2, 0, -3, 3, 8])); HALF5 = lambda y: float(np.interp(y, [-250, -110, 20, 150, 262], [88, 116, 132, 124, 106]))
def wing(a, e_drop, kfar=0.55, sag=0.30, drip_dx=45.0, name='D', seed=0):
    from engine import tent_r
    sd = a['sd']; ca, ta, _ = curve(a['pts'], 3.0); Ra = tent_r(ta, a['R0'], 6.0, 0.6); sel = (ta > 0.12) & (ta < kfar); arm = ca[sel][::3]; Rr = Ra[sel][::3]
    tg = np.gradient(arm[:, :2], axis=0); tg /= np.linalg.norm(tg, axis=1)[:, None]; nr = np.stack([-tg[:, 1], tg[:, 0]], 1)
    if nr[:, 1].mean() > 0: nr = -nr
    low = arm[:, :2] + nr * (0.85 * Rr)[:, None]; e = low[-1]
    D = [(e[0], e[1], 70), (e[0] - sd * 6 + sd * drip_dx * 0.0, e[1] - 0.22 * e_drop, 62), (e[0] - sd * drip_dx * 0.55, e[1] - 0.42 * e_drop, 55), (e[0] - sd * drip_dx, e[1] - 0.58 * e_drop, 48)]
    dc = curve(D, 6.0)[0]; yr = low[0, 1]; yf = yr - 1.15 * e_drop; ys = np.linspace(yr, yf, 7); flank = [(XC5(y) + sd * (HALF5(y) - 6), y) for y in ys]
    cat = catenary(dc[-1, :2], flank[-1], sag * np.linalg.norm(dc[-1, :2] - np.array(flank[-1])), (0.5 * (dc[0, 0] + XC5(0)), dc[0, 1] - 0.3 * e_drop))
    poly = [tuple(p) for p in low] + [tuple(p[:2]) for p in dc[1:]] + cat + [tuple(p) for p in flank[::-1][1:]]
    web = dict(poly=poly, anchors=[[(p[0], p[1], p[2] - 8) for p in arm], [tuple(p) for p in dc[::2]], [(x, y, 46 - 0.04 * abs(y)) for x, y in flank]], holes=0.28, hlen=84, asp=0.2, seed=seed)
    return web, dict(name=name, pts=D, R0=14.0, p=0.8, r_tip=4.6)
def cascade5():
    H = []
    H.append(dict(name='H1', pts=curl_end([(-40, -228, 24), (-105, -300, 30), (-190, -352, 36), (-285, -392, 42), (-365, -425, 46), (-418, -444, 48)], 2.7, 20, 6, 1), R0=44, n=3, seed=0.6, p=0.7))
    H.append(dict(name='H2', pts=[(-44, -205, 24), (-70, -285, 30), (-84, -365, 38), (-70, -444, 44)], R0=28, n=2, seed=1.6, p=0.7))
    H.append(dict(name='H3', pts=curl_end([(-6, -226, 26), (-16, -292, 34), (-6, -352, 42)], 3.2, 16, 6, -1), R0=32, n=1, seed=0.9, p=0.7))
    H.append(dict(name='H4', pts=[(20, -210, 24), (60, -300, 32), (120, -372, 40), (200, -418, 46), (276, -440, 50)], R0=34, n=2, seed=2.0, p=0.7))
    H.append(dict(name='H6', pts=[(54, -196, 24), (96, -262, 32), (120, -336, 40), (112, -400, 46)], R0=24, n=2, seed=0.4, p=0.7))
    return H
def eyes_s6(mx, my):
    E = [dict(x=mx + 132, y=my + 6, G=66, lid='hood', pupil='slit', gaze=(0.15, 0.1), tilt=-16),
         dict(x=mx - 112, y=my - 250, G=46, lid='ring', pupil='none', clouded=True, tilt=15),
         dict(x=mx + 170, y=my - 58, G=26, lid='ring', pupil='round', gaze=(-0.2, -0.1)),
         dict(x=mx + 148, y=my - 112, G=22, lid='turret', pupil='slit', gaze=(0.0, -0.2)),
         dict(x=mx + 194, y=my - 108, G=20, lid='ring', pupil='none')]
    B = [dict(c=(mx + 140, my - 36), a=62, b=100, z=38, h=44), dict(c=(mx - 114, my - 250), a=48, b=58, z=34, h=40)]
    return E, B
def s56(id_, six):
    mx, my = 8, 262; shUL = shelf(-335, 285, seed=3); shLL = shelf(-335, -190, seed=4); shUR = shelf(335, 150, seed=5)
    massive = dict(name='T_massive', R0=52, p=0.5, shelf=shLL, suckers=11, s0=0.10, s1=0.78, fingers=6, pts=zline([(-70, -100), (-120, -150), (-175, -200), (-212, -226)], 40, 100) + grip(-335, -190, -1))
    medium = dict(name='T_medium', R0=31, p=0.55, shelf=shUR, suckers=8, s0=0.10, s1=0.75, fingers=5, pts=zline([(70, 60), (130, 85), (190, 100)], 40, 100) + grip(335, 150, 1))
    whip = dict(name='T_whip', R0=15, p=0.5, shelf=shUL, fingers=5, r_tip=5.0, pts=zline([(-105, 150), (-145, 185), (-185, 215), (-208, 232)], 36, 100) + grip(-335, 285, -1))
    w1, d1 = wing(dict(pts=medium['pts'][:5], R0=31, sd=1), 190, kfar=0.7, drip_dx=40, name='D0', seed=21)
    w2, d2 = wing(dict(pts=massive['pts'][:5], R0=52, sd=-1), 120, kfar=0.7, drip_dx=40, name='D1', seed=22)
    if six: E, B = eyes_s6(mx, my)
    else: E, B = eyes_for(mx, my, 1)
    c_, t_, _ = curve(massive['pts'], 3.0); k_ = int(0.2 * (len(c_) - 1)); E.append(dict(x=float(c_[k_][0]), y=float(c_[k_][1]), G=36, lid='hood', pupil='slit', gaze=(0.1, -0.1), tilt=25, z=None))
    return dict(id=id_, name=id_ + (' A + eyes pushed' if six else ' A body: tentacles, thinned cascade, 2 webs'), gesture='r08c A body, shelf positions of A', seed=5 + six, spine4=body(mx, my, 0.0), mask=dict(c=(mx, my), D=200, z=74, dz=26),
                maw=dict(c=(mx + 2, my - 277), w=150, h=316, tilt=0.05, jag=0.11), limbs=[massive, medium, whip] + cascade5() + [d1, d2], webs=[w1, w2], ribs=ribs_for(mx, my, 0.0, 3), eyes=E, bulges=B,
                teeth_cfg=dict(front=34, back=18, fangs=[3, 8, 14, 20, 27]), fang_angle=140.0)
S['S5'] = s56('S5', 0); S['S6'] = s56('S6', 1)
for fn in (s1, s2, s3, s4):
    st = fn(); S[st['id']] = st
STUDIES = S
