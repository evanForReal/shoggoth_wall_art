import unittest, json
from pathlib import Path
import numpy as np
from sim.voxel import occupancy
from sim.hexfea import HexModel
from sim.reference import gen_reference as gr


class TestFEA(unittest.TestCase):
    def test_square_bar_tip_deflection_5pct(self):
        E, nu = 2000.0, 0.35
        m = gr.straight_bar("square", L=100, side=20)
        occ, bad, g = occupancy(m, 2.5, pad=1)
        M = HexModel(occ, g, E, nu, rho=1.27e-9)
        x0 = M.xyz[:, 0].min()
        M.set_fixed(M.nodes_where(lambda X: X[:, 0] < x0 + 1e-6))
        tip = M.nodes_where(lambda X: X[:, 0] > M.xyz[:, 0].max() - 1e-6)
        f = np.zeros(M.ndof); f[tip * 3 + 2] = -100.0 / len(tip)
        M.factor(); u, info = M.solve(f)
        I = 20 ** 4 / 12; kap = 10 * (1 + nu) / (12 + 11 * nu); G = E / (2 * (1 + nu))
        d_cf = 100 * 100 ** 3 / (3 * E * I) + 100 * 100 / (kap * G * 400)
        self.assertLess(abs(-u[tip * 3 + 2].mean() / d_cf - 1), 0.05)
        self.assertLess(info["rel_res"], 1e-6)

    def test_amg_cg_matches_direct(self):
        E, nu = 2000.0, 0.35
        m = gr.straight_bar("square", L=60, side=12)
        occ, bad, g = occupancy(m, 1.5, pad=1)
        M = HexModel(occ, g, E, nu, rho=1.27e-9)
        x0 = M.xyz[:, 0].min(); M.set_fixed(M.nodes_where(lambda X: X[:, 0] < x0 + 1e-6))
        f = M.gravity_load()
        M.factor(direct_limit=10 ** 9); u1, _ = M.solve(f)
        M.factor(direct_limit=0); u2, _ = M.solve(f)
        self.assertLess(np.linalg.norm(u1 - u2) / np.linalg.norm(u1), 1e-5)


class TestSchema(unittest.TestCase):
    def test_loadcases_valid(self):
        import subprocess, sys
        root = Path(__file__).resolve().parent.parent
        r = subprocess.run([sys.executable, str(root / "tools" / "schema_check.py"), str(root / "prototype/p0/loadcases.json")], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
