#!/usr/bin/env python3
"""Field-based min-wall measurement (skeleton + EDT) and clamp pass, plus through-void (6 mm) rule.

Measures the voxel FIELD (occ = F > 0, pre-meshing), not the marching-cubes mesh.

Usage:
  python3 minwall.py DIR                 measure only  -> DIR/minwall_before.json
  python3 minwall.py DIR --clamp         measure, clamp thin skeleton, re-measure, mesh
                                         -> DIR/minwall_after.json, DIR/raw_mesh_clamped.npz, DIR/F_clamped.npy
Thickness estimate at a skeleton voxel: t = 2*EDT - vox/2 (EDT to nearest empty voxel centre);
true thickness lies in [2*EDT - vox, 2*EDT]. A feature counts as thin when t < THIN_MM.
"""
import sys, os, json, argparse, time
import numpy as np
from scipy import ndimage as ndi
from skimage.morphology import skeletonize

TARGET_MM = 2.0
THIN_MM = 1.75        # 2.0 mm minus ~half a voxel of quantisation slack
CLAMP_R = 1.1         # mm ball radius stamped on thin skeleton voxels (2.2 mm wide)
VOID_RULE_MM = 6.0
FILL_MM = 6.0         # projection voids with inscribed diameter below this are closed by a plug
PLUG_T = 2.6          # plug thickness on the back plane (blind pocket floor)
MIN_COMP = 25         # thin-ridge components smaller than this many voxels are tip/corner noise


def skeleton_regions(occ, ys, y_lo=-102.0, y_hi=-28.0, zsplit=44.0, zs0=0.25, vox=0.5):
    """Skeletonise in two crops (web slab z<zsplit; shelf block above) to bound time and memory."""
    skel = np.zeros_like(occ)
    kz = int(round((zsplit - zs0) / vox))
    t0 = time.time()
    skel[:, :, :kz] = skeletonize(occ[:, :, :kz])
    print('  skeleton A', round(time.time() - t0, 1), flush=True)
    if occ.shape[2] > kz:
        j0 = max(0, int(round((y_lo - ys[0]) / vox))); j1 = min(occ.shape[1], int(round((y_hi - ys[0]) / vox)))
        if j1 > j0:
            skel[:, j0:j1, kz:] = skeletonize(occ[:, j0:j1, kz:])
    print('  skeleton B', round(time.time() - t0, 1), flush=True)
    return skel


def void_stats(occ, vox):
    cov = occ.any(axis=2)
    void = ~cov
    lab, n = ndi.label(void)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    edt = ndi.distance_transform_edt(void, sampling=vox)
    idx = np.arange(1, n + 1)
    mx = ndi.maximum(edt, lab, idx); ar = ndi.sum(void, lab, idx) * vox * vox
    interior = ~np.isin(idx, edge)
    D = 2 * mx[interior] - vox / 2; A = ar[interior]
    bins = [0, 2, 6, 10, 20, 40, 1e9]
    hist = np.histogram(D, bins)[0].tolist()
    return dict(interior_voids=int(interior.sum()), inscribed_diam_bins_mm='<2,2-6,6-10,10-20,20-40,>40', counts=hist,
                n_below_6mm=int((D < VOID_RULE_MM).sum()), n_ge_6mm=int((D >= VOID_RULE_MM).sum()),
                area_frac_below_6mm=round(float(A[D < VOID_RULE_MM].sum() / max(A.sum(), 1e-9)), 4),
                total_interior_void_area_cm2=round(float(A.sum()) / 100, 1),
                median_inscribed_diam_mm=round(float(np.median(D)), 1) if len(D) else None,
                mean_equiv_diam_mm=round(float(np.mean(np.sqrt(4 * A / np.pi))), 1) if len(A) else None,
                note='voids = z-projection gaps not touching the array border; ragged-silhouette notches that open to the exterior are excluded')


