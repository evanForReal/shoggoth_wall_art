"""Round-08 studies: trunk-bodied figures with strand-bundle limbs, lace webs, gothic ribs, pendant (non-standing) lower body.
Coordinates mm: x right, y up, z out of wall; envelope +-457."""
import numpy as np
S = {}
def shelf(cx, top, cz=105, a=118, b=100, seed=1): return dict(cx=cx, top=top, cz=cz, a=a, b=b, seed=seed)
def arm(name, sh, root, R0, n=4, seed=0.0):
    cx, top = sh['cx'], sh['top']; ya = top - 44; sd = 1 if cx > root[0] else -1; ap = (cx - sd * 135, ya)
    p1 = (root[0] + 0.32 * (ap[0] - root[0]), root[1] + (ya - root[1]) * 0.15); p2 = (root[0] + 0.68 * (ap[0] - root[0]), root[1] + (ya - root[1]) * 0.75)
    tail = [(cx + sd * 60, ya, 108), (cx + sd * 100, ya - 4, 112), (cx + sd * 122, ya + 10, 112)]
    pts = [(root[0], root[1], 38), (p1[0], p1[1], 55), (p2[0], p2[1], 75), (ap[0], ap[1], 90), (cx, ya, 100)] + tail
    return dict(name=name, R0=R0, n=n, shelf=sh, pts=pts, seed=seed, wave=(0.05 * np.hypot(ap[0] - root[0], ap[1] - root[1]) * (1 if sd > 0 else -1), 2.0, 0.0, 0.42), root=root, ap=ap, sd=sd, ya=ya)
def hang(name, pts, R0, n=3, seed=0.0, amp=0.05, p=0.75):
    ln = float(np.linalg.norm(np.diff(np.array(pts)[:, :2], axis=0), axis=1).sum()); sg = 1 if seed > 1.0 else -1
    return dict(name=name, R0=R0, n=n, pts=pts, seed=seed, p=p, wave=(sg * amp * ln, 2.0, 0.0, 0.85))
def web_under_arm(a, drop=30, e_drop=150, bow=16, seed=0, cell=44):
    (rx, ry), (ax, ay), sd = a['root'], a['ap'], a['sd']
    p1 = a['pts'][1]; O = (ax + sd * 50, ay - drop - 4); E = (sd * 176, ry - e_drop); M = ((O[0] + E[0]) / 2 - sd * bow, (O[1] + E[1]) / 2 + 8)
    poly = [(sd * 150, ry + 10), (p1[0], p1[1] - 14), (ax, ay - drop), O, M, ((M[0] + E[0]) / 2 - sd * 4, (M[1] + E[1]) / 2), E, (sd * 140, ry - e_drop + 30), (sd * 140, ry - 20)]
    anch = [[(p1[0], p1[1] - 10, 45), (ax, ay - 12, 82), (O[0], O[1] + 8, 92)], [(E[0], E[1], 55), (M[0], M[1], 72)]]
    return dict(poly=poly, anchors=anch, cell=cell, seed=seed, sag=0.20)
def web_between(a, b, i0, i1, j0, j1, seed=0, cell=40, sag=0.25):
    A = [tuple(p) for p in a['pts'][i0:i1]]; B = [tuple(p) for p in b['pts'][j0:j1]]
    return dict(poly=[p[:2] for p in A] + [p[:2] for p in B[::-1]], anchors=[A, B], cell=cell, seed=seed, sag=sag, rim=8.0)
def maw_ribs(c, w, h, tilt=0.0, off=17.0):
    out = []
    for sg in (-1, 1):
        pts = []
        for t in np.linspace(0.07, 0.93, 14):
            prof = np.sin(np.pi * t ** 0.82) ** 0.75; x = sg * (w / 2 * prof + off) ; y = (t - 0.5) * (h + 36)
            pts.append((c[0] + x * np.cos(tilt) - y * np.sin(tilt), c[1] + x * np.sin(tilt) + y * np.cos(tilt)))
        out.append(pts)
    return out
MASK = dict(c=(8, 262), D=200, z=100, dz=26)
HEAD = [(10, 428, 44, 8), (9, 380, 50, 70), (7, 330, 48, 120), (6, 262, 40, 146), (2, 190, 30, 172), (-2, 110, 22, 190), (-6, 20, 14, 188), (-8, -70, 8, 160)]
MAW = dict(c=(0, -20), w=200, h=300, tilt=0.0)
TRUNK_RIBS = [[(-118, 300), (-152, 200), (-172, 100), (-168, -30), (-135, -150)], [(126, 292), (156, 190), (176, 85), (172, -60), (128, -185)],
              [(-60, 372), (-96, 300), (-120, 215)], [(52, 368), (92, 300), (118, 225)]]

def g1_common():
    a1 = arm('S1_UL', shelf(-335, 285), (-80, 20), 52, seed=0.3)
    a2 = arm('S2_UR', shelf(335, 150, seed=2), (80, -110), 52, seed=1.7)
    a3 = arm('S3_LL', shelf(-335, -190, seed=3), (-60, -130), 38, seed=2.4)
    return a1, a2, a3

