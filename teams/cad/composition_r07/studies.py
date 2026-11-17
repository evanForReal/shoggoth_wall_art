"""Round-07 composition studies as FIGURE data (v2: trunk-bodied, per orchestrator read of G1a).
Coordinates mm: x right, y up, z out of the wall; envelope +-457. Body = ONE variable-radius sweep (head hood merges into a bulky trunk, NO neck pinch).
Limbs root at staggered heights on the trunk, differ in weight (r0), taper by tent_r. Shelf limbs pass under their plate (attach y = top-44), plate
carved flat on top, tail continues past the plate and lifts a little at the rim (cradle). Curls: <= 2 per study. G1a_neck = superseded first pass (kept in studies_v0_neck.py)."""
import numpy as np
S = {}
def shelf(cx, top, cz=105, a=118, b=100, seed=1): return dict(cx=cx, top=top, cz=cz, a=a, b=b, seed=seed)
def arm(name, sh, root, r0=52):
    """shelf arm: leaves the trunk at `root`, is LEVEL at the plate's inner edge (never above the plate top inside its footprint), passes under the plate, tail lifts at the rim."""
    cx, top = sh['cx'], sh['top']; ya = top - 44; sd = 1 if cx > root[0] else -1; ap = (cx - sd * 135, ya)
    sm = lambda u: u * u * (3 - 2 * u)
    p1 = (root[0] + 0.32 * (ap[0] - root[0]), root[1] + (ya - root[1]) * 0.15); p2 = (root[0] + 0.68 * (ap[0] - root[0]), root[1] + (ya - root[1]) * 0.75)
    return dict(name=name, r0=r0, shelf=sh, pts=[(root[0], root[1], 35), (p1[0], p1[1], 55), (p2[0], p2[1], 75), (ap[0], ap[1], 90), (cx, ya, 100)] + tail(cx, ya, sd))
def fl(name, pts, r0=50, r_tip=6.0): return dict(name=name, r0=r0, pts=pts, r_tip=r_tip)
def trunk(mx, end=120, head=138): return [(0, head), (0.18, 0.93 * mx), (0.45, mx), (0.75, 0.88 * mx), (1, end)]
def tail(cx, ytop_att, sg=1):   # standard shelf tail past the plate, gentle lift at the rim
    return [(cx + sg * 55, ytop_att, 108), (cx + sg * 95, ytop_att - 3, 112), (cx + sg * 113, ytop_att + 14, 112)]

# ---------------- G1 Descending Figure (c01-derived, trunk-bodied)
S['G1a'] = dict(id='G1a', name='G1a Descending Figure (c01-faithful): tall trunk + root column, head set into trunk top, 6 limbs staggered', gesture='G1 vertical trunk, slight S (head +8 mm)', seed=1,
  spine=[(8, 262, 15), (3, 150, 12), (-3, 20, 10), (0, -110, 8), (2, -250, 6)], spine_r=[(0, 138), (0.13, 172), (0.32, 184), (0.5, 170), (0.7, 124), (1, 100)],
  mask=dict(c=(8, 262), D=200, z=115, dz=28), maw=dict(c=(0, -20), w=200, h=300, orient='v'),
  limbs=[
   arm('S1_UL', shelf(-335, 285), (-105, 150)),
   arm('S2_UR', shelf(335, 150, seed=2), (70, 60)),
   arm('S3_LL', shelf(-335, -190, seed=3), (-70, -100)),
   fl('T1', [(-30, -250, 30), (-90, -320, 45), (-180, -380, 70), (-280, -415, 95), (-360, -445, 108), (-415, -440, 112)], r0=64),
   fl('T2', [(90, -120, 30), (190, -150, 45), (290, -170, 70), (380, -215, 95), (428, -290, 108), (430, -370, 112), (405, -430, 112)], r0=62),
   fl('T3', [(0, -200, 30), (50, -300, 45), (110, -370, 70), (200, -415, 92), (300, -440, 100), (380, -450, 106)], r0=46),
  ])
