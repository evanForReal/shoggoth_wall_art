"""Silhouette connectivity, holes, wedges, limb tips, balance, straight runs. Source: orthographic front silhouette of build/H.npz (+ mask disc),
1.5 mm/px, 640 grid, envelope = 914 mm square = 609 px."""
from common import *
from skimage.morphology import skeletonize, disk, opening, convex_hull_image
from scipy.ndimage import label, binary_fill_holes
S = 1.5; N = 640; c = N/2; ENV = 914/S; ENV_AREA = ENV*ENV
sil = np.load(os.path.join(OUT, "mesh_sil.npy"))
yy, xx = np.mgrid[0:N, 0:N]
# mask disc: centre (-32, 248) mm, r 100 mm (README s.1)
disc = ((xx-(c-32/S))**2 + (yy-(c-248/S))**2) <= (100/S)**2
sil = sil | disc
res = dict(px_mm=S, env_px=ENV)
res["fill_ratio_geometric"] = float(sil.sum()/ENV_AREA)      # composition_gate r11 value (its own mask) = 0.4395
lab, n = label(sil, structure=np.ones((3, 3)))
sizes = np.bincount(lab.ravel())[1:]
order = np.argsort(sizes)[::-1]
res["components_total"] = int(n)
res["components_ge_0p05pct_env"] = int((sizes >= 0.0005*ENV_AREA).sum())
res["components_ge_0p5pct_env"] = int((sizes >= 0.005*ENV_AREA).sum())
res["largest_component_share"] = float(sizes.max()/sizes.sum())
isl = [int(s) for s in sorted(sizes, reverse=True)[1:8]]
res["island_areas_px_top7"] = isl
res["island_areas_mm2_top7"] = [round(s*S*S) for s in isl]
# holes (enclosed wall): largest component only
big = lab == (order[0]+1)
filled = binary_fill_holes(big)
holes = filled & ~big
hl, hn = label(holes)
hs = np.sort(np.bincount(hl.ravel())[1:])[::-1]
res["holes_n"] = int(hn); res["holes_ge_0p5pct_env"] = int((hs >= 0.005*ENV_AREA).sum())
res["holes_area_share_of_filled"] = float(holes.sum()/filled.sum())
res["holes_top8_mm2"] = [round(int(s)*S*S) for s in hs[:8]]
# hull & wedges
hull = convex_hull_image(sil)
neg = hull & ~sil
nl, nn = label(neg)
ns = np.bincount(nl.ravel())[1:]
# open-to-outside: touches hull boundary band
from scipy.ndimage import binary_erosion
band = hull & ~binary_erosion(hull, iterations=3)
open_ids = set(np.unique(nl[band & neg])) - {0}
wedges = [(i, int(ns[i-1])) for i in open_ids if ns[i-1] >= 0.02*ENV_AREA]
res["hull_solidity"] = float(sil.sum()/hull.sum())
res["neg_in_hull_ratio"] = float(neg.sum()/hull.sum())
res["wedges_ge_2pct_open"] = len(wedges)
res["wedges_ge_4pct_open"] = int(sum(1 for _, a in wedges if a >= 0.04*ENV_AREA))
res["wedge_areas_pct_env"] = sorted([round(a/ENV_AREA*100, 1) for _, a in wedges], reverse=True)
# balance
ys, xs = np.nonzero(sil)
cx = (xs.mean()-c)*S; cy = (c-ys.mean())*S
res["centroid_mm"] = [float(cx), float(cy)]
res["centroid_x_pct_of_envelope"] = float(cx/914*100)
res["centroid_y_from_top_pct"] = float((457 - cy)/914*100)   # envelope y +-457
L = sil[:, :int(c)].sum(); R = sil[:, int(c):].sum()
res["LR_area_ratio"] = float(max(L, R)/min(L, R)); res["heavier_side"] = "L" if L > R else "R"
res["mirror_iou"] = float((sil & sil[:, ::-1]).sum()/(sil | sil[:, ::-1]).sum())
# torso blob (gate-style opening r = 12% of envelope)
op = opening(filled, disk(int(0.12*ENV)))
tl, tn = label(op); ts = np.bincount(tl.ravel())[1:]; tb = tl == (np.argmax(ts)+1)
yb, xb = np.nonzero(tb)
res["torso_blob_width_frac"] = float((xb.max()-xb.min()+1)/ENV); res["torso_blob_area_frac"] = float(tb.sum()/ENV_AREA)
# part decomposition: residual after removing the opened body at r=4% env (36 mm): limbs/shelves
op2 = opening(filled, disk(int(0.04*ENV)))
resid = filled & ~ndi.binary_dilation(op2, iterations=2)
rl, rn = label(resid); rs = np.sort(np.bincount(rl.ravel())[1:])[::-1]
res["feature_areas_pct_env_top8_body_first"] = [round(op2.sum()/ENV_AREA*100, 1)] + [round(x/ENV_AREA*100, 2) for x in rs[:7]]
# straight horizontal runs on the silhouette top boundary
topb = sil & ~np.roll(sil, 1, axis=0)
best = []
for r in range(N):
    row = topb[r]; run = 0; mx = 0
    for v in row:
        run = run+1 if v else 0; mx = max(mx, run)
    best.append(mx)