def measure(occ, vox, ys):
    t0 = time.time()
    edt = ndi.distance_transform_edt(occ, sampling=vox).astype(np.float32)
    print('  edt', round(time.time() - t0, 1), flush=True)
    skel = skeleton_regions(occ, ys, vox=vox)
    est = 2 * edt[skel] - vox / 2
    res = dict(vox=vox, skeleton_voxels=int(skel.sum()),
               thickness_p1_mm=round(float(np.percentile(est, 1)), 2), thickness_p5_mm=round(float(np.percentile(est, 5)), 2),
               thickness_p25_mm=round(float(np.percentile(est, 25)), 2), thickness_p50_mm=round(float(np.percentile(est, 50)), 2),
               thickness_p95_mm=round(float(np.percentile(est, 95)), 2),
               frac_below_thin=round(float((est < THIN_MM).mean()), 4), frac_below_1p25=round(float((est < 1.25).mean()), 4),
               thin_mm=THIN_MM)
    # medial ridge (sheet-capable medial axis): local maxima of EDT
    ridge = (edt == ndi.maximum_filter(edt, size=3)) & occ
    est_r = 2 * edt[ridge] - vox / 2
    thin_r = ridge & (2 * edt - vox / 2 < THIN_MM)
    lab, n = ndi.label(thin_r, structure=np.ones((3, 3, 3)))
    if n:
        sizes = ndi.sum(thin_r, lab, np.arange(1, n + 1))
        keep = np.isin(lab, 1 + np.flatnonzero(sizes >= MIN_COMP))
    else:
        keep = thin_r
    res['ridge'] = dict(samples=int(ridge.sum()), p1=round(float(np.percentile(est_r, 1)), 2), p5=round(float(np.percentile(est_r, 5)), 2),
                        p50=round(float(np.percentile(est_r, 50)), 2), frac_below_thin=round(float((est_r < THIN_MM).mean()), 4),
                        thin_components=int(n), thin_components_ge_min=int((sizes >= MIN_COMP).sum()) if n else 0,
                        thin_voxels_in_kept_components=int(keep.sum()))
    del lab
    # thickness histogram (strand width distribution)
    res['width_hist_mm'] = dict(zip(['<1.5', '1.5-2', '2-3', '3-4', '4-6', '6-8', '>8'],
                                    np.histogram(est, [0, 1.5, 2, 3, 4, 6, 8, 1e9])[0].tolist()))
    # residue of a 2.0 mm opening (volume in features < 2 mm), tips/corners included
    er = edt > 1.0 - 1e-3
    op = ndi.distance_transform_edt(~er, sampling=vox) <= 1.0 + 1e-3
    res['opening_2mm_volume_retained_frac'] = round(float((op & occ).sum() / occ.sum()), 4)
    res['voids'] = void_stats(occ, vox)
    # location of thin skeleton
    thin = np.zeros_like(occ); thin[skel] = (est < THIN_MM)
    thin |= keep
    res['thin_skeleton_voxels'] = int(thin.sum())
    return res, edt, thin


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('dir'); ap.add_argument('--clamp', action='store_true'); ap.add_argument('--fill', action='store_true', help='close projection voids smaller than FILL_SLIVER_MM with a back plug')
    a = ap.parse_args()
    g = json.load(open(os.path.join(a.dir, 'grid.json'))); vox = g['vox']
    occ = np.load(os.path.join(a.dir, 'occ.npy'))
    ys = g['y0'] + vox * np.arange(occ.shape[1])
    print('measure before', flush=True)
    before, edt, thin = measure(occ, vox, ys)
    json.dump(before, open(os.path.join(a.dir, 'minwall_before.json'), 'w'), indent=1)
    print(json.dumps({k: v for k, v in before.items() if k not in ('voids', 'width_hist_mm')}, indent=1))
    if a.clamp:
        F = np.load(os.path.join(a.dir, 'F.npy')).astype(np.float32)
        if thin.any():
            D = ndi.distance_transform_edt(~thin, sampling=vox).astype(np.float32)
            F = np.maximum(F, CLAMP_R - D)
            del D
        fillinfo = None
        if a.fill:
            vox_ = vox; zs_ = g['z0'] + vox * np.arange(F.shape[2])
            occ_t = F > 0
            void = ~occ_t.any(axis=2)
            lab, n = ndi.label(void)
            edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
            edt2 = ndi.distance_transform_edt(void, sampling=vox)
            idx = np.arange(1, n + 1)
            mx = ndi.maximum(edt2, lab, idx); ar = ndi.sum(void, lab, idx) * vox * vox
            Dv = 2 * mx - vox / 2
            small = (~np.isin(idx, edge)) & (Dv < FILL_MM)
            mask = ndi.binary_dilation(np.isin(lab, idx[small]), iterations=1)
            kp = int(np.searchsorted(zs_, PLUG_T)) + 2
            ine = ndi.distance_transform_edt(mask, sampling=vox).astype(np.float32)
            plug = np.minimum(PLUG_T - zs_[None, None, :kp], (ine + 0.5 * vox)[:, :, None])
            plug = np.where(mask[:, :, None], plug, -9.0)
            F[:, :, :kp] = np.maximum(F[:, :, :kp], plug.astype(np.float32))
            fillinfo = dict(voids_filled=int(small.sum()), projected_area_filled_cm2=round(float(ar[small].sum()) / 100, 2),
                            plug_thickness_mm=PLUG_T, rule_mm=FILL_MM)
            del plug, ine, edt2
        np.save(os.path.join(a.dir, 'F_clamped.npy'), F.astype(np.float16))
        occ2 = F > 0
        added = int(occ2.sum() - occ.sum())
        np.save(os.path.join(a.dir, 'occ_clamped.npy'), occ2)
        print('measure after', flush=True)
        after, _, _ = measure(occ2, vox, ys)
        after['fill'] = fillinfo
        after['voxels_added'] = added; after['volume_added_cm3'] = round(added * vox ** 3 / 1000, 2)
        json.dump(after, open(os.path.join(a.dir, 'minwall_after.json'), 'w'), indent=1)
        print(json.dumps({k: v for k, v in after.items() if k not in ('voids', 'width_hist_mm')}, indent=1))
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from gen_patch import mesh_from_field
        xs = g['x0'] + vox * np.arange(occ.shape[0]); zs = g['z0'] + vox * np.arange(occ.shape[2])
        v, f = mesh_from_field(F, xs, ys, zs, vox)
        np.savez(os.path.join(a.dir, 'raw_mesh_clamped.npz'), v=v.astype(np.float32), f=f.astype(np.uint32))
        print('meshed', v.shape, f.shape)