S['G1b'] = dict(id='G1b', name='G1b Descending Figure: head offset left, S-leaning trunk, shelves re-staggered', gesture='G1 S-trunk, head -85 mm', seed=2,
  spine=[(-62, 262, 15), (-48, 150, 12), (-20, 30, 10), (5, -110, 8)], spine_r=trunk(190, 120),
  mask=dict(c=(-62, 262), D=200, z=115, dz=28), maw=dict(c=(-8, -20), w=200, h=300, orient='v', tilt=0.10),
  limbs=[
   arm('S1_UR', shelf(330, 310, seed=4), (110, 150)),
   arm('S2_UL', shelf(-360, 135, seed=5), (-110, 60)),
   arm('S3_LR', shelf(335, -190, seed=6), (80, -120)),
   fl('T1', [(-60, -190, 30), (-120, -270, 45), (-190, -340, 70), (-280, -400, 95), (-360, -435, 108), (-410, -425, 112), (-425, -395, 110)], r0=60),
   fl('T2', [(10, -180, 30), (-20, -260, 45), (10, -340, 70), (90, -395, 90), (180, -420, 100), (270, -440, 106), (330, -445, 106)], r0=38),
   fl('T3', [(-150, -80, 30), (-230, -130, 50), (-310, -190, 75), (-390, -250, 95), (-440, -300, 105)], r0=40),
  ])

# ---------------- G2 Diagonal Emergence (head upper-right); heavy vs lean trunk
def g2(id_, heavy):
    mx = 186 if heavy else 150; end = 120 if heavy else 92
    return dict(id=id_, name=f'{id_} Diagonal Emergence: ' + ('heavy' if heavy else 'lean') + ' trunk', gesture='G2 diagonal C, head upper right', seed=3,
  spine=[(215, 230, 15), (130, 140, 12), (20, 20, 10), (-90, -100, 8)], spine_r=trunk(mx, end),
  mask=dict(c=(215, 230), D=200, z=115, dz=28), maw=dict(c=(40, 25), w=200, h=300, orient='v', tilt=-0.35),
  limbs=[
   arm('S1_UL', shelf(-320, 330, seed=7), (-30, 150)),
   arm('S2_LR', shelf(345, -290, seed=8), (90, -170)),
   arm('S3_ML', shelf(-340, -60, seed=9), (-60, -30)),
   fl('T1', [(-160, -190, 30), (-220, -270, 45), (-280, -340, 70), (-350, -400, 95), (-410, -440, 108), (-440, -420, 108)], r0=58),
   fl('T2', [(-110, -210, 30), (-100, -310, 45), (-50, -390, 70), (30, -440, 92), (100, -452, 100)], r0=40),
   fl('T3', [(-10, 170, 30), (-40, 280, 55), (-20, 380, 80), (60, 436, 95), (140, 446, 105)], r0=38),
  ])
S['G2a'] = g2('G2a', True); S['G2b'] = g2('G2b', False)

# ---------------- G3 Low Crouch: wide hunched trunk, limbs rising; maw vertical vs horizontal
def g3(id_, orient):
    horiz = orient == 'h'
    return dict(id=id_, name=f'{id_} Low Crouch: ' + ('horizontal' if horiz else 'vertical') + ' maw', gesture='G3 inverted-U arch, low heavy trunk', seed=4,
  spine=[(-45, 185, 15), (-35, 90, 12), (-10, -20, 10), (15, -150, 8)], spine_r=[(0, 134), (0.2, 168), (0.5, 192), (0.8, 170), (1, 120)],
  mask=dict(c=(-45, 185), D=200, z=115, dz=28),
  maw=dict(c=(0, -95) if horiz else (0, -100), w=200, h=300, orient=orient),
  limbs=[
   arm('S1_UL', shelf(-335, 305, seed=10), (-90, 100)),
   arm('S2_UR', shelf(335, 150, seed=11), (90, 40)),
   arm('S3_LR', shelf(335, -335, seed=12), (90, -190)),
   fl('H1', [(20, 90, 30), (110, 170, 45), (170, 250, 65), (190, 330, 85), (160, 400, 100), (100, 445, 110)], r0=50),
   fl('H2', [(-90, 90, 30), (-135, 170, 45), (-175, 250, 65), (-185, 330, 85), (-150, 400, 100), (-100, 445, 108)], r0=36),
   fl('T1', [(-160, -60, 30), (-250, -100, 45), (-340, -160, 70), (-420, -230, 95), (-450, -300, 108), (-425, -350, 110)], r0=62),
   fl('T2', [(-30, -170, 30), (-100, -260, 45), (-180, -340, 70), (-260, -400, 92), (-340, -440, 105)], r0=44),
   fl('T3', [(0, -190, 30), (30, -290, 45), (90, -370, 70), (180, -420, 95), (270, -445, 105), (340, -450, 106)], r0=36),
  ])