best = np.array(best)
runs = []
used = np.zeros(N, bool)
for r in np.argsort(best)[::-1]:
    if best[r] < 20: break
    if used[max(0, r-6):r+7].any(): continue
    used[r] = True; runs.append((int(r), int(best[r]), round(best[r]*S)))
res["straight_horizontal_runs_(row, px, mm)"] = runs[:6]
# skeleton endpoints = limb tips; inward tangent vs bearing to the mask centre / maw
sk = skeletonize(opening(filled, disk(int(0.015*ENV))))
nb = ndi.convolve(sk.astype(int), np.ones((3, 3), int), mode="constant") - 1
ends = np.argwhere(sk & (nb == 1))
MASKC = np.array([c-248/S, c-32/S]); MAWC = np.array([c+30/S*-1, c+0])  # (y, x); maw centre ~ (x 20 mm, y -30mm) approx
MAWC = np.array([c-(-30)/S, c+(20)/S])
def walk(p, steps):
    path = [tuple(p)]; seen = {tuple(p)}
    cur = tuple(p)
    for _ in range(steps):
        nxt = None
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                q = (cur[0]+dy, cur[1]+dx)
                if q in seen or not (0 <= q[0] < N and 0 <= q[1] < N): continue
                if sk[q]: nxt = q; break
            if nxt: break
        if not nxt: break
        seen.add(nxt); path.append(nxt); cur = nxt
    return np.array(path)
tips = []
for e in ends:
    p = walk(e, 50)
    if len(p) < 30: continue         # spur < 45 mm
    t_in = p[-1] - p[0]; t_in = t_in/np.linalg.norm(t_in)          # points from tip inward
    for nm, tgt in (("mask", MASKC), ("maw", MAWC)):
        pass
    to_m = MASKC - e; to_m /= np.linalg.norm(to_m)
    ang = float(np.degrees(np.arccos(np.clip(t_in @ to_m, -1, 1))))
    tips.append(dict(tip_mm=[round((e[1]-c)*S), round((c-e[0])*S)], len_px=len(p), inward_vs_mask_bearing_deg=round(ang, 1),
                     dist_to_mask_mm=round(float(np.linalg.norm(MASKC-e)*S))))
res["limb_tips_n"] = len(tips); res["limb_tips"] = tips
dump("d4_silhouette.json", res)
print(json.dumps({k: v for k, v in res.items() if k != "limb_tips"}, indent=1))
for t in tips: print(t)
# figure: silhouette, holes, wedges, skeleton, tips
rgb = np.zeros((N, N, 3), np.uint8); rgb[sil] = (200, 200, 200)
rgb[disc & sil] = (250, 235, 190)
rgb[holes] = (200, 60, 60)
for i, a in wedges: rgb[nl == i] = (50, 80, 160)
rgb[sk] = (255, 220, 0)
for t in tips:
    x = int(t["tip_mm"][0]/S + c); y = int(c - t["tip_mm"][1]/S)
    rgb[max(0, y-4):y+5, max(0, x-4):x+5] = (0, 255, 120)
im = Image.fromarray(rgb)
from PIL import ImageDraw
ImageDraw.Draw(im).text((8, 4), "grey=geometric silhouette (mesh+disc) | red=enclosed holes | blue=open wedges >=2% | yellow=skeleton | green=tips", fill=(255, 255, 255))
print("kb", save(im, "d4_silhouette_map.png"))
