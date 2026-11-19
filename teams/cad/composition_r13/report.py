#!/usr/bin/env python3
"""r13 limits table from arm_report_<id>.json + measure_extra_<id>.json + gap_reach.json + part bounding boxes -> report.json, report.md. python3 report.py"""
import os, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); B = f'{HERE}/build'; out = {}
gr = json.load(open(f'{HERE}/gap_reach.json'))
def bbox(path, X0):
    a = np.load(path, mmap_mode='r'); ii = np.argwhere(np.asarray(a.any(axis=(1, 2)))); jj = np.argwhere(np.asarray(a.any(axis=(0, 2)))); kk = np.argwhere(np.asarray(a.any(axis=(0, 1))))
    return [round(float((ii.max() - ii.min() + 1) * 2)), round(float((jj.max() - jj.min() + 1) * 2)), round(float((kk.max() - kk.min() + 1) * 2))]
for sid, X0 in (('H13', -468.0), ('E1', -612.0)):
    r = json.load(open(f'{HERE}/arm_report_{sid}.json'))[sid]; ex = json.load(open(f'{HERE}/measure_extra_{sid}.json'))[sid]; meta = json.load(open(f'{B}/{sid}_meta.json')); g = meta['held_geo']; sh = ex['shelves']; b = r['ball']; m = r['P6_mask_mass_calc']
    sil = np.load(f'{B}/{sid}_sil.npy', mmap_mode='r'); ii = np.argwhere(np.asarray(sil.any(1))); jj = np.argwhere(np.asarray(sil.any(0)))
    row = dict(id=sid, body_scale=meta['scale'], bbox_x_mm=[round(float(X0 + ii.min() * 2)), round(float(X0 + ii.max() * 2))], bbox_y_mm=[round(float(X0 + jj.min() * 2)), round(float(X0 + jj.max() * 2))], overall_w_h_mm=[round(float((ii.max() - ii.min() + 1) * 2)), round(float((jj.max() - jj.min() + 1) * 2))],
               ball_D_mm=b['D_mm'], ball_depth_mm=b['depth_mm'], ball_front_z_mm=b['front_z_mm'], relief_max_z_mm=ex['max_z_mm'], mass_kg=r['P6_mask_mass_kg'], lever_mm=round(r['P5_horizontal_lever_exit_axis_to_CoM_mm'], 1), com_offset_mm=round(r['P5_CoM_offset_from_rod_axis_mm'], 1), tilt_deg=round(r['P5_total_tilt_deg'], 1),
               core_dia_min_mm=round(r['P7_core_min_diameter_free_span_mm'], 1), cover_min_mm=round(r['P1_radial_cover_free_span_min_mm'], 1), free_span_clear_mm=round(r['P12_arm_free_span_min_dist_to_rest_mm_beyond_45mm_of_exit'], 1), pad_dia_mm=r['P4_pad_dia_mm'], pad_depth_mm=r['P4_pad_depth_along_axis_mm'] + 14,
               rod_to_seat_normal_deg=round(r['P13_rod_to_seat_normal_deg'], 1), ball_to_rest_mm=round(r['P12_mask_part_min_dist_to_rest_of_piece_mm'], 1), gap_ball_back_to_flesh_mm=r['gap_mask_back_to_flesh_mm'], root_exit=[round(float(x), 1) for x in g['Rx']],
               arm_part_xyz_mm=bbox(f'{B}/{sid}_armpart.npy', X0), arm_part_z_range_mm=r['arm_part_z_range_mm'], mask_part_xyz_mm=bbox(f'{B}/{sid}_maskpart.npy', X0),
               shelves={k: dict(flat_x=v['flat_top_x_mm'], flat_z=v['flat_top_z_mm'], clear_above=v['clear_above_flat_mm']) for k, v in sh.items()}, whip=meta['whip'], gaps=gr[sid]['gaps'] if sid in gr else gr['H13' if sid == 'H13' else 'E1']['gaps'], reach=gr[sid]['reach'])
    row['limits'] = dict(relief=row['relief_max_z_mm'] <= 300, shelves=all(v['ok'] for v in sh.values()), lever=row['lever_mm'] <= 250, com=row['com_offset_mm'] <= 50, tilt=row['tilt_deg'] <= 35, mass=row['mass_kg'] <= 0.8, core=row['core_dia_min_mm'] >= 22, cover=row['cover_min_mm'] >= 5,
                         clear=row['free_span_clear_mm'] >= 6, pad=row['pad_dia_mm'] >= 70 and row['pad_depth_mm'] >= 30, seat=row['rod_to_seat_normal_deg'] <= 35, arm_part_z_bed=row['arm_part_xyz_mm'][2] <= 256, mask_part_bed=max(row['mask_part_xyz_mm']) <= 256)
    row['pass_all'] = all(row['limits'].values()); out[sid] = row; print(sid, row['pass_all'], {k: v for k, v in row['limits'].items() if not v})
    print({k: row[k] for k in ('overall_w_h_mm', 'relief_max_z_mm', 'mass_kg', 'lever_mm', 'com_offset_mm', 'tilt_deg', 'core_dia_min_mm', 'cover_min_mm', 'free_span_clear_mm', 'rod_to_seat_normal_deg', 'arm_part_xyz_mm', 'mask_part_xyz_mm', 'ball_front_z_mm')})
json.dump(out, open(f'{HERE}/report.json', 'w'), indent=1)
