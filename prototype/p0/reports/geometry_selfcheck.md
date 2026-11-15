# geometry_selfcheck

ALL PASS: **True**

| check | value | pass |
|---|---|---|
| underlay.watertight_winding_volume>0 | {"wt": true, "wind": true, "vol": 1211391.9592229028} | PASS |
| skin.watertight_winding_volume>0 | {"wt": true, "wind": true, "vol": 494852.2166289116} | PASS |
| assembly.watertight_winding_volume>0 | {"wt": true, "wind": true, "vol": 1604590.8865593206} | PASS |
| skin_never_removes_underlay (vol U-A mm3) | -5.693 | PASS |
| skin_overlap_with_underlay mm3 (<= inset*envelope area = bond overlap only) | 1.017e+05 | PASS |
| skin_max_proud_mm (skin verts to underlay envelope, +-0.5 sampling tol) | 6.079 | PASS |
| shelf_120x120_top_z_range_mm (assembly) | 0.02212 | PASS |
| shelf_slope_deg | 0.01056 | PASS |
| shelf_top_plane_z | 84 | PASS |
| max_geometry_above_shelf_plane_in_footprint+margin_mm | 0 | PASS |
| protrusion_x_max_mm (assembly aabb, incl skin) | 357.4 | PASS |
| tip_centerline_x | 300.8 | PASS |
| centerline_rise_mm | 52 | PASS |
| span_arc3d_mm (plan arc = span_length) | 455.4 | PASS |
| seg0_fits_240mm_bed | [220.83, 210.36, 209.13] | PASS |
| seg1_fits_240mm_bed | [167.47, 159.67, 89.73] | PASS |
| seg2_fits_240mm_bed | [172.39, 160.0, 70.0] | PASS |
| segment_count>=2 | 3 | PASS |
| segments_union_volume_deficit_mm3 (holes+clearance) | 3284 | PASS |
| skin_swap_styles_never_alter_underlay | {"calcified_webbing": {"skin_vol": 491266.88388473727, "underlay_removed": -5.899320596434729, "underlay_bytes_equal": true}, "bone_crust": {"skin_vol": 551577. | PASS |
