# Round-09 brainstorm diagrams. Flat shapes only. Run: python3 -I make_diagrams.py
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Polygon, Rectangle, Circle, FancyArrowPatch
import os
OUT = os.path.dirname(os.path.abspath(__file__))
WALL, LIMB, BODY, SHELF, MASK, MAW = "#1e1a17", "#a88458", "#7c5d3c", "#e2c58e", "#f1e8d2", "#0b0908"
PATH, GREEN = "#ff7a3d", "#5f8f4e"

def cr(pts, n=40):
    p = np.array(pts, float); p = np.vstack([2*p[0]-p[1], p, 2*p[-1]-p[-2]])
    out = []
    for i in range(1, len(p)-2):
        for t in np.linspace(0, 1, n, endpoint=False):
            a, b, c, d = p[i-1], p[i], p[i+1], p[i+2]
            out.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t**3))
    out.append(p[-2]); return np.array(out)

def tent(ax, pts, w0, w1, color=LIMB, z=2, ls="-", alpha=1):
    c = cr(pts); d = np.gradient(c, axis=0); nrm = np.stack([-d[:,1], d[:,0]], 1)
    nrm /= np.linalg.norm(nrm, axis=1, keepdims=True)+1e-9
    w = np.linspace(w0, w1, len(c))[:, None]/2
    poly = np.vstack([c+nrm*w, (c-nrm*w)[::-1]])
    ax.add_patch(Polygon(poly, closed=True, fc=color, ec="none" if ls=="-" else "#d8c8a8", ls=ls, lw=1, zorder=z, alpha=alpha))
    return c

def shelf(ax, x, y, w=15, plant=True):
    ax.add_patch(Rectangle((x-w/2, y-1.4), w, 2.8, fc=SHELF, ec="none", zorder=5))
    if plant:
        ax.add_patch(Rectangle((x-2, y+1.4), 4, 4, fc="#8a4f2e", ec="none", zorder=5))
        for dx in (-2.5, 0, 2.5): ax.add_patch(Ellipse((x+dx, y+8), 3, 6, fc=GREEN, ec="none", zorder=5))

def body(ax, cx, cy, s=1.0, tilt=0, maw_off=0):
    ax.add_patch(Ellipse((cx, cy), 30*s, 44*s, angle=tilt, fc=BODY, ec="none", zorder=3))
    ax.add_patch(Circle((cx+maw_off*.5, cy+14*s), 8.5*s, fc=MASK, ec="none", zorder=4))
    for dx in (-3, 3): ax.add_patch(Circle((cx+maw_off*.5+dx*s, cy+16*s), 1*s, fc="#333", zorder=4))
    t = np.linspace(-.8, .8, 20); ax.plot(cx+maw_off*.5+t*5.5*s, cy+12*s-2.2*s*(1-t**2)*-1*-1+ -0*t, color="#333", lw=1, zorder=4)
    ax.add_patch(Ellipse((cx+maw_off, cy-6*s), 9*s, 18*s, fc=MAW, ec="none", zorder=4))
    for k in range(5):
        yy = cy-6*s-6*s+k*3*s
        ax.add_patch(Polygon([[cx+maw_off-4.4*s,yy],[cx+maw_off-1.8*s,yy+.8*s],[cx+maw_off-4*s,yy+2*s]], fc=MASK, zorder=5))
        ax.add_patch(Polygon([[cx+maw_off+4.4*s,yy+1],[cx+maw_off+1.8*s,yy+1.6*s],[cx+maw_off+4*s,yy+2.6*s]], fc=MASK, zorder=5))
    # off-axis eye cluster (3 unequal globes)
    for (dx, dy, r) in ((-9.5, 3, 2.6), (-6.5, 6.5, 1.5), (-11.5, 8, 1.1)):
        ax.add_patch(Circle((cx+dx*s, cy+dy*s), r*s, fc="#d9d0a0", ec="#7a1d1d", lw=.8, zorder=5))

def path(ax, pts, color=PATH):
    c = cr(pts, 20)
    ax.plot(c[:,0], c[:,1], color=color, lw=2.2, ls=(0,(4,2.5)), zorder=9)
    ax.add_patch(FancyArrowPatch(c[-3], c[-1], arrowstyle="-|>", mutation_scale=16, color=color, zorder=9, lw=0))

