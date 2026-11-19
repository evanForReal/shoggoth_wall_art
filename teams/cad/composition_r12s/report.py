#!/usr/bin/env python3
"""per-variant limits table from arm_report_<p>.json + measure_extra_<p>.json (+ rest diff vs r11 H) -> report_<p>.json, report_<p>.md.  python3 report.py p1|p2"""
import os, sys, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); p = sys.argv[1]
arm = json.load(open(f'{HERE}/arm_report_{p}.json')); ex = json.load(open(f'{HERE}/measure_extra_{p}.json')); out = {}
H11 = np.load(f'{HERE}/../composition_r11/build/H_rest.npy')
for sid, r in arm.items():
    meta = json.load(open(f'{HERE}/build/{sid}_meta.json')); g = meta['held_geo']; b = r['ball']; m = r['P6_mask_mass_calc']; sh = ex[sid]['shelves']
    row = dict(id=sid, grip=b['grip'], ball_D_mm=b['D_mm'], ball_depth_mm=b['depth_mm'], depth_over_D=round(b['depth_over_D'], 2), ball_front_z_mm=b['front_z_mm'], ball_back_lowest_z_mm=b['back_lowest_z_mm'], relief_max_z_mm=ex[sid]['max_z_mm'],
               gap_ball_back_to_flesh_peak_mm=r['gap_mask_back_to_flesh_mm'], ball_min_dist_to_rest_of_piece_mm=round(r['P12_mask_part_min_dist_to_rest_of_piece_mm'], 1), mass_kg=r['P6_mask_mass_kg'], mass_basis=m['basis'], V_total_STL_cm3=m['V_total_STL_mesh_cm3'],
               lever_mm=round(r['P5_horizontal_lever_exit_axis_to_CoM_mm'], 1), com_offset_mm=round(r['P5_CoM_offset_from_rod_axis_mm'], 1), tilt_deg=round(r['P5_total_tilt_deg'], 1), core_dia_min_mm=round(r['P7_core_min_diameter_free_span_mm'], 1), cover_min_mm=round(r['P1_radial_cover_free_span_min_mm'], 1),
               free_span_clear_mm_r11def=round(r['P12_arm_free_span_min_dist_to_rest_mm_beyond_45mm_of_exit'], 1), free_span_clear_mm_along_axis=round(r['P12_arm_free_span_min_dist_to_rest_mm_beyond_45mm_ALONG_AXIS'], 1),
               pad_dia_mm=r['P4_pad_dia_mm'], pad_depth_mm=r['P4_pad_depth_along_axis_mm'] + 14, rod_to_seat_normal_deg=round(r['P13_rod_to_seat_normal_deg'], 1), rod_to_mask_axis_deg=round(r['rod_to_mask_axis_en_deg'], 1), arm_part_z_mm=r['arm_part_z_range_mm'], thread_bore_to_pad_wall_mm=r.get('thread_bore_to_pad_min_wall_mm'),
               root_exit=[round(x, 1) for x in g['Rx']], boss_used=g.get('boss_used'), shelves={k: [v['flat_top_x_mm'], v['flat_top_z_mm'], v['clear_above_flat_mm']] for k, v in sh.items()}, shelves_ok=all(v['ok'] for v in sh.values()),
               rest_diff_vs_r11_H_cm3=round(float((np.load(f'{HERE}/build/{sid}_rest.npy') ^ H11).sum() * 8 / 1e3), 1) if sid in ('S1', 'S2', 'S3') else None,
               limits=dict(relief=r['max_z_mm'] <= 300, mass=r['P6_mask_mass_kg'] <= 0.8, lever=r['P5_horizontal_lever_exit_axis_to_CoM_mm'] <= 250, com=r['P5_CoM_offset_from_rod_axis_mm'] <= 50, tilt=r['P5_total_tilt_deg'] <= 35, core=r['P7_core_min_diameter_free_span_mm'] >= 22, cover=r['P1_radial_cover_free_span_min_mm'] >= 5,
                           clear=r['P12_arm_free_span_min_dist_to_rest_mm_beyond_45mm_of_exit'] >= 6, seat=r['P13_rod_to_seat_normal_deg'] <= 35, pad=r['P4_pad_dia_mm'] >= 70, shelves=all(v['ok'] for v in sh.values())),
               sources=dict(arm=f'measure_arm.py -> arm_report_{p}.json', shelves_relief=f'measure_extra.py -> measure_extra_{p}.json', geometry=f'build/{sid}_meta.json', mask_mesh=f'build/{sid}_maskpart.stl (trimesh volume)'))
    row['pass_all'] = all(row['limits'].values()); out[sid] = row
json.dump(out, open(f'{HERE}/report_{p}.json', 'w'), indent=1)
cols = ['id', 'ball_D_mm', 'ball_depth_mm', 'relief_max_z_mm', 'mass_kg', 'lever_mm', 'com_offset_mm', 'tilt_deg', 'rod_to_seat_normal_deg', 'free_span_clear_mm_r11def', 'ball_min_dist_to_rest_of_piece_mm', 'arm_part_z_mm', 'pass_all']
with open(f'{HERE}/report_{p}.md', 'w') as fh:
    fh.write('| ' + ' | '.join(cols) + ' |\n|' + '---|' * len(cols) + '\n')
    for r in out.values(): fh.write('| ' + ' | '.join(str(r[c]) for c in cols) + ' |\n')
print(open(f'{HERE}/report_{p}.md').read()); print({k: v['limits'] for k, v in out.items() if not v['pass_all']})
