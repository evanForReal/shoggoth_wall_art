# geometry_selfcheck

ALL PASS: **True**

| check | value | pass |
|---|---|---|
| underlay.watertight_winding_volume>0_single_component | {"wt": true, "wind": true, "vol": 1235216.7300442692, "components": [[116596, 1235216.73]]} | PASS |
| skin.watertight_winding_volume>0_single_component | {"wt": true, "wind": true, "vol": 488328.49278577295, "components": [[350478, 488328.49]]} | PASS |
| assembly.watertight_winding_volume>0_single_component | {"wt": true, "wind": true, "vol": 1622604.7395751153, "components": [[249404, 1622604.74]]} | PASS |
| skin_never_removes_underlay (vol U-A mm3) | 0.3828 | PASS |
| skin_overlap_with_underlay mm3 (<= 1.05*inset*underlay_surface_area) | {"overlap": 100940.52404538155, "bound": 371599.1386716737, "ratio": 0.27163820779080844} | PASS |
| skin_max_proud_mm (skin verts to underlay envelope, +0.5 sampling tol) | 6.045 | PASS |
| shelf_120x120_top_z_range_mm (assembly) | 0.02212 | PASS |
| shelf_slope_deg | 0.01056 | PASS |
| shelf_top_plane_z | 84 | PASS |
| max_geometry_above_shelf_plane_over_T+-95xN+-80_mm (>=40 mm keepout margin: 160 mm pot clears) | 0 | PASS |
| protrusion_x_max_mm (assembly aabb, incl skin) | 357.9 | PASS |
| tip_centerline_x | 300.8 | PASS |
| centerline_rise_mm | 52 | PASS |
| span_arc3d_mm (plan arc = span_length) | 455.4 | PASS |
| seg0_fits_240mm_bed_single_component | {"ext": [220.83, 210.36, 209.13], "components": 1} | PASS |
| seg1_fits_240mm_bed_single_component | {"ext": [167.6, 159.61, 89.74], "components": 1} | PASS |
| seg2_fits_240mm_bed_single_component | {"ext": [172.39, 160.0, 70.0], "components": 1} | PASS |
| segment_count>=2 | 3 | PASS |
| segments_union_volume_deficit_mm3 (holes+clearance) | 3280 | PASS |
| vent_holes (d>=3 mm, >=2 per sealed chamber, listed in manifest) | {"n": 6, "d": [4.0], "stations": [72.0, 216.0, 368.0]} | PASS |
| min_wall_normal_dir_mm (ray-cast, underlay; fail < 2.3; edge-filtered) | {"n_samples": 50000, "n_valid": 47120, "n_filtered": 34994, "raw_min_mm": 2.302567793854109, "raw_pct_lt_2p3": 0.0, "min_mm": 2.381676077219845, "p0p1_mm": 2.3986135797451666, "pct_lt_2p3": 0.0, "pct_lt_2p4": 0.0, "worst_xyz_th": [[314.5, 357.6, 40.1, 2.38], [ | PASS |
| repairs (clean_mesh per-mesh max / loft winding flips) vs limits | {"worst": {"loft_winding_flips": 0, "boundary_loops_filled": 0, "boundary_loops_left_open": 0, "degenerate_faces_dropped": 12, "vertices_merged": 6}, "limits": {"loft_winding_flips": 0, "boundary_loops_filled": 2, "boundary_loops_left_open": 0, "degenerate_fac | PASS |
| skin_swap: underlay.stl sha256 identical across all 5 styles and equal to out/underlay.stl (skin hashes must differ) | {"out_underlay": "22257f8f9cebb89b", "styles": {"calcified_webbing": "22257f8f9cebb89b", "bone_crust": "22257f8f9cebb89b", "flowstone": "22257f8f9cebb89b", "rust_blister": "22257f8f9cebb89b", "mummified_ochre": "22257f8f9cebb89b"}, "distinct_skins": 5} | PASS |
| determinism: two generate runs, sha256 of every STL | {"n_files": 9, "differing": []} | PASS |
