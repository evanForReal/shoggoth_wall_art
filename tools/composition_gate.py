#!/usr/bin/env python3
"""Objective composition gate (Aesthetics; computed by a non-CAD agent).

Usage:  python3 -I tools/composition_gate.py <render.png> <mask.png> [--ref c01_metrics.json]
        render and mask must be pixel-aligned (same size). mask: white = creature only.
Output: JSON on stdout: metrics, per-metric PASS/FAIL vs bands, overall verdict. Exit 0 = PASS, 1 = FAIL.
Method, definitions, bands: teams/aesthetics/analysis/composition_gate/README.md
All geometry is done on the creature's bounding square (the "envelope"), resampled to N x N.
"""
import sys, os, json, argparse
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.morphology import skeletonize, disk, convex_hull_image, opening

N = 512                      # envelope resolution
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_REF = os.path.join(HERE, '..', 'teams', 'aesthetics', 'analysis', 'composition_gate', 'c01_metrics.json')

# parameters (fractions of envelope side N). [GENERAL] = chosen, not derived.
P = dict(
    wedge_min_area=0.02,     # [GENERAL] wedge = background component inside convex hull, area >= 2% of envelope
    torso_open_r=0.12,       # [GENERAL] opening disk radius 12% of envelope (6% spec value leaves c01 limbs attached: width 0.87; see README)
    skel_open=0.015,         # [GENERAL] mask opened with disk r=1.5% N before skeletonising (kills drips/fringe thinner than ~3% N)
    spur_prune=0.05,         # [GENERAL] skeleton spurs shorter than 5% N removed
    limb_min_len=0.08,       # [GENERAL] limb = skeleton branch >= 8% N ...
    limb_beyond=0.05,        # [GENERAL] ... whose tip is >= 5% N outside the torso blob
    head_blur=0.015,         # blur sigma, fraction of envelope (DESIGN s.8 recipe)
    head_frac=0.85,          # head blob = connected region >= 85% of max blurred luma inside mask
    ring_out=0.08,           # flesh ring = mask pixels within 8% N of head blob
)

# ---------------------------------------------------------------- io / geometry
def load(render_path, mask_path):
    r = Image.open(render_path).convert('RGB')
    m = Image.open(mask_path).convert('L')
    if m.size != r.size:
        m = m.resize(r.size, Image.NEAREST)
    return np.asarray(r).astype(float) / 255.0, np.asarray(m) > 127

def envelope(mask):
    """bbox -> centred square; returns (N x N bool mask, (x0,y0,side) square box in source px)."""
    ys, xs = np.where(mask)
    if len(ys) == 0:
        raise SystemExit('empty mask')
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    side = max(x1 - x0, y1 - y0)
    bx = x0 - (side - (x1 - x0)) // 2
    by = y0 - (side - (y1 - y0)) // 2
    pad = np.zeros((side, side), bool)
    sx0, sy0 = max(bx, 0), max(by, 0)
    sx1, sy1 = min(bx + side, mask.shape[1]), min(by + side, mask.shape[0])
    pad[sy0 - by:sy1 - by, sx0 - bx:sx1 - bx] = mask[sy0:sy1, sx0:sx1]
    sq = Image.fromarray((pad * 255).astype(np.uint8)).resize((N, N), Image.LANCZOS)
    return np.asarray(sq) > 127, (bx, by, side)

def luma(rgb):
    return 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]

# ---------------------------------------------------------------- skeleton
def _nbrs(sk):
    k = np.ones((3, 3), int); k[1, 1] = 0
    return ndi.convolve(sk.astype(int), k, mode='constant') * sk

