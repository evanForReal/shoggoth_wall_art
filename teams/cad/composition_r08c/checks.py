#!/usr/bin/env python3
"""DESIGN_PRINCIPLES s.4 items #1-13 on one study. python3 -I checks.py ID [ID...] -> checks/<id>.json ; `--all` merges to checks.json
Geometry tests use the front-orthographic silhouette S (3 mm grid, from the SDF). Value tests use the 1200x900 front render + its binary mask png.
Items marked JUDGMENT carry a stated judgment with the proxies that support it."""
import sys, os, json
import numpy as np
from scipy import ndimage as ndi
from skimage import measure
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import XS, YS, RES, almond
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.join(HERE, 'build'); R = os.path.join(HERE, 'renders')
ENV = 914.0 ** 2; PX = RES ** 2; MMPX = 1.41 / 1200 * 1000    # render mm per pixel
X, Y = np.meshgrid(XS, YS, indexing='ij'); IN = (np.abs(X) <= 457) & (np.abs(Y) <= 457)

def area(m): return float(m.sum() * PX)
def idx(x, y): return int(round((x - XS[0]) / RES)), int(round((y - YS[0]) / RES))

def straight_runs(sil, tol=2.5, minlen=100):
    c = max(measure.find_contours(sil.astype(float), 0.5), key=len)
    pts = np.stack([c[:, 0] * RES + XS[0], c[:, 1] * RES + YS[0]], 1)
    seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]
    pts = np.stack([np.interp(np.arange(0, seg[-1], 3.0), seg, pts[:, k]) for k in (0, 1)], 1); n = len(pts); runs = []; i = 0
    while i < n - 1:
        j = i + 1; best = i + 1
        while j < n:
            a, b = pts[i], pts[j]; d = b - a; L = np.linalg.norm(d)
            if L < 1: j += 1; continue
            seg_pts = pts[i:j + 1]; u_ = d / L; q_ = seg_pts - a; dev = np.abs(u_[0] * q_[:, 1] - u_[1] * q_[:, 0]).max()
            if dev > tol: break
            best = j; j += 1
        L = np.linalg.norm(pts[best] - pts[i])
        if L >= minlen: runs.append((float(L), pts[i].tolist(), pts[best].tolist()))
        i = max(best, i + 1) if L >= minlen else i + 1
    return runs