def g1_i():
    a1, a2, a3 = g1_common()
    sp = HEAD + [(-10, -165, 8, 116), (-6, -250, 8, 62), (4, -330, 8, 34), (18, -395, 8, 20), (34, -445, 8, 8)]
    h1 = hang('H1', [(-40, -60, 20), (-95, -150, 26), (-130, -250, 34), (-150, -340, 42), (-172, -440, 48)], 40, 3, 0.6)
    h2 = hang('H2', [(70, -100, 20), (112, -190, 28), (135, -280, 34), (152, -360, 40), (138, -430, 44)], 30, 3, 1.9)
    h3 = hang('H3', [(30, -230, 22), (62, -300, 30), (108, -365, 36), (195, -412, 40), (270, -442, 44)], 22, 2, 1.4)
    h4 = hang('H4', [(-8, -300, 22), (-62, -352, 30), (-125, -402, 36), (-205, -430, 40), (-290, -447, 44)], 16, 1, 0.8)
    limbs = [a1, a2, a3, h1, h2, h3, h4]
    webs = [web_under_arm(a1, seed=1), web_under_arm(a2, seed=2, e_drop=260, drop=40), web_between(h1, h2, 1, 4, 1, 3, seed=3), web_between(h2, h3, 0, 3, 0, 2, seed=4, cell=36)]
    return dict(id='G1a_i', name='G1a-dev (i): pendant taper into a trailing root cascade', gesture='G1 vertical trunk, ogive head, pendant taper', seed=1, spine4=sp, mask=MASK, maw=MAW,
                ribs=maw_ribs(MAW['c'], MAW['w'], MAW['h']), cords=dict(f=[-0.95, -0.78, -0.6, -0.42, -0.24, -0.06, 0.12, 0.30, 0.48, 0.66, 0.84, 0.97], t0=0.08, t1=0.93, r=8.0, lift=7.0), limbs=limbs, webs=webs)

def rope(x0, y0, x1, y1, bend, R0, name, n=2, seed=0.0, z0=22, steps=5, amp=0.04):
    """hanging strand from (x0,y0) to (x1,y1) with a lateral bow."""
    pts = []
    for i in range(steps + 1):
        u = i / steps; x = x0 + (x1 - x0) * u + bend * np.sin(np.pi * u) * (1 - 0.3 * u); y = y0 + (y1 - y0) * u
        pts.append((x, y, z0 + 30 * u))
    return hang(name, pts, R0, n, seed, amp)

def finish(id_, name, gesture, sp, limbs, webs, mask, maw, seed, cords=None, ribs=True):
    cf = cords or dict(f=[-0.95, -0.78, -0.6, -0.42, -0.24, -0.06, 0.12, 0.30, 0.48, 0.66, 0.84, 0.97], t0=0.08, t1=0.80, r=8.0, lift=7.0)
    return dict(id=id_, name=name, gesture=gesture, seed=seed, spine4=sp, mask=mask, maw=maw, ribs=maw_ribs(maw['c'], maw['w'], maw['h'], maw.get('tilt', 0.0)) if ribs else [], cords=cf, limbs=limbs, webs=webs)

def g1_ii():
    a1, a2, a3 = g1_common()
    sp = HEAD + [(-10, -150, 8, 124), (-8, -215, 8, 80), (-4, -260, 8, 30)]   # trunk ends ragged, dissolving
    rp = [rope(-70, -170, -150, -380, -18, 30, 'D1', 3, 0.5), rope(-30, -190, -60, -445, 14, 20, 'D2', 2, 1.6), rope(10, -200, 70, -410, -12, 24, 'D3', 2, 0.9),
          rope(50, -180, 160, -445, 20, 16, 'D4', 2, 2.0), rope(-100, -140, -230, -330, 22, 14, 'D5', 1, 0.7), rope(80, -150, 215, -330, 16, 14, 'D6', 1, 1.4),
          rope(-5, -230, -20, -315, 8, 12, 'D7', 1, 0.4, steps=4)]
    webs = [web_under_arm(a1, seed=1), web_under_arm(a2, seed=2, e_drop=260, drop=40), web_between(rp[0], rp[1], 0, 5, 0, 4, seed=3, cell=38), web_between(rp[1], rp[2], 0, 4, 0, 4, seed=5, cell=36), web_between(rp[2], rp[3], 0, 4, 0, 5, seed=4, cell=36), web_between(rp[0], rp[4], 0, 3, 0, 3, seed=6, cell=34), web_between(rp[3], rp[5], 0, 3, 0, 3, seed=7, cell=34)]
    return finish('G1a_ii', 'G1a-dev (ii): trunk dissolving into hanging strands (c01-like)', 'G1 vertical trunk, ogive head, dissolving hang', sp, [a1, a2, a3] + rp, webs, MASK, MAW, 2)

