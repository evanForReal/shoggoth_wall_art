"""FEA vs analytic cross-check; flags >15 % disagreement. python tools/crosscheck.py fea.json analytic.json --out dir"""
import argparse, json
from pathlib import Path

TOL = 0.15
DATE = "2026-11-15"

def rel(a, f):
    d = max(abs(f), 1e-9)
    return (a - f) / d

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("fea"); ap.add_argument("analytic"); ap.add_argument("--out", required=True); a = ap.parse_args()
    F = json.loads(Path(a.fea).read_text()); A = json.loads(Path(a.analytic).read_text())
    fl = {c["id"]: c for c in F["load_cases"]}; al = {c["id"]: c for c in A["load_cases"]}
    rows = []
    def add(name, fe, an, floor=0.0, note=""):
        r = rel(an, fe)
        flag = "FLAG" if (abs(r) > TOL and max(abs(fe), abs(an)) > floor) else "ok"
        rows.append({"metric": name, "fea": fe, "analytic": an, "rel_diff_pct": 100 * r, "flag": flag, "note": note})
    for lc in ("LC1", "LC2", "LC3a", "LC3c"):
        if lc in fl and lc in al:
            add(f"{lc} tip |u| mm", fl[lc]["tip_disp_mag_mm"], al[lc]["tip_disp_mag_mm"], 0.05, "FEA includes plate/stub compliance; analytic root rigid at plate+stub")
    if "LC1" in fl and "LC1" in al:
        add("LC1 root reaction Fz N", fl["LC1"]["reaction_F_N"][2], al["LC1"]["root_react_F_N"][2], 0, "weight incl. skin mass: checks mass bookkeeping")
        # moments about origin: analytic anchor_M vs FEA reaction M
        Mf = fl["LC1"]["reaction_M_Nmm_about_origin"]; Ma = al["LC1"].get("anchor_M_Nmm_origin")
        if Ma:
            for i, nm in enumerate(("Mx", "My", "Mz")):
                add(f"LC1 anchor {nm} N*mm", Mf[i], Ma[i], 2000.0)
    fm = F["modal"]; am = A["modal"]
    if fm.get("freq_with_5kg_plant_Hz"):
        add("f1 with plant Hz", fm["freq_with_5kg_plant_Hz"][0], am["freq_with_5kg_plant_Hz"][0], 0, "")
        add("f1 bare Hz", fm["freq_bare_Hz"][0], am["freq_bare_Hz"][0], 0, "")
    # stress: max utilization excluding root (first) and tip bins
    su = F.get("station_utilization", [])
    if su and "util_by_station" in al.get("LC1", {}):
        fe_max = max(s["util_max"] for s in su[1:-1]) if len(su) > 2 else None
        # FEA utilization is max over all LCs; compare to analytic max over all static LCs outside the root region
        an = max(max(c["util_by_station"][len(c["util_by_station"]) // 6:-2]) for c in A["load_cases"] if c.get("util_by_station"))
        if fe_max is not None:
            add("max utilization U=FI*SF_req (span interior)", fe_max, an, 0.02, "FEA includes local concentration at ribs/pad; analytic is beam-theory fibre stress -> FEA >= analytic expected")
    # anchor (FEA screws-only vs analytic)
    af = F.get("anchor_fea", {}).get("per_config", {})
    for cfg, nm in (("all4", "backer_4"), ("stud_2", "stud_2")):
        if cfg in af and nm in A["anchor"]["options"]:
            for lc in ("LC1",):
                Tf = max(abs(v[0]) for v in af[cfg][lc].values())   # Fx = pull-out
                add(f"anchor {nm} {lc} max |pull-out| N", Tf, A["anchor"]["options"][nm][lc]["T_max"], 5.0, "FEA no-contact patch support vs elastic screw-group")
    nflag = sum(r["flag"] == "FLAG" for r in rows)
    out = {"tool": "tools/crosscheck.py", "date": DATE, "tolerance_pct": 100 * TOL, "rows": rows, "summary": {"n_flag": nflag, "status": "FLAG" if nflag else "AGREE"}}
    d = Path(a.out); d.mkdir(parents=True, exist_ok=True)
    (d / "crosscheck.json").write_text(json.dumps(out, indent=1))
    L = [f"# FEA vs analytic cross-check ({DATE})\n", f"Tolerance {100*TOL:.0f} %. Status: **{out['summary']['status']}** ({nflag} flagged)\n", "| metric | FEA | analytic | diff % | flag | note |\n|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['metric']} | {r['fea']:.4g} | {r['analytic']:.4g} | {r['rel_diff_pct']:+.1f} | {r['flag']} | {r['note']} |")
    L.append("\n---\n*Edit log*\n\n| Date | Agent | Change | Signed-off-by |\n|------|-------|--------|---------------|\n| " + DATE + " | verif-analytic (generated) | tools/crosscheck.py | [PROVISIONAL] |")
    (d / "crosscheck.md").write_text("\n".join(L) + "\n")
    print(out["summary"])

if __name__ == "__main__":
    main()