def dots(ax, pts):
    for i, (x, y) in enumerate(pts, 1):
        ax.add_patch(Circle((x, y), 2.6, fc="#111", ec=PATH, lw=1.8, zorder=10))
        ax.text(x, y-.1, str(i), color="#fff", ha="center", va="center", fontsize=8, zorder=11, weight="bold")

def rest(ax, x, y, txt="rest"):
    ax.text(x, y, txt, color="#6d645a", ha="center", va="center", fontsize=9, style="italic", zorder=1)

def fig(name, title, sub):
    f, ax = plt.subplots(figsize=(6, 6.5), dpi=130); f.patch.set_facecolor("#111")
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(Rectangle((0,0),100,100, fc=WALL, ec="#555", lw=1.2, zorder=0))
    f.suptitle(title, color="#eee", fontsize=11, x=.5, y=.975, weight="bold")
    f.text(.5, .025, sub, color="#aaa", ha="center", fontsize=8)
    f.subplots_adjust(left=.03, right=.97, top=.93, bottom=.06); return f, ax

def save(f, name): f.savefig(os.path.join(OUT, name+".png")); plt.close(f)

# 1 single S-sweep
f, ax = fig("", "1  One serpentine limb through all three shelves", "orange = eye path   numbered = linger   italic = rest")
body(ax, 50, 62)
tent(ax, [(56,46),(74,46),(86,52),(82,38),(62,26),(36,20),(18,30),(10,52),(14,74)], 9, 2.5)
tent(ax, [(40,46),(32,40),(24,42),(22,36)], 5, 1.2); tent(ax, [(60,58),(70,70),(78,74),(80,68)], 4, 1.2)
shelf(ax, 85, 52, 14); shelf(ax, 33, 20, 14); shelf(ax, 14, 76, 14)
path(ax, [(50,66),(50,48),(70,46),(84,50),(80,38),(60,26),(34,20),(16,32),(10,52),(14,72)])
dots(ax, [(50,70),(50,54),(85,52),(33,21),(14,77)]); rest(ax, 60, 12); rest(ax, 28, 60)
save(f, "d1_s-sweep")

# 2 coil around supports
f, ax = fig("", "2  Each limb coils once around its shelf support", "orange = eye path   numbered = linger   italic = rest")
body(ax, 50, 58)
def coil(cx, y0, y1, r, turns, w0, w1):
    t = np.linspace(0, turns*2*np.pi, 14*int(turns)+6); ys = np.linspace(y0, y1, len(t))
    return [(cx+r*np.sin(a), y) for a, y in zip(t, ys)]
for (sx, sy, root, mid) in ((16,76,(38,60),[(28,70)]), (86,58,(64,52),[(76,56)]), (66,18,(54,38),[(62,30)])):
    ax.add_patch(Rectangle((sx-.8, sy-22), 1.6, 22, fc="#4a3a28", zorder=2))
    pts = [root]+mid+coil(sx, sy-20, sy-2, 3.2, 1.5, 0, 0)[::1]
    tent(ax, pts, 8, 2.2); shelf(ax, sx, sy, 15)
path(ax, [(50,66),(50,48),(36,60),(24,70),(16,72)]); dots(ax, [(50,70),(50,54),(16,77),(86,59),(66,19)])
ax.plot([50,70,80,86],[50,48,54,56], color=PATH, lw=2, ls=(0,(4,2.5)), zorder=9)
ax.plot([54,60,64,66],[44,34,28,22], color=PATH, lw=2, ls=(0,(4,2.5)), zorder=9)
rest(ax, 18, 30); rest(ax, 86, 22); rest(ax, 50, 90)
save(f, "d2_coil-support")

# 3 pinwheel
f, ax = fig("", "3  Pinwheel: three limbs curl one rotation, spiral reading", "orange = eye path   numbered = linger   italic = rest")
body(ax, 46, 56)
tent(ax, [(40,66),(30,80),(18,84),(12,78)], 9, 3); shelf(ax, 15, 80, 14)
tent(ax, [(60,60),(76,68),(86,62),(88,52)], 9, 3); shelf(ax, 86, 54, 14)
tent(ax, [(52,36),(60,22),(72,14),(80,18)], 9, 3); shelf(ax, 78, 20, 14)
tent(ax, [(40,38),(30,30),(24,22),(28,16),(34,18)], 5, 1.2)
path(ax, [(46,70),(46,54),(40,66),(28,82),(14,80),(40,70),(66,64),(84,58),(86,54),(76,30),(78,22)])
dots(ax, [(46,70),(46,54),(15,81),(86,55),(78,21)]); rest(ax, 24, 50); rest(ax, 70, 40)
save(f, "d3_pinwheel")

