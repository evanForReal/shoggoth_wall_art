"""Consolidated P0 review: pass/fail vs spec exit criteria 1-5. Honest: unknown/unvalidated = UNVERIFIED/FAIL, never PASS by default.
python tools/consolidate.py --reports prototype/p0/reports --p0 prototype/p0"""
import argparse, json, subprocess, sys, os
from pathlib import Path

DATE = "2026-11-15"

def jl(p):
    p = Path(p)
    return json.loads(p.read_text()) if p.exists() else None

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--reports", required=True); ap.add_argument("--p0", required=True); a = ap.parse_args()
    R = Path(a.reports); P = Path(a.p0)
    fea, ana, prt, xc, ss = (jl(R / f"{n}.json") for n in ("fea", "analytic", "printability", "crosscheck", "skin_swap"))
    sign = jl(R / "SIGNOFF.json")
    val = jl(Path(__file__).resolve().parent.parent / "sim" / "validation.json")
    rows = []
    # 1 generator
    art = [P / "out" / n for n in ("underlay.stl", "skin.stl", "assembly.stl")]
    segs = sorted((P / "out" / "segments").glob("seg_??.stl")) if (P / "out" / "segments").exists() else []
    gen = (P / "generate.py").exists(); params = (P / "params.json").exists()
    ok1 = gen and params and all(x.exists() for x in art) and len(segs) >= 2
    rows.append(("1 one-command generator emits all artifacts", "PASS" if ok1 else "FAIL",
                 f"generate.py={gen}, params.json={params}, artifacts={[x.exists() for x in art]}, segments={len(segs)}. Not verified here: that artifacts are reproducible from params.json alone (make p0 GEN=1 reruns it)."))
    # 2 FEA + analytic
    if not fea or not ana:
        rows.append(("2 FEA + analytic pass LC1-LC5 at SF", "UNVERIFIED", "fea.json or analytic.json missing"))
    else:
        fl = fea["load_cases"]; fails = [c["id"] for c in fl if c["status"] == "FAIL"] + [c["id"] for c in ana["load_cases"] if c["pass_numeric"] is False]
        unver = [c["id"] for c in fl if c["status"] == "UNVERIFIED"]
        modal_f = fea["modal"].get("status"); an_modal = ana["modal"]["pass_numeric"]
        anchor_ok = {o: all(v["pass"] for v in d.values()) for o, d in ana["anchor"]["options"].items()}
        any_anchor = any(anchor_ok.values())
        flag = xc["summary"]["n_flag"] if xc else None
        if fails or not an_modal or modal_f == "FAIL" or not any_anchor:
            st = "FAIL"
        elif unver or modal_f in ("UNVERIFIED", "ERROR") or flag is None or flag > 0 or not (val and val.get("validated")):
            st = "UNVERIFIED"
        else:
            st = "PASS"
        rows.append(("2 FEA + analytic pass LC1-LC5 at SF", st,
                     f"FEA status {fea['summary']['status']} (solver validated={fea['solver_validation']['validated']}, h/wall={fea['model']['h_over_wall']:.2f}); fails={fails or 'none'}; FEA min SF(LC1,LC3)={fea['summary']['min_sf_lc1_lc3']:.2f}, analytic {ana['summary']['min_sf_lc1_lc3']:.2f}; "
                     f"f1(plant) FEA {fea['modal'].get('freq_with_5kg_plant_Hz', ['?'])[0]} / analytic {ana['modal']['freq_with_5kg_plant_Hz'][0]} Hz; LC5 anchor options passing (analytic, ASSUMED capacities): {anchor_ok}; cross-check flags={flag}"))
    # 3 printability
    if not prt:
        rows.append(("3 printability passes", "UNVERIFIED", "printability.json missing"))
    else:
        s = prt["summary"]
        rows.append(("3 printability passes (manifold, wall/feature, overhang, bed, joints)", s["status"],
                     f"{s['n_fail']} failing / {s['n_unverified']} unverified checks: " + "; ".join(i["check"] for i in prt["checks"] if i["status"] != "PASS")[:600]))
    # 4 independent sign-off
    if sign and sign.get("reviewer") and sign["reviewer"] not in sign.get("authors", []):
        rows.append(("4 independent reviewer signs report", "PASS", f"reviewer {sign['reviewer']} (authors {sign.get('authors')}), scope {sign.get('scope')}"))
    else:
        rows.append(("4 independent reviewer signs report", "UNVERIFIED", "no reports/SIGNOFF.json from an agent distinct from the check authors; run tools/review_rerun.py by a separate reviewer"))
    # 5 skin swap
    if not ss:
        rows.append(("5 skin swap test", "UNVERIFIED", "skin_swap.json missing"))
    else:
        rows.append(("5 skin swap: underlay results unchanged (<=2 %)", ss["summary"]["status"], "; ".join(f"{c['check']}: {c['status']}" for c in ss["checks"])[:700]))
    L = [f"# P0 review (consolidated, generated {DATE})\n", "Status vocabulary: PASS = demonstrated; FAIL = demonstrated violation; UNVERIFIED = not demonstrated (missing evidence, unvalidated solver, or assumption not signed off).\n",
         "| # criterion | status | evidence / caveat |\n|---|---|---|"]
    for n, s, d in rows:
        L.append(f"| {n} | **{s}** | {d} |")
    overall = "FAIL" if any(s == "FAIL" for _, s, _ in rows) else ("UNVERIFIED" if any(s != "PASS" for _, s, _ in rows) else "PASS")
    L.append(f"\n**Overall P0: {overall}**\n")
    if fea:
        L.append("## Key numbers\n")
        for c in fea["load_cases"]:
            L.append(f"- FEA {c['id']}: SF {c['sf']:.2f} (req {c['sf_required']}), vM {c['vm_max_MPa']:.2f} MPa at {c['hotspot_xyz']}, tip {c['tip_disp_mag_mm']:.2f} mm [{c['status']}]")
    if ana:
        L.append(f"- Analytic min SF(LC1,LC3) {ana['summary']['min_sf_lc1_lc3']:.2f}; mass {ana['mass_kg']} kg (beam integral)")
    L.append("\nSee `fea.md`, `analytic.md`, `crosscheck.md`, `printability.md`, `skin_swap.md`, `../VERIFICATION_NOTES.md`, `sim/VALIDATION.md`.")
    L.append("\n---\n*Edit log*\n\n| Date | Agent | Change | Signed-off-by |\n|------|-------|--------|---------------|\n| " + DATE + " | verif-infra (generated) | tools/consolidate.py | [PROVISIONAL] |")
    (R / "P0_REVIEW.md").write_text("\n".join(L) + "\n")
    (R / "P0_REVIEW.json").write_text(json.dumps({"date": DATE, "overall": overall, "criteria": [{"criterion": n, "status": s, "detail": d} for n, s, d in rows]}, indent=1))
    print(overall, [(n[:2], s) for n, s, _ in rows])

if __name__ == "__main__":
    main()
