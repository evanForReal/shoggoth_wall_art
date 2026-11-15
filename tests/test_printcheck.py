import unittest
import numpy as np
import trimesh
from sim.voxel import occupancy
from printcheck import checks as C
from printcheck.joints import joint_fit


def box(ext, c=(0, 0, 0)):
    return trimesh.creation.box(ext, transform=trimesh.transformations.translation_matrix(c))


class TestPrintcheck(unittest.TestCase):
    def test_raster_hollow_volume(self):
        o = trimesh.creation.cylinder(radius=20, height=60, sections=96)
        i = trimesh.creation.cylinder(radius=17.6, height=60, sections=96); i.invert()
        m = trimesh.util.concatenate([o, i])
        occ, bad, g = occupancy(m, 0.4)
        v = occ.sum() * g.pitch ** 3
        self.assertLess(abs(v / (np.pi * (400 - 17.6 ** 2) * 60) - 1), 0.02)
        self.assertEqual(bad, 0)

    def test_integrity_detects_defects(self):
        good = box([20, 20, 20])
        self.assertTrue(C.mesh_integrity(good)["pass"])
        opened = good.copy(); opened.update_faces(np.arange(len(opened.faces)) != 0); opened.remove_unreferenced_vertices()
        self.assertFalse(C.mesh_integrity(opened)["pass"])
        overlap = trimesh.util.concatenate([box([20, 20, 20]), box([20, 20, 20], (8, 0, 0))])   # un-unioned overlapping shells
        r = C.mesh_integrity(overlap)
        self.assertGreater(r["self_intersection_proxy_cells"], 0)
        self.assertFalse(r["pass"])

    def test_thin_scan_flags_thin_plate(self):
        thin = box([40, 40, 0.6]); thick = box([40, 40, 3.0])
        rt = C.thin_scan(thin, thresholds=(1.2,), pitch=0.2); rk = C.thin_scan(thick, thresholds=(1.2,), pitch=0.2)
        self.assertGreater(rt["by_threshold"]["1.2"]["vol_mm3"], 0.0)
        self.assertEqual(rk["by_threshold"]["1.2"]["vol_mm3"], 0.0)

    def test_joint_fit(self):
        a = box([20, 20, 20], (-10, 0, 0))
        b_ok = box([20, 20, 20], (10.25, 0, 0))        # 0.25 mm gap
        b_bad = box([20, 20, 20], (9.0, 0, 0))         # 1 mm interference
        jo = joint_fit(a, b_ok); jb = joint_fit(a, b_bad)
        self.assertTrue(jo["mating"]); self.assertAlmostEqual(jo["gap_median_mm"], 0.25, delta=0.12)
        self.assertGreater(jb["interference_mm3"], 100.0); self.assertFalse(jb["pass"])

    def test_overhang_and_bed(self):
        t = trimesh.creation.cylinder(radius=10, height=100)      # axis z: no overhang except bottom on bed
        o = C.orient_stats(t, np.array([0, 0, 1.0]))
        self.assertLess(o["overhang_fraction"], 0.01)
        h = trimesh.creation.cylinder(radius=10, height=100); h.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0]))
        o2 = C.orient_stats(h, np.array([0, 0, 1.0]))               # lying cylinder: lower half-ish overhang beyond 45deg
        self.assertGreater(o2["overhang_fraction"], 0.2)
        long = box([400, 10, 10]); self.assertFalse(any(x["fits_bed"] for x in C.orientations(long) if x["up"] == "+z"))
        diag = box([200, 200, 10]); self.assertTrue(any(x["fits_bed"] for x in C.orientations(diag)))


if __name__ == "__main__":
    unittest.main()