def g1_iii():
    a1, a2, a3 = g1_common()
    sp = HEAD + [(-22, -160, 8, 112), (-40, -225, 8, 82), (-46, -280, 8, 50)]
    big = hang('K1', [(-30, -170, 24), (20, -250, 32), (110, -310, 40), (210, -330, 50), (310, -380, 56), (385, -445, 58)], 58, 4, 1.8, 0.04)   # one heavy S-rope sweeps lower right
    veil = [rope(-55, -200, -120, -430, -14, 24, 'V1', 2, 0.5), rope(-70, -190, -205, -400, 24, 18, 'V2', 2, 0.9), rope(-60, -170, -270, -330, 22, 14, 'V3', 1, 0.6), rope(-45, -230, -70, -445, 10, 12, 'V4', 1, 0.3)]
    r2 = rope(70, -80, 190, -220, 14, 20, 'K2', 2, 1.2, steps=4)
    webs = [web_under_arm(a1, seed=1), web_under_arm(a2, seed=2, e_drop=260, drop=40), web_between(veil[0], veil[1], 0, 5, 0, 4, seed=3, cell=38), web_between(veil[1], veil[2], 0, 4, 0, 3, seed=4, cell=34), web_between(veil[3], veil[0], 0, 4, 0, 4, seed=6, cell=36), web_between(big, r2, 0, 3, 0, 3, seed=7, cell=40)]
    return finish('G1a_iii', 'G1a-dev (iii): off-centre root-knot, one heavy S-rope + hanging veil', 'G1 vertical trunk, ogive head, knot + veil', sp, [a1, a2, a3, big, r2] + veil, webs, MASK, MAW, 3)

def g2_dev():
    mask = dict(c=(215, 230), D=200, z=100, dz=26); maw = dict(c=(40, 28), w=200, h=300, tilt=-0.35)
    sp = [(336, 360, 44, 8), (290, 318, 50, 66), (250, 272, 48, 110), (215, 230, 40, 134), (150, 160, 30, 142), (80, 85, 22, 148), (10, 10, 14, 142), (-60, -70, 10, 122), (-120, -150, 8, 92),
          (-165, -235, 8, 66), (-185, -320, 8, 40), (-180, -390, 8, 22), (-165, -445, 8, 8)]
    a1 = arm('S1_UL', shelf(-320, 330, seed=7), (-20, 90), 52, seed=0.4); a2 = arm('S2_LR', shelf(345, -262, seed=8), (60, -70), 42, seed=1.5); a3 = arm('S3_ML', shelf(-340, -60, seed=9), (-80, -40), 38, seed=2.2)
    h1 = rope(-95, -120, -250, -420, -26, 36, 'H1', 3, 0.6); h2 = rope(-75, -150, -100, -440, 18, 22, 'H2', 2, 1.8); h3 = rope(-20, -90, 40, -300, 16, 18, 'H3', 2, 0.9, steps=4)
    webs = [web_under_arm(a1, seed=1), web_under_arm(a3, seed=2, e_drop=110), web_between(h1, h2, 0, 4, 0, 3, seed=3, cell=38)]
    return finish('G2a_dev', 'G2a-dev: diagonal emergence, ogive head upper right, pendant cascade', 'G2 diagonal C, head upper right, hanging tail', sp, [a1, a2, a3, h1, h2, h3], webs, mask, maw, 4)

def g4_dev():
    mask = dict(c=(-250, 235), D=200, z=100, dz=26); maw = dict(c=(-75, 28), w=200, h=300, tilt=-0.30)
    sp = [(-312, 396, 44, 8), (-282, 352, 50, 64), (-262, 300, 48, 106), (-250, 235, 40, 134), (-208, 130, 28, 132), (-122, 50, 20, 138), (-10, 5, 12, 134), (90, -70, 8, 116), (135, -170, 8, 92),
          (160, -260, 8, 64), (170, -340, 8, 38), (160, -400, 8, 20), (150, -446, 8, 8)]
    a1 = arm('S1_UR', shelf(315, 330, seed=13), (-20, 60), 52, seed=0.2); a2 = arm('S2_LL', shelf(-330, -300, seed=14), (-10, -80), 40, seed=1.1); a3 = arm('S3_R', shelf(330, -40, seed=15), (90, -10), 38, seed=2.0)
    h1 = rope(100, -150, 330, -420, 30, 34, 'H1', 3, 1.6); h2 = rope(60, -200, 30, -445, -16, 22, 'H2', 2, 0.5); h3 = rope(125, -110, 210, -300, -14, 16, 'H3', 1, 1.1, steps=4)
    webs = [web_under_arm(a1, seed=1), web_under_arm(a3, seed=2, e_drop=110), web_between(h2, h1, 0, 3, 0, 3, seed=3, cell=38)]
    return finish('G4a_dev', 'G4a-dev: sinuous S ribbon, ogive head upper left, hanging cascade lower right', 'G4 diagonal S ribbon, head upper-left, hanging tail', sp, [a1, a2, a3, h1, h2, h3], webs, mask, maw, 5)

for fn in (g1_i, g1_ii, g1_iii, g2_dev, g4_dev):
    st = fn(); S[st['id']] = st
STUDIES = S