S['G3a'] = g3('G3a', 'v'); S['G3b'] = g3('G3b', 'h')

# ---------------- G4 Sinuous Spiral: S-ribbon trunk, head upper-left; fan of limbs (a) vs ribbon running through into a long lower-right tail (b)
SP4 = [(-250, 235, 15), (-208, 130, 12), (-122, 50, 10), (-10, 5, 10), (90, -70, 10), (135, -170, 8)]
R4 = [(0, 134), (0.15, 150), (0.40, 150), (0.65, 132), (0.85, 108), (1, 88)]
SP4B = SP4 + [(190, -262, 8), (280, -335, 6), (370, -372, 6), (430, -372, 6)]
R4B = [(0, 134), (0.10, 150), (0.28, 150), (0.43, 132), (0.55, 100), (0.72, 50), (0.9, 22), (1, 7)]
def g4(id_, ribbon_tail):
    L = [
   arm('S1_UR', shelf(315, 330, seed=13), (-20, 100)),
   arm('S2_LL', shelf(-330, -365, seed=14), (-20, -200)),
   arm('S3_R', shelf(330, -115, seed=15), (100, -95)),
   fl('F2', [(100, -230, 30), (70, -330, 45), (20, -410, 70), (-60, -448, 95), (-140, -452, 100)], r0=48),
   fl('W1', [(-40, 120, 30), (-10, 220, 45), (30, 320, 70), (70, 400, 92), (130, 440, 100)], r0=34),
    ]
    if ribbon_tail:
        L += [fl('F3', [(40, -150, 30), (-10, -260, 45), (-20, -340, 70), (30, -410, 90), (100, -445, 100)], r0=44)]
    else:
        L += [fl('F1', [(150, -200, 30), (215, -290, 45), (290, -365, 70), (370, -405, 95), (430, -385, 105), (435, -340, 108), (400, -325, 106)], r0=60)]
    return dict(id=id_, name=f'{id_} Sinuous Spiral: ' + ('ribbon runs through into a lower-right tail' if ribbon_tail else 'fan of limbs from the pelvis'), gesture='G4 diagonal S ribbon, head upper-left', seed=5,
  spine=SP4, spine_r=R4,
  mask=dict(c=(-250, 235), D=200, z=115, dz=28), maw=dict(c=(-75, 28), w=200, h=300, orient='v', tilt=-0.30), limbs=L)
S['G4a'] = g4('G4a', False)
import copy
S['G4b'] = copy.deepcopy(S['G4a']); S['G4b']['id'] = 'G4b'
S['G4b']['name'] = 'G4b Sinuous Spiral: lean ribbon (same limbs, body weight cut)'
S['G4b']['spine_r'] = [(0, 130), (0.15, 118), (0.40, 112), (0.65, 98), (0.85, 84), (1, 70)]

ORDER = {'G1a': ['S1_UL', 'S2_UR', 'S3_LL', 'T2', 'T1', 'T3'], 'G1b': ['S1_UR', 'S3_LR', 'S2_UL', 'T2', 'T3', 'T1'],
         'G2a': ['S2_LR', 'S1_UL', 'S3_ML', 'T1', 'T2', 'T3'], 'G2b': ['S2_LR', 'S1_UL', 'S3_ML', 'T1', 'T2', 'T3'],
         'G3a': ['S2_UR', 'S1_UL', 'S3_LR', 'T3', 'H1', 'T1', 'T2', 'H2'], 'G3b': ['S2_UR', 'S1_UL', 'S3_LR', 'T3', 'H1', 'T1', 'T2', 'H2'],
         'G4a': ['S1_UR', 'S2_LL', 'S3_R', 'F1', 'F2', 'W1'], 'G4b': ['S1_UR', 'S2_LL', 'S3_R', 'F1', 'F2', 'W1']}
def _post():
    for k, st in S.items():
        st['order'] = ORDER[k]
        for n_, L in enumerate([L for L in st['limbs'] if L.get('shelf')]): L['r0'] = [70, 58, 48][n_]
    for i, (k, st) in enumerate(S.items()):
        for j, L in enumerate(st['limbs']):
            p = np.array(L['pts'], float); ln = np.linalg.norm(np.diff(p[:, :2], axis=0), axis=1).sum()
            sg = 1 if (i + j) % 2 == 0 else -1
            L['wave'] = (sg * 0.07 * ln, 2.0, 0.0, 0.50 if L.get('shelf') else 0.85)
_post()
STUDIES = S
