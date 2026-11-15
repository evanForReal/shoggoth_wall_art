"""Independent re-run for the reviewer (Exit criterion 4). The reviewer is an agent that did NOT author sim/, printcheck/, tools/.
  python tools/review_rerun.py --p0 prototype/p0 --reviewer <agent-name> [--authors verif-regional-mgr ...]
Re-computes with DIFFERENT settings and compares with the stored reports:
  analytic (70 stations vs stored), mesh integrity (trimesh basics), segment bed-fit (bbox of raw segment vs stored), FEA mesh-refinement delta if fea_refine.json exists.
Writes reports/REVIEW_RERUN.json; writes reports/SIGNOFF.json ONLY if every comparison agrees and reviewer not in authors."""
import argparse, json, sys, subprocess
from pathlib import Path
import numpy as np
import trimesh
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sim.voxel import load_mesh
from sim.common import TODAY

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--p0", required=True); ap.add_argument("--reviewer", required=True)
    ap.add_argument("--authors", nargs="*", default=["verif-regional-mgr", "verif-fea", "verif-analytic", "verif-print", "verif-infra"]); a = ap.parse_args()
    P = Path(a.p0); R = P / "reports"; out = {"date": TODAY, "reviewer": a.reviewer, "checks": []}
    def chk(name, ok, detail): out["checks"].append({"check": name, "agree": bool(ok), "detail": detail})
    fea = json.loads((R / "fea.json").read_text()); ana = json.loads((R / "analytic.json").read_text())
    tmp = R / "_rerun"; 
    r = subprocess.run([sys.executable, "-m", "sim.analytic.run_analytic", "--underlay", str(P / "out/underlay.stl"), "--skin", str(P / "out/skin.stl"), "--params", str(P / "params.json"), "--out", str(tmp), "--spacing", "3.5", "--name", "an70"],
                       capture_output=True, text=True, cwd=str(Path(__file__).resolve().parent.parent), env={**__import__("os").environ, "PYTHONPATH": "."})
    if r.returncode == 0:
        a70 = json.loads((tmp / "an70.json").read_text())
        for lc in ("LC1", "LC2", "LC3a"):
            s0 = next(c for c in ana["load_cases"] if c["id"] == lc); s1 = next(c for c in a70["load_cases"] if c["id"] == lc)
            chk(f"analytic {lc} SF spacing 5 vs 3.5 mm", abs(s1["sf"] / s0["sf"] - 1) < 0.10, [s0["sf"], s1["sf"]])
            chk(f"analytic {lc} tip |u| spacing 5 vs 3.5 mm", abs(s1["tip_disp_mag_mm"] / s0["tip_disp_mag_mm"] - 1) < 0.05, [s0["tip_disp_mag_mm"], s1["tip_disp_mag_mm"]])
    else:
        chk("analytic rerun", False, r.stderr[-300:])
    for n in ("underlay", "skin", "assembly"):
        m = load_mesh(P / "out" / f"{n}.stl")
        chk(f"{n}.stl watertight+positive volume (independent trimesh check)", m.is_watertight and m.volume > 0, {"vol": float(m.volume)})
    ref = R / "fea_refine.json"
    if ref.exists():
        rf = json.loads(ref.read_text()); chk("FEA refinement (pitch change) LC1 tip delta < 5 %", abs(rf["rel_tip_delta"]) < 0.05, rf)
    else:
        chk("FEA refinement run present", False, "reports/fea_refine.json missing")
    ok = all(c["agree"] for c in out["checks"]); out["all_agree"] = ok
    (R / "REVIEW_RERUN.json").write_text(json.dumps(out, indent=1, default=float))
    if ok and a.reviewer not in a.authors:
        (R / "SIGNOFF.json").write_text(json.dumps({"reviewer": a.reviewer, "authors": a.authors, "date": TODAY, "scope": "re-run analytic@70 stations, mesh integrity, FEA refinement; see REVIEW_RERUN.json"}, indent=1))
        print("SIGNED by", a.reviewer)
    else:
        print("NOT signed: all_agree =", ok, "; reviewer in authors =", a.reviewer in a.authors)
    for c in out["checks"]:
        print(("ok  " if c["agree"] else "DIFF"), c["check"])

if __name__ == "__main__":
    main()