# 4 weight ladder
f, ax = fig("", "4  Weight ladder: massive / medium / whip", "orange = eye path   numbered = linger   italic = rest")
body(ax, 40, 58)
tent(ax, [(32,44),(22,30),(14,18),(20,10)], 16, 7); shelf(ax, 24, 12, 22)
tent(ax, [(54,52),(68,50),(82,44)], 8, 4.5); shelf(ax, 84, 46, 14)
tent(ax, [(50,70),(62,86),(78,92),(92,80),(94,66)], 3, .8); shelf(ax, 93, 66, 9, plant=False)
ax.add_patch(Rectangle((90,66),6,.1)); 
path(ax, [(40,70),(40,54),(30,38),(20,20),(24,13)]); dots(ax, [(40,70),(40,54),(24,13),(84,47),(93,67)])
ax.plot([48,66,82],[52,50,46], color=PATH, lw=2, ls=(0,(4,2.5)), zorder=9)
ax.plot([48,62,78,92,93],[72,86,92,80,68], color=PATH, lw=2, ls=(0,(4,2.5)), zorder=9)
rest(ax, 70, 24); rest(ax, 14, 62)
save(f, "d4_weight-ladder")

# 5 exit and re-enter
f, ax = fig("", "5  Limbs leave the body, dive off-frame or behind, re-enter", "orange = eye path   dashed limb = hidden/off-frame   numbered = linger")
body(ax, 52, 64)
tent(ax, [(40,56),(24,50),(8,44),(-4,40)], 9, 5)
tent(ax, [(-4,40),(-14,34)], 5, 4, ls="--", alpha=.35)
tent(ax, [(-4,20),(10,22),(22,28),(28,36)], 4, 8); shelf(ax, 12, 24, 15)
tent(ax, [(62,50),(74,42),(80,30),(78,14),(70,0),(70,-8)], 9, 5)
tent(ax, [(104,40),(94,44),(84,56),(80,62)], 4, 9); shelf(ax, 90, 46, 14)
tent(ax, [(48,-6),(46,6),(44,14)], 3, 8); shelf(ax, 44, 16, 14)
path(ax, [(52,68),(52,50),(30,50),(6,43)]); ax.plot([6,2],[43,34], color=PATH, lw=2, ls=(0,(1,3)), zorder=9)
ax.plot([2,8,12],[26,26,25], color=PATH, lw=2, ls=(0,(4,2.5)), zorder=9)
ax.plot([62,76,80,78,72],[50,42,30,14,0], color=PATH, lw=2, ls=(0,(4,2.5)), zorder=9)
ax.plot([100,92,88],[40,46,48], color=PATH, lw=2, ls=(0,(4,2.5)), zorder=9)
dots(ax, [(52,68),(52,54),(12,25),(90,47),(44,17)]); rest(ax, 56, 34)
ax.plot([70,60,50,45],[0,-2,2,12], color=PATH, lw=2, ls=(0,(1,3)), zorder=9)
save(f, "d5_exit-reenter")

# 6 asymmetric fan
f, ax = fig("", "6  Asymmetric fan: body on one side, bare wall as rest", "orange = eye path   numbered = linger   italic = rest")
body(ax, 26, 56, 1.1)
tent(ax, [(36,70),(54,82),(76,86),(90,82)], 9, 3); shelf(ax, 86, 84, 14)
tent(ax, [(40,56),(62,58),(80,56),(90,52)], 10, 3.5); shelf(ax, 88, 54, 14)
tent(ax, [(34,42),(50,28),(68,20),(82,20)], 10, 3); shelf(ax, 82, 22, 14)
tent(ax, [(24,36),(18,22),(22,10),(30,8)], 5, 1.5)
path(ax, [(26,70),(26,52),(44,58),(70,57),(86,54)]); dots(ax, [(26,71),(26,54),(86,55),(86,85),(82,23)])
ax.plot([30,50,72,84],[60,80,86,85], color=PATH, lw=2, ls=(0,(4,2.5)), zorder=9)
ax.plot([30,50,66,80],[48,30,22,22], color=PATH, lw=2, ls=(0,(4,2.5)), zorder=9)
rest(ax, 62, 70); rest(ax, 62, 38); rest(ax, 10, 88)
save(f, "d6_asym-fan")