def run(sid):
    meta = json.load(open(f'{B}/{sid}_meta.json')); sil = np.load(f'{B}/{sid}_sil.npy') & IN; body = np.load(f'{B}/{sid}_body.npy') & IN
    limbs = dict(np.load(f'{B}/{sid}_limbs.npz')); zmax = np.load(f'{B}/{sid}_zmax.npy')
    img = np.asarray(Image.open(f'{R}/study_{sid}_front.png').convert('L'), float); msk = np.asarray(Image.open(f'{R}/study_{sid}_mask.png')) > 0
    out = dict(id=sid, name=meta['name'], gesture=meta['gesture']); res = {}
    mk = meta['mask']; D = mk['D']; mcx, mcy = mk['c']
    # ------ geometry measures
    sil_area = area(sil); bb = np.argwhere(sil); bbox_area = (np.ptp(bb[:, 0]) + 1) * (np.ptp(bb[:, 1]) + 1) * PX
    limb_own = {}
    for L in meta['limbs']:
        m = limbs[L['name']] & IN & ~body; limb_own[L['name']] = area(m)
    body_area = area(body); big = max(limb_own.values())
    dt_body = ndi.distance_transform_edt(body) * RES
    sp = np.array(meta['spine']['pts']); from engine import curve
    c_sp, t_sp, L_sp = curve(sp, step=3.0)
    def dtv(c, dt): return np.array([dt[idx(p[0], p[1])] for p in c])
    w_sp = 2 * dtv(c_sp, dt_body); ih = int(np.argmin(np.linalg.norm(c_sp[:, :2] - np.array(meta['mask']['c']), axis=1))); head_w = w_sp[ih]; neck = w_sp[ih:int(0.45 * len(w_sp))].min()
    sh = w_sp[ih:int(0.75 * len(w_sp))].max()
    step_ok = bool(sh >= 1.15 * head_w)   # trunk-bodied: shoulders step out from the head hood; no neck pinch (orchestrator rule)
    # ---- #1 creature read (JUDGMENT + proxies)
    tips = np.array([L['c'][-1][:2] for L in meta['limbs']]); dmin = min(np.linalg.norm(tips[i] - tips[j]) for i in range(len(tips)) for j in range(i))
    res[1] = dict(pass_=bool(len(tips) >= 6 and dmin >= 40 and step_ok), kind='JUDGMENT', n_tips=len(tips), min_tip_gap_mm=round(dmin, 1),
                  note='head disc + shouldered torso + >=6 separable tapered tips; reads tentacled figure (octopus-person) in silhouette; shelves not needed to name it')
    # ---- #2
    bp = 100 * body_area / ENV
    res[2] = dict(pass_=bool(12 <= bp <= 20 and body_area >= 1.8 * big and step_ok), body_pct=round(bp, 2), body_vs_largest_limb=round(body_area / big, 2),
                  head_w=round(head_w), neck_w=round(neck), shoulder_w=round(sh), neck_step=bool(step_ok))
    # ---- #3
    ma = np.pi / 4 * D * D * mk['aspect']; mp = 100 * ma / ENV; ytop = (457 - mcy) / 914
    res[3] = dict(pass_=bool(2 <= mp <= 4 and 0.15 <= ytop <= 0.30), mask_pct=round(mp, 2), D=D, centre_y_from_top_H=round(ytop, 3), ring_or_crown=False)
    # ---- #4 (render)
    ex = lambda x, y: (600 + x / MMPX, 450 - y / MMPX)
    yy, xx = np.mgrid[0:img.shape[0], 0:img.shape[1]]; px, py = ex(mcx, mcy); rr = D / 2 / MMPX
    inm = ((xx - px) ** 2 + (yy - py) ** 2) < (0.96 * rr) ** 2; near = ((xx - px) ** 2 + (yy - py) ** 2) < (1.16 * rr) ** 2
    mlum = float(np.median(img[inm])); other = msk & ~near; top2 = float(np.percentile(img[other], 99.5)); omax = float(img[other].max())
    topl = (img >= 0.85 * mlum) & msk; frac_in = float((topl & near).sum() / max(topl.sum(), 1))
    lab, n = ndi.label((img >= 0.85 * mlum) & other); sizes = ndi.sum(np.ones_like(img), lab, range(1, n + 1)) if n else np.array([0])
    big_rival = float(sizes.max() * MMPX ** 2 / ENV * 100) if n else 0.0
    res[4] = dict(pass_=bool(frac_in >= 0.6 and big_rival <= 0.5 and mlum > omax), mask_median_lum=round(mlum, 1), brightest_nonmask_p99_5=round(top2, 1), brightest_nonmask_max=round(omax, 1),
                  margin_p99_5=round(mlum - top2, 1), margin_max=round(mlum - omax, 1), top_level_frac_in_mask=round(frac_in, 3), largest_rival_pct=round(big_rival, 3),
                  note='top level = lum >= 0.85 x mask median (image is mostly wall, so percentile V4 would not isolate the mask)')
    # ---- #5
    mw = meta['maw']; w_, h_ = mw['w'], mw['h']
    ad = almond(mw['c'][0], mw['c'][1], w_, h_, tilt=(np.pi / 2 if mw['orient'] == 'h' else 0) + (-0.0), seed={'G1a': 1, 'G1b': 2}.get(sid, 0))
    S_ = json.load(open(f'{B}/{sid}_meta.json'))
    import importlib; st = importlib.import_module('studies').STUDIES[sid]
    from engine import maw_sd; ad = maw_sd(st['maw'], st.get('seed', 0))
    open_ = ad(X, Y) < 0; maw_area = area(open_ & IN); ratio = maw_area / ma
    mpx, mpy = ex(*mw['c']); sx = (X[open_] - mw['c'][0]); 
    # render masks: opening pixels via projection of the opening footprint
    Xp = (600 + X / MMPX).astype(int); Yp = (450 - Y / MMPX).astype(int); okp = open_ & (Xp >= 0) & (Xp < 1200) & (Yp >= 0) & (Yp < 900)
    om = np.zeros(img.shape, bool); om[Yp[okp], Xp[okp]] = True; om = ndi.binary_closing(om, iterations=3)
    ring = ndi.binary_dilation(om, iterations=int(25 / MMPX)) & ~om & msk
    body_px = msk & ~near & ~ndi.binary_dilation(om, iterations=int(40 / MMPX))
    bmean = float(img[body_px].mean()); imean = float(img[om].mean()); rmean = float(img[ring].mean())
    sep = float(np.hypot(mcx - mw['c'][0], mcy - mw['c'][1]))
    res[5] = dict(pass_=bool((ratio <= 0.7 or ratio >= 1.3) and imean < bmean and rmean <= bmean * 1.0 and sep >= D), maw_to_mask_area=round(ratio, 2), maw_w=w_, maw_h=h_, orient=mw['orient'],
                  maw_interior_lum=round(imean, 1), rim_lum=round(rmean, 1), body_mean_lum=round(bmean, 1), centre_sep_mm=round(sep), mask_height=D)
    # ---- #6
    root = np.array(meta['spine']['pts'][-1][:2]); axis_x = 0
    nonshelf = [L for L in meta['limbs'] if not L['shelf']]; nshelf = sum(L['shelf'] for L in meta['limbs'])
    out_or_up = [L['name'] for L in nonshelf if (L['c'][-1][1] > L['c'][0][1] + 40) or abs(L['c'][-1][0]) >= 250]
    g64 = Image.fromarray((sil.T[::-1] * 255).astype(np.uint8)).resize((64, 64), Image.BOX)
    res[6] = dict(pass_=bool(len(meta['limbs']) >= 6 and nshelf == 3 and len(out_or_up) >= 2 and dmin >= 2 * 14.3), n_limbs=len(meta['limbs']), n_shelf=nshelf, outward_or_rising_free=out_or_up, min_tip_gap_mm=round(dmin, 1),
                  note='tips distinct at 64 px (14.3 mm/px) if gap >= 2 px = 28.6 mm')
    # ---- #7
    tp = {}; ok7 = True
    dt_all = ndi.distance_transform_edt(sil) * RES
    for L in meta['limbs']:
        c = np.array(L['c']); r = np.array(L['r']); t = np.array(L['t'])
        inb = np.array([body[idx(p[0], p[1])] for p in c]); k0 = int(np.argmax(~inb)) if (~inb).any() else 0
        w0 = 2 * r[k0]; k92 = int(np.argmin(np.abs(t - 0.97))); w92 = 2 * r[k92]; mono = bool(np.all(np.diff(r[k0:]) <= 0.10 * r[k0:-1] + 1e-6))
        vis_len = (len(c) - 1 - k0) * 8 * 1.5; tot = L['length']
        tp[L['name']] = dict(root_w=round(w0), tip_w=round(w92, 1), taper=round(w0 / w92, 1), len_mm=round(tot), len_over_W=round(tot / 914, 2), len_over_rootw=round(tot / w0, 1), monotone=mono)
        good = (w0 / w92 >= 5) and mono and (0.40 <= tot / 914 <= 0.65) and (12 <= w92 <= 25)
        tp[L['name']]['ok'] = bool(good); ok7 &= bool(good)
    res[7] = dict(pass_=ok7, limbs=tp, note='widths = designed section widths of the limb sweep alone (plate excluded); root = first sample outside the body silhouette; tip = t 0.97 (width must land in the 12-25 mm band); length range 0.40-0.65 W per checklist (feature-ref 6-10x root width is longer than the envelope allows)')
    # ---- #8
    feats = sorted([('body', body_area, None, None)] + [(L['name'], limb_own[L['name']], L['length'], L['shelf']) for L in meta['limbs']], key=lambda z_: -z_[1])
    top6 = feats[:6]; ratio12 = top6[0][1] / top6[1][1]; bad = []
    for i in range(1, 6):
        for j in range(i + 1, 6):
            q = top6[j][1] / top6[i][1]
            if 0.8 <= q <= 1.25:
                same = top6[i][3] == top6[j][3]; ld = abs(top6[i][2] / top6[j][2] - 1)
                if not (same and ld >= 0.15): bad.append((top6[i][0], top6[j][0], round(q, 2), round(ld, 2)))
    lens = sorted(L['length'] for L in meta['limbs']); mind = min(lens[i + 1] / lens[i] - 1 for i in range(len(lens) - 1))
    res[8] = dict(pass_=bool(ratio12 >= 2 and not bad), largest_over_second=round(ratio12, 2), top6=[(a_, round(b_ / 1e3, 1)) for a_, b_, _, _ in top6], rival_pairs=bad, min_adjacent_length_gap=round(mind, 3))
    # ---- #9 gesture
    lg = max(meta['limbs'], key=lambda L: L['length']); lc = np.array(lg['c'])
    g = np.vstack([sp[:, :3], lc[np.argmin(np.linalg.norm(lc[:, :2] - sp[-1, :2], axis=1)):, :3]]) if False else None
    cg, _, _ = curve(np.vstack([sp, lc[::2][:, :3]])[[0, 1, 2, 3, 4] + list(range(5, 5 + len(lc[::2])))], step=3.0) if False else (None, None, None)
    ds = np.full(body.shape, 1e9)
    mask_sp = np.zeros(body.shape, bool)
    for p in c_sp[::2]: mask_sp[idx(p[0], p[1])] = True
    dist_sp = ndi.distance_transform_edt(~mask_sp) * RES
    within = float((body & (dist_sp <= 0.5 * head_w)).sum() / body.sum())
    tang = np.gradient(c_sp[:, :2], axis=0); ang = np.unwrap(np.arctan2(tang[:, 1], tang[:, 0])); dang = np.gradient(ang)
    step_mm = 3.0; k100 = int(100 / step_mm); turn100 = max(abs(ang[i + k100] - ang[i]) for i in range(len(ang) - k100)) * 180 / np.pi
    sg = np.sign(np.gradient(ang)); infl = int(((sg[1:] * sg[:-1]) < 0).sum()) if np.abs(dang).max() > 1e-4 else 0
    dang_s = ndi.gaussian_filter1d(dang, 30); sgn = np.sign(dang_s[np.abs(dang_s) > 4e-4]); infl = int((sgn[1:] != sgn[:-1]).sum())
    res[9] = dict(pass_=bool(within >= 0.7 and turn100 <= 30 + 1e-6 and infl <= 2), body_mass_within_half_head_width=round(within, 3), max_turn_per_100mm_deg=round(turn100, 1), inflections=infl, named=meta['gesture'], spine_len_mm=round(L_sp))
    # ---- #10
    fill = 100 * sil_area / bbox_area
    from scipy.spatial import ConvexHull
    pts = np.argwhere(sil); hull = ConvexHull(pts); from matplotlib.path import Path
    gx, gy = np.meshgrid(np.arange(sil.shape[0]), np.arange(sil.shape[1]), indexing='ij')
    hm = Path(pts[hull.vertices]).contains_points(np.c_[gx.ravel(), gy.ravel()]).reshape(sil.shape); empty = hm & ~sil
    empty_ratio = float(empty.sum() / hm.sum())
    op = ndi.binary_opening(empty, structure=np.ones((17, 17)))     # cut necks < 34 mm
    lab, n = ndi.label(op); wedges = sorted([float(a_ * PX / ENV * 100) for a_ in ndi.sum(np.ones_like(op), lab, range(1, n + 1))], reverse=True) if n else []
    wed4 = [w for w in wedges if w >= 4.0]
    # limb gaps
    names = [L['name'] for L in meta['limbs']]; close = []
    for i, a_ in enumerate(meta['limbs']):
        for b_ in meta['limbs'][i + 1:]:
            ca, ra = np.array(a_['c']), np.array(a_['r']); cb, rb = np.array(b_['c']), np.array(b_['r'])
            from scipy.spatial import cKDTree
            d, ii = cKDTree(cb[:, :2]).query(ca[:, :2]); gap = d - ra - rb[ii]
            outside = np.array([not ndi.binary_dilation(body, iterations=12)[idx(p[0], p[1])] for p in ca])
            lenc = float(((gap < 60) & outside).sum() * 8 * 1.5)
            if lenc > 150: close.append((a_['name'], b_['name'], round(lenc)))
    res[10] = dict(pass_=bool(30 <= fill <= 45 and len(wed4) >= 3 and empty_ratio >= 0.25 and not close), fill_pct=round(fill, 1), wedges_ge4pct=[round(w, 1) for w in wed4], wedges_all=[round(w, 1) for w in wedges[:8]],
                   empty_hull_ratio=round(empty_ratio, 3), limb_pairs_closer_than_60mm_over_150mm=close)
    # ---- #11
    runs = straight_runs(sil); pl = meta['plates']; shelf_runs = []; other = []
    for Ln, p0, p1 in runs:
        ys_ = (p0[1] + p1[1]) / 2; isshelf = any(abs(ys_ - pp['top']) < 4 and abs(p0[1] - p1[1]) < 4 for pp in pl)
        (shelf_runs if isshelf else other).append(round(Ln))
    res[11] = dict(pass_=bool(max(other + [0]) <= 120), longest_nonshelf_run_mm=max(other + [0]), shelf_top_runs_mm=shelf_runs, all_runs_ge100=[round(r_[0]) for r_ in runs],
                   note='shelf-top runs are the spec flat top (>=150 mm): inherent conflict with the 120 mm rule, listed apart; JUDGMENT: plate corners R26, plan outline wobbled superellipse, no posts, shelf is the tangent flare of the limb tail')
    # ---- #12
    tops = [(pp['cx'], pp['top']) for pp in pl]; ys_ = sorted(t[1] for t in tops)
    tri = abs((tops[1][0] - tops[0][0]) * (tops[2][1] - tops[0][1]) - (tops[2][0] - tops[0][0]) * (tops[1][1] - tops[0][1])) / 2
    hr = {}
    Fz = None
    # headroom from zmax map is projection-only; need volume: use the saved field via rebuild-free proxy: nearest solid above in the z-columns of the plate footprint
    vol = np.load(f'{B}/{sid}_solid.npy', mmap_mode='r') if os.path.exists(f'{B}/{sid}_solid.npy') else None
    for pp in pl:
        a_, b_ = pp['a'] - 18, pp['b'] - 18
        i0, i1 = idx(pp['cx'] - a_, 0)[0], idx(pp['cx'] + a_, 0)[0]; j0 = idx(0, pp['top'] + 4)[1]; j1 = min(idx(0, pp['top'] + 300)[1], len(YS) - 1)
        k0 = int((pp['cz'] - b_ + 9) // RES); k1 = int((pp['cz'] + b_ + 9) // RES)
        sub = np.asarray(vol[i0:i1 + 1, j0:j1 + 1, k0:k1 + 1]); col_any = sub.any(axis=(0, 2))
        h = 300.0 if not col_any.any() else float(np.argmax(col_any) * RES + 4)
        jt = idx(0, pp['top'])[1]; flat = np.asarray(vol[i0:i1 + 1, jt - 2:jt + 3, k0:k1 + 1]).any(axis=(0, 2))   # plate present at top level
        zero_dev = float(max(0, np.ptp([ (np.argwhere(np.asarray(vol[ii, jt - 6:jt + 6, kk]))[:, 0].max() if np.asarray(vol[ii, jt - 6:jt + 6, kk]).any() else 0) for ii in range(i0, i1 + 1, 6) for kk in range(k0, k1 + 1, 6)]) * RES))
        hr[pp['limb']] = dict(top_flatness_mm=round(zero_dev, 1), top_y=pp['top'], flat_top_mm=(round(2 * a_), round(2 * b_)), clear_above_mm=round(h), ok=bool(h >= 299))
    per = all(abs(t[0]) >= 183 or abs(t[1]) >= 183 for t in tops)
    res[12] = dict(pass_=bool(tri > 20000 and all(ys_[i + 1] - ys_[i] >= 120 for i in range(2)) and ys_[-1] > 152 and per and all(v_['ok'] for v_ in hr.values())), triangle_area_mm2=round(tri), top_ys=ys_,
                   min_height_gap=round(min(ys_[i + 1] - ys_[i] for i in range(2))), highest_in_upper_third=bool(ys_[-1] > 152), periphery=bool(per), headroom=hr)
    # ---- #13 (S weighted by render luminance)
    wlum = (img / 255.0) * msk; yy2, xx2 = np.mgrid[0:img.shape[0], 0:img.shape[1]]
    cxm = (wlum * (xx2 - 600) * MMPX).sum() / wlum.sum(); cym = (wlum * (450 - yy2) * MMPX).sum() / wlum.sum()
    L_ = wlum[:, :600].sum(); R_ = wlum[:, 600:].sum(); lr = max(L_, R_) / min(L_, R_)
    sa = (sil & IN); flip = sa[::-1, :]; iou = float((sa & flip).sum() / (sa | flip).sum())
    vfrac = (457 - cym) / 914
    res[13] = dict(pass_=bool(abs(cxm) <= 0.08 * 914 and 0.40 <= vfrac <= 0.55 and 1.1 <= lr <= 1.5 and iou < 0.85), centroid_x_mm=round(cxm), centroid_y_from_top_H=round(vfrac, 3), LR_weight_ratio=round(lr, 2), mirror_iou=round(iou, 3))
    out['checks'] = {str(k): v for k, v in res.items()}
    out['passed'] = [k for k, v in res.items() if v['pass_']]; out['failed'] = [k for k, v in res.items() if not v['pass_']]
    out['score'] = f"{len(out['passed'])}/13"
    # wall luminance
    out['wall_luminance_pct'] = round(float(img[~msk].mean()) / 255 * 100, 1); out['flesh_luminance_pct'] = round(float(img[msk & ~near & ~ndi.binary_dilation(om, iterations=int(40 / MMPX))].mean()) / 255 * 100, 1)
    out['mask_luminance_pct'] = round(mlum / 255 * 100, 1); out['maw_luminance_pct'] = round(imean / 255 * 100, 1)
    os.makedirs(f'{HERE}/checks', exist_ok=True); json.dump(out, open(f'{HERE}/checks/{sid}.json', 'w'), indent=1)
    return out

if __name__ == '__main__':
    for s in sys.argv[1:]:
        o = run(s); print(s, o['score'], 'FAIL', o['failed'])
