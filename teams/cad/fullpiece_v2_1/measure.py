#!/usr/bin/env python3
"""Re-measure headroom + relief stats from a retained mesh npz (same definitions as gen_fullpiece.py).
Usage: python3 measure.py MESH.npz META.json  -> JSON on stdout.  Used to back-fill v1 (../fullpiece/engineering_checks.json)."""
import sys, json, numpy as np
HALF, SHELF_W = 457.0, 190.0


def measure(v, shelves):
    out = {'headroom': []}
    for sh in shelves:
        x0, x1 = sh['x_range']
        inb = (v[:, 0] > x0 + 2.5) & (v[:, 0] < x1 - 2.5) & (v[:, 2] < sh['p']) & (v[:, 1] > sh['top_y'] + 12.0) & (v[:, 1] < sh['top_y'] + 300.0)
        out['headroom'].append(dict(top_y=sh['top_y'], intruding_verts_above_12mm_lip=int(inb.sum()),
                                    clear_height_mm=round(float(v[inb, 1].min() - sh['top_y']), 1) if inb.any() else '>= 300 (none)'))
    G = np.zeros((229, 229)); gi = np.clip(((v[:, 0] + HALF) / 4.0).astype(int), 0, 228); gj = np.clip(((v[:, 1] + HALF) / 4.0).astype(int), 0, 228)
    np.maximum.at(G, (gi, gj), v[:, 2]); body = G > 5
    gx, gy = np.meshgrid(np.arange(229) * 4.0 - HALF, np.arange(229) * 4.0 - HALF, indexing='ij')
    for sh in shelves: body &= ~((np.abs(gx - (sh['x_range'][0] + sh['x_range'][1]) / 2) < SHELF_W / 2 + 6) & (gy > sh['top_y'] - 160) & (gy < sh['top_y'] + 12))
    Gb = G[body]
    out['relief_mm'] = dict(mean=round(float(Gb.mean()), 1), p10=round(float(np.percentile(Gb, 10)), 1), p50=round(float(np.percentile(Gb, 50)), 1),
                            p90=round(float(np.percentile(Gb, 90)), 1), std=round(float(Gb.std()), 1), max=round(float(Gb.max()), 1), covered_cells=int(body.sum()))
    return out


if __name__ == '__main__':
    v = np.load(sys.argv[1])['v'].astype(np.float64); meta = json.load(open(sys.argv[2]))
    print(json.dumps(measure(v, meta['shelves']), indent=1))
