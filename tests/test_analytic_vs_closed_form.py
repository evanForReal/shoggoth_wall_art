import unittest
import numpy as np
from sim.common import Centerline
from sim.analytic.sections import sections_along
from sim.analytic.frame import solve_frame
from sim.analytic import anchor as anc
from sim.reference import gen_reference as gr

E, NU, RHO = 2000.0, 0.35, 1.27e-9


class TestFrame(unittest.TestCase):
    def test_tube_cantilever(self):
        L, D, w = 300.0, 50.0, 2.4
        m = gr.straight_bar("tube", L=L, D=D, wall=w, segs=128)
        cl = Centerline(np.array([[0, 0, 0], [L, 0, 0]], float))
        st = sections_along(m, cl, w, 0.2, n=25, s0=0.02, s1=0.97, r_hint=lambda f: D / 2)
        for s in st:
            s["rhoA"] = RHO * s["A_eff"]
        ro = D / 2; ri = ro - w
        I = np.pi * (ro ** 4 - ri ** 4) / 4; A = np.pi * (ro ** 2 - ri ** 2)
        Leff = st[-1]["p"][0] - st[0]["p"][0]
        P = 100.0
        r = solve_frame(st, E, NU, RHO, loads=[(st[-1]["p"], np.array([0, 0, -P]))], self_weight=False, modal=True)
        d = -r["u"][-1, 2]
        d_cf = P * Leff ** 3 / (3 * E * I)
        self.assertLess(abs(d / d_cf - 1), 0.02)
        f_cf = 1.8751 ** 2 / (2 * np.pi * Leff ** 2) * np.sqrt(E * I / (RHO * A))
        self.assertLess(abs(r["freq"][0] / f_cf - 1), 0.03)
        # root reaction moment = P * Leff
        self.assertLess(abs(abs(r["react"][4]) / (P * Leff) - 1), 0.01)

    def test_screw_group_hand_calc(self):
        # 4 screws at (+-60,+-35); pure axial pull-out Fx=400 N -> 100 N each; moment My (about Y) 10000 N*mm -> +-10000*35/(4*35^2)
        pos = np.array([[60, 35], [60, -35], [-60, 35], [-60, -35]], float)
        g = anc.group_loads([-400.0, 0, 0], [0, -10000.0, 0], pos, [0, 1, 2, 3])   # reaction = -load
        T = np.array(g["T_N"])
        self.assertAlmostEqual(T.mean(), 100.0, places=3)
        self.assertAlmostEqual(T.max() - T.min(), 2 * 10000 * 35 / (4 * 35 ** 2), places=1)


if __name__ == "__main__":
    unittest.main()