def prune(sk, min_len, passes=6):
    sk = sk.copy()
    for _ in range(passes):
        nb = _nbrs(sk)
        ends = list(zip(*np.where((nb == 1) & sk)))
        removed = False
        for (y, x) in ends:
            path = [(y, x)]; prev = None; cur = (y, x); length = 0.0; hit = False
            while True:
                cy, cx = cur
                nxt = [(cy + dy, cx + dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                       if (dy or dx) and 0 <= cy + dy < sk.shape[0] and 0 <= cx + dx < sk.shape[1]
                       and sk[cy + dy, cx + dx] and (cy + dy, cx + dx) != prev and (cy + dy, cx + dx) not in path]
                if len(nxt) != 1:
                    hit = len(nxt) >= 2 or len(nxt) == 0 and False
                    break
                n = nxt[0]
                length += np.hypot(n[0] - cy, n[1] - cx)
                if nb[n] >= 3:
                    hit = True; break
                prev = cur; cur = n; path.append(n)
            if hit and length < min_len:
                for p in path:
                    sk[p] = False
                removed = True
        if not removed:
            break
        sk = skeletonize(sk)
    return sk

def branch_lengths(sk):
    """for each endpoint: (y, x, length to first junction)."""
    nb = _nbrs(sk); out = []
    for (y, x) in zip(*np.where((nb == 1) & sk)):
        path = [(y, x)]; cur = (y, x); length = 0.0
        while True:
            cy, cx = cur
            nxt = [(cy + dy, cx + dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                   if (dy or dx) and 0 <= cy + dy < sk.shape[0] and 0 <= cx + dx < sk.shape[1]
                   and sk[cy + dy, cx + dx] and (cy + dy, cx + dx) not in path]
            if len(nxt) != 1:
                break
            n = nxt[0]; length += np.hypot(n[0] - cy, n[1] - cx)
            if nb[n] >= 3:
                break
            cur = n; path.append(n)
        out.append((int(y), int(x), float(length)))
    return out

# ---------------------------------------------------------------- metrics
def torso_blob(sq):
    filled = ndi.binary_fill_holes(sq)
    op = opening(filled, disk(int(round(P['torso_open_r'] * N))))
    lab, n = ndi.label(op)
    if n == 0:
        return np.zeros_like(sq), filled
    sizes = ndi.sum(op, lab, range(1, n + 1))
    return lab == (1 + int(np.argmax(sizes))), filled

def geometry_metrics(sq):
    d = {}
    area = sq.sum()
    d['fill_ratio'] = float(area / N**2)
    hull = convex_hull_image(sq)
    bg = hull & ~sq
    lab, n = ndi.label(bg)
    amin = P['wedge_min_area'] * N**2
    areas = sorted([int(a) for a in ndi.sum(bg, lab, range(1, n + 1))], reverse=True) if n else []
    d['wedge_count'] = int(sum(a >= amin for a in areas))
    d['wedge_areas_frac'] = [round(a / N**2, 4) for a in areas[:8]]
    d['empty_hull_ratio'] = float(bg.sum() / max(hull.sum(), 1))
    torso, filled = torso_blob(sq)
    ys, xs = np.where(torso)
    if len(ys):
        tw = (xs.max() + 1 - xs.min()) / N
        th = (ys.max() + 1 - ys.min()) / N
        cy, cx = ys.mean(), xs.mean()
    else:
        tw = th = 0.0; cy = cx = N / 2
    d['torso_width_frac'] = float(tw)
    d['torso_height_frac'] = float(th)
    d['torso_area_frac'] = float(torso.sum() / N**2)
    # skeleton / limbs
    smooth = opening(filled, disk(int(round(P['skel_open'] * N))))
    lab_s, n_s = ndi.label(smooth)
    if n_s > 1:
        smooth = lab_s == (1 + int(np.argmax(ndi.sum(smooth, lab_s, range(1, n_s + 1)))))
    sk = prune(skeletonize(smooth), P['spur_prune'] * N)
    dist_to_torso = ndi.distance_transform_edt(~torso)
    limbs = []
    for (y, x, L) in branch_lengths(sk):
        if L >= P['limb_min_len'] * N and dist_to_torso[y, x] >= P['limb_beyond'] * N:
            limbs.append(dict(tip=[x / N, y / N], branch_len=L / N, reach=float(dist_to_torso[y, x] / N)))
    d['limb_count'] = len(limbs)
    tsize = max(tw, 1e-6)
    d['limb_reach_ratio'] = float(np.mean([l['reach'] for l in limbs]) / tsize) if limbs else 0.0
    d['limb_reach_max_ratio'] = float(max([l['reach'] for l in limbs], default=0) / tsize)
    d['_limbs'] = limbs
    d['_skeleton'] = sk
    d['_torso'] = torso
    return d

def head_metrics(rgb, mask, box):
    """head = brightest blurred-luma blob inside mask. returns contrast vs flesh ring + diagnostics vs wall."""
    L = luma(rgb)
    bx, by, side = box
    sig = P['head_blur'] * side
    Lb = ndi.gaussian_filter(L, sig)
    inner = ndi.binary_erosion(mask, iterations=max(1, int(0.005 * side)))
    if not inner.any():
        inner = mask
    Lm = np.where(inner, Lb, -1)
    py, px = np.unravel_index(np.argmax(Lm), Lm.shape)
    cand = (Lb >= P['head_frac'] * Lm[py, px]) & inner
    lab, _ = ndi.label(cand)
    head = lab == lab[py, px]
    head = ndi.binary_fill_holes(head)
    head &= mask
    ring_zone = ndi.distance_transform_edt(~head) <= P['ring_out'] * side
    ring = mask & ring_zone & ~ndi.binary_dilation(head, iterations=max(1, int(0.01 * side)))
    wall_zone = (ndi.distance_transform_edt(~mask) > 0.03 * side) & (ndi.distance_transform_edt(~mask) <= 0.10 * side)
    h_L = float(np.median(L[head])); r_L = float(np.median(L[ring])) if ring.any() else float('nan')
    w_L = float(np.median(L[wall_zone])) if wall_zone.any() else float('nan')
    ys, xs = np.where(head)
    ymin = np.where(mask)[0].min()
    return dict(head_luma=h_L, flesh_ring_luma=r_L, wall_luma=w_L,
                head_vs_flesh=h_L / max(r_L, 1e-3), head_vs_wall=h_L / max(w_L, 1e-3),
                head_area_frac=float(head.sum() / max(mask.sum(), 1)),
                head_centre_xy=[float((xs.mean() - bx) / side), float((ys.mean() - by) / side)])

def iou_vs(sq, ref_sq):
    inter = (sq & ref_sq).sum(); uni = (sq | ref_sq).sum()
    return float(inter / max(uni, 1))

def compute(render_path, mask_path, ref_mask=None):
    rgb, mask = load(render_path, mask_path)
    sq, box = envelope(mask)
    g = geometry_metrics(sq)
    h = head_metrics(rgb, mask, box)
    m = dict(fill_ratio=g['fill_ratio'], wedge_count=g['wedge_count'], torso_width_frac=g['torso_width_frac'],
             limb_reach_ratio=g['limb_reach_ratio'], limb_count=g['limb_count'], head_vs_flesh=h['head_vs_flesh'])
    if ref_mask is not None:
        m['iou_vs_c01'] = iou_vs(sq, ref_mask)
    diag = {k: v for k, v in g.items() if not k.startswith('_') and k not in m}
    diag.update({k: v for k, v in h.items() if k != 'head_vs_flesh'})
    diag['limbs'] = g['_limbs']
    diag['envelope_box_xy_side'] = [int(v) for v in box]
    return m, diag, sq, g

# ---------------------------------------------------------------- gate
def judge(m, ref):
    res = {}
    for k, b in ref['bands'].items():
        if k not in m:
            continue
        v = m[k]
        ok = (b['lo'] <= v <= b['hi'])
        res[k] = dict(value=round(v, 4) if isinstance(v, float) else v, lo=b['lo'], hi=b['hi'], verdict='PASS' if ok else 'FAIL')
    return res

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('render'); ap.add_argument('mask')
    ap.add_argument('--ref', default=DEFAULT_REF)
    ap.add_argument('--no-diag', action='store_true')
    a = ap.parse_args()
    ref = json.load(open(a.ref))
    refmask = None
    rp = os.path.join(os.path.dirname(os.path.abspath(a.ref)), ref.get('ref_mask_envelope', ''))
    if ref.get('ref_mask_envelope') and os.path.exists(rp):
        refmask = np.asarray(Image.open(rp).convert('L').resize((N, N), Image.NEAREST)) > 127
    m, diag, sq, g = compute(a.render, a.mask, refmask)
    res = judge(m, ref)
    fails = [k for k, v in res.items() if v['verdict'] == 'FAIL']
    geo_fails = [k for k in fails if k != 'iou_vs_c01']
    out = dict(render=a.render, mask=a.mask, ref=a.ref, metrics=res, failed=fails,
               verdict='PASS' if not fails else 'FAIL', n_pass=len(res) - len(fails), n_total=len(res),
               verdict_excl_iou='PASS' if not geo_fails else 'FAIL')  # IoU is a c01-family check; alt-gesture studies: read this line
    wl = diag.get('wall_luma')
    if wl is not None and wl > 0.15:
        out['warnings'] = [f'wall luminance {wl:.2f} > 0.15 (DESIGN_PRINCIPLES s.0): head contrast under-reported; render against wall <= 15%']
    if not a.no_diag:
        out['diagnostics'] = diag
    print(json.dumps(out, indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o)))
    sys.exit(0 if not fails else 1)

if __name__ == '__main__':
    main()