# 7 hanging
f, ax = fig("", "7  Hanging: shelves cradled in the hooked ends of drooping limbs", "orange = eye path   numbered = linger   italic = rest")
body(ax, 50, 76, .95)
tent(ax, [(38,70),(24,62),(14,50),(14,38),(20,32),(26,36)], 9, 3); shelf(ax, 20, 40, 14)
tent(ax, [(50,56),(48,44),(50,30),(54,18),(60,14),(64,20)], 11, 3); shelf(ax, 56, 24, 14)
tent(ax, [(62,70),(78,64),(88,52),(88,40),(82,34),(76,38)], 9, 3); shelf(ax, 82, 44, 14)
tent(ax, [(44,56),(36,46),(34,34)], 4, 1)
path(ax, [(50,80),(50,66),(46,54),(48,40),(54,28)]); dots(ax, [(50,80),(50,66),(56,25),(20,41),(82,45)])
ax.plot([40,24,14,16,20],[68,62,50,42,40], color=PATH, lw=2, ls=(0,(4,2.5)), zorder=9)
ax.plot([62,78,88,86,82],[68,64,52,46,45], color=PATH, lw=2, ls=(0,(4,2.5)), zorder=9)
rest(ax, 50, 6); rest(ax, 70, 20); rest(ax, 32, 22)
save(f, "d7_hanging")

# 8 relay
f, ax = fig("", "8  Relay: limb to shelf 1, shelf lip hands off to limb 2, to shelf 3", "orange = eye path   numbered = linger   italic = rest")
body(ax, 62, 72, .9)
tent(ax, [(50,70),(36,76),(22,82),(14,78)], 9, 4); shelf(ax, 16, 80, 14)
tent(ax, [(10,78),(8,62),(14,50),(28,48),(40,50)], 6, 3)
tent(ax, [(40,50),(52,44),(58,34)], 3, 7)
shelf(ax, 30, 50, 14)
tent(ax, [(64,52),(74,44),(84,38),(88,28)], 8, 4); shelf(ax, 86, 36, 14)
tent(ax, [(40,50),(36,38),(40,26),(52,18),(66,18)], 5, 2)
path(ax, [(62,76),(62,56),(46,72),(24,82),(14,80),(8,64),(14,52),(28,50),(40,48),(52,44)]); dots(ax, [(62,78),(62,62),(16,81),(30,51),(86,37)])
ax.plot([62,76,86,86],[54,46,40,38], color=PATH, lw=2, ls=(0,(4,2.5)), zorder=9)
rest(ax, 66, 18); rest(ax, 26, 24)
save(f, "d8_relay")

# 9 reaching diagonal
f, ax = fig("", "9  Reach: body low in a corner, limbs climb a rising diagonal", "orange = eye path   numbered = linger   italic = rest")
body(ax, 30, 36, 1.15, tilt=-12)
tent(ax, [(22,52),(16,66),(20,80),(28,88)], 10, 3); shelf(ax, 24, 90, 14)
tent(ax, [(38,50),(50,60),(60,70),(70,72)], 10, 3); shelf(ax, 70, 72, 14)
tent(ax, [(44,36),(60,40),(76,46),(90,50)], 10, 3); shelf(ax, 88, 52, 14)
tent(ax, [(30,16),(36,6),(48,4),(56,10)], 6, 1.5)
path(ax, [(30,50),(30,36),(24,56),(18,72),(24,84)]); dots(ax, [(30,50),(30,36),(24,91),(70,73),(88,53)])
ax.plot([38,52,62,70],[50,60,70,72], color=PATH, lw=2, ls=(0,(4,2.5)), zorder=9)
ax.plot([46,62,78,88],[38,41,46,50], color=PATH, lw=2, ls=(0,(4,2.5)), zorder=9)
rest(ax, 76, 20); rest(ax, 8, 88); rest(ax, 52, 88)
save(f, "d9_reach")
