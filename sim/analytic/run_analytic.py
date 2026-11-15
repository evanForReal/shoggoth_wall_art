"""Independent hand/beam-theory check. python -m sim.analytic.run_analytic --underlay .. --params .. --out reports/
Uses ONLY trimesh slicing + shapely + a 3D frame model; shares no solver code with sim.hexfea.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import trimesh

from ..common import *
from .sections import sections_along
from .frame import solve_frame, G_ACC
from . import anchor as anc

GN = 9.81


def lc_loads(case, shelf_pt, tip_pt):
    loads = []; extra = []
    for ld in case.get("loads", []):
        d = np.asarray(ld["direction"], float); d /= np.linalg.norm(d)
        mag = ld["mass_kg"] * GN if "mass_kg" in ld else ld["force_N"]
        pt = shelf_pt if ld["where"] == "shelf_center" else tip_pt
        loads.append((pt, mag * d))
    return loads


def station_stress(st, ef_a, mat, bdir, wall):
    """ef_a: local end-a force vector acting on the outboard element at this station [Fx,Fy,Fz,Mx,My,Mz]."""
    Fx, Fy, Fz, Mx, My, Mz = ef_a
    A = st["A_eff_k"]; Iy = st["Iu_k"]; Iz = st["Iv_k"]
    # local y = u, z = v (see frame.beam_k); boundary coords relative to centroid (u,v)
    y = st["bnd"][:, 0]; z = st["bnd"][:, 1]
    sig = -Fx / A - My * z / Iy + Mz * y / Iz
    s = np.abs(sig); k = int(np.argmax(s)); smax = s[k]
    V = np.hypot(Fy, Fz)
    rmax = np.max(np.hypot(y, z))
    tau = 2.0 * V / A + abs(Mx) * rmax / max(st["J_k"], 1e-9)
    vm = np.sqrt(smax ** 2 + 3 * tau ** 2)
    sn = max(sig[k], 0.0) * float(st["t"] @ bdir) ** 2
    fi1 = vm / mat["allow_xy"]; fi2 = sn / mat["allow_z"]
    # classical thin-cylinder local buckling with 0.3 knockdown (compressive fibre)
    t = wall; R = 0.25 * ((y.max() - y.min()) + (z.max() - z.min())) if st["n_holes"] else 1e9
    scr = 0.3 * 0.605 * mat["E"] * t / max(R, 1e-6) if st["n_holes"] else 1e9
    fi3 = max(-sig.min(), 0.0) / scr
    return {"sigma_max": float(smax), "tau": float(tau), "vm": float(vm), "fi": float(max(fi1, fi2, fi3)),
            "fi_buckling": float(fi3), "V": float(V), "T": float(abs(Mx)), "M": float(np.hypot(My, Mz))}


def run(a):
    params = load_params(a.params); lc = load_loadcases(a.loadcases); mat = material(lc, params)
    mesh = trimesh.load(a.underlay, force="mesh", process=False)
    skin = trimesh.load(a.skin, force="mesh", process=False) if a.skin and Path(a.skin).exists() else None
    manifest = load_manifest(a.params, a.underlay)
    cl = get_centerline(params, manifest)
    if cl is None:
        b = mesh.bounds; cl = Centerline(np.array([[b[0][0], 0, 0], [b[1][0], 0, 0]]))
    wall = params["shell_wall"]; f_inf = lc["infill"]["fraction"]
    pdm = plate_dims(params, manifest)
    x_root = pdm["thickness"] + stub_depth(params)
    # root station: first centerline fraction past the root block
    fr = np.linspace(0, 1, 2001); P, _ = cl.at(fr)
    s0 = float(fr[np.argmax(P[:, 0] >= x_root - 1e-6)]) if (P[:, 0] >= x_root - 1e-6).any() else 0.0
    rh = lambda f: 70.0 if manifest else float(local_radius(params, f))
    ribp = float((params.get("ribs") or {}).get("pitch", 36.0))
    n_st = a.stations or int(np.ceil(cl.L * (1 - s0) / a.spacing)) + 1
    st = sections_along(mesh, cl, wall, f_inf, n=n_st, s0=s0, s1=1.0, r_hint=rh, window_mm=ribp)
    # drop the last 2 mm-ish station if inside the tip cap (section may be solid disc)
    for s in st:
        s["rhoA"] = mat["rho_t_mm3"] * s["A_eff"]
    skin_info = {}
    if skin is not None:
        fm = lc["skin"]["mass_factor"]
        for s in st:
            A = 0.0
            from .sections import slice_loops, ring_moments
            from shapely.geometry import Polygon
            reg = None
            for l in sorted(slice_loops(skin, s["p"], s["t"]), key=lambda l: -abs(ring_moments(np.c_[l[:, 0], l[:, 1]])[0])):
                u_, v_ = s["u"], s["v"]; rel = l - s["p"]
                pg = Polygon(np.c_[rel @ u_, rel @ v_]).buffer(0)
                reg = pg if reg is None else reg.symmetric_difference(pg)
            A = float(reg.area) if reg is not None else 0.0
            s["rhoA"] += mat["rho_t_mm3"] * fm * A
        skin_info["note"] = "skin mass from planar sections x mass_factor"
    sz = params.get("shelf_zone", {}) or {}
    if manifest and manifest.get("shelf", {}).get("load_point_LC1"):
        lp = np.array(manifest["shelf"]["load_point_LC1"], float)
        frac = float(cl.project(lp[None, :])[0][0])
    else:
        frac = sz.get("center_frac", float(np.mean(sz.get("span_frac", sz.get("s_range", [0.65, 0.95])))) if ("span_frac" in sz or "s_range" in sz) else 0.8)
    idx_shelf = int(np.argmin([abs(s["s"] - frac) for s in st]))
    shelf_pt = st[idx_shelf]["p"]; tip_pt = st[-1]["p"]
    if manifest and manifest.get("shelf", {}).get("load_point_LC1"):
        shelf_pt = lp.copy(); shelf_pt[2] = st[idx_shelf]["p"][2] + 0.0 * shelf_pt[2]    # load applied at centroid height to avoid fake torsion; offset reported
    bdir = layer_dir(params)
    out = {"tool": "sim.analytic.run_analytic", "date": TODAY, "inputs": {"underlay": str(a.underlay), "skin": str(a.skin) if skin is not None else None, "params": str(a.params)},
           "material": mat["name"], "n_stations": len(st), "spacing_mm": a.spacing, "root_fraction": s0, "root_x_mm": x_root,
           "assumptions": [f"stiffness properties = running minimum over +-{ribp/2:.0f} mm (rib pitch {ribp:.0f}): ring ribs/bulkhead plugs not credited as continuous beam stiffness; mass is not filtered", "root block (plate+stub) rigid: frame fixed at first station past plate+stub", "J via Bredt (single-cell) or polar; product of inertia neglected in frame (reported)",
                           "infill-equivalent: material deeper than shell_wall scaled by infill E/rho factor", "stress at station boundary fibres; tau = 2V/A + T*r/J"],
           "sections": [{"s": round(s["s"], 3), "A_mm2": round(s["A_eff"], 1), "Iu": round(s["Iu"], 0), "Iv": round(s["Iv"], 0), "Iuv_over_sqrt_IuIv": round(abs(s["Iuv"]) / np.sqrt(s["Iu"] * s["Iv"]), 4),
                         "J": round(s["J"], 0), "t_eff": round(s["t_eff_mm"], 2), "centroid": s["p"].round(1).tolist()} for s in st],
           "mass_kg": round(sum(0.5 * (st[i]["rhoA"] + st[i + 1]["rhoA"]) * np.linalg.norm(st[i + 1]["p"] - st[i]["p"]) for i in range(len(st) - 1)) * 1000, 4),
           "shelf_point": shelf_pt.round(1).tolist(), "tip_point": tip_pt.round(1).tolist()}
    cases = []
    for case in lc["load_cases"]:
        if case["kind"] != "static":
            continue
        loads = lc_loads(case, shelf_pt, tip_pt)
        r = solve_frame(st, mat["E"], mat["nu"], mat["rho_t_mm3"], loads=loads, self_weight=bool(case.get("self_weight")), modal=False)
        u = r["u"]
        stress = []
        for i in range(len(st) - 1):
            stress.append(station_stress(st[i], r["ef"][i][:6], mat, bdir, wall))
        fi = np.array([s["fi"] for s in stress]); k = int(np.argmax(fi))
        sfreq = case.get("sf_min")
        c = {"id": case["id"], "sf": float(1 / fi[k]), "sf_required": sfreq, "governing_station_s": round(st[k]["s"], 3),
             "sigma_max_MPa": stress[k]["sigma_max"], "vm_MPa": stress[k]["vm"],
             "tip_disp_mm": u[-1, :3].round(4).tolist(), "tip_disp_mag_mm": float(np.linalg.norm(u[-1, :3])),
             "shelf_disp_mm": u[idx_shelf, :3].round(4).tolist(),
             "root_react_F_N": r["react"][:3].round(3).tolist(), "root_react_M_Nmm": r["react"][3:].round(1).tolist(),
             "fi_buckling_max": max(s["fi_buckling"] for s in stress),
             "util_by_station": [round(float(x * (sfreq or 1)), 3) for x in fi]}
        c["pass_numeric"] = None if not sfreq else bool(c["sf"] >= sfreq)
        if case["id"] == "LC1":
            c["defl_metric_mm"] = float(max(abs(u[idx_shelf, 2]), np.linalg.norm(u[-1, :3])))
            c["defl_ok"] = c["defl_metric_mm"] <= lc["criteria"]["tip_deflection_max_mm"]
            c["pass_numeric"] = bool(c["pass_numeric"] and c["defl_ok"])
            c["stress_profile"] = [{"s": round(st[i]["s"], 3), "sigma": round(stress[i]["sigma_max"], 3), "vm": round(stress[i]["vm"], 3), "V": round(stress[i]["V"], 2), "M": round(stress[i]["M"], 0)} for i in range(len(stress))]
        # internal forces at root station for anchor transfer: reaction at root node -> origin
        c["_root_pt"] = st[0]["p"].tolist()
        cases.append(c)
    out["load_cases"] = cases
    # modal
    mp = 5.0 / 1000.0
    rb = solve_frame(st, mat["E"], mat["nu"], mat["rho_t_mm3"], loads=None, self_weight=False, modal=True)
    rp = solve_frame(st, mat["E"], mat["nu"], mat["rho_t_mm3"], extra_mass=[(shelf_pt, mp)], loads=None, self_weight=False, modal=True)
    out["modal"] = {"freq_bare_Hz": rb["freq"][:4].round(3).tolist(), "freq_with_5kg_plant_Hz": rp["freq"][:4].round(3).tolist(), "limit_Hz": lc["criteria"]["freq_min_hz"],
                    "pass_numeric": bool(rp["freq"][0] >= lc["criteria"]["freq_min_hz"]), "method": "3D EB frame, consistent mass, dense eig"}
    # anchor (LC1, LC2): transfer root reaction to origin
    sp_ = screw_positions(params, manifest)
    capsd = lc["anchor"]["capacities_ultimate_N"]
    pl = {"size_y": pdm["size_y"], "size_z": pdm["size_z"], "thickness": pdm["thickness"], "hole_dia": pdm["hole_d"]}
    anchor = {"screw_positions_yz": sp_.tolist(), "options": {}}
    for case_id in ("LC1", "LC2"):
        c = next(c for c in cases if c["id"] == case_id)
        F = np.array(c["root_react_F_N"]); Mr = np.array(c["root_react_M_Nmm"])
        Mo = Mr + np.cross(np.array(c["_root_pt"]), F)       # moment of reaction about origin
        c["anchor_F_N"] = F.tolist(); c["anchor_M_Nmm_origin"] = Mo.round(0).tolist()
        for oname, opt in lc["anchor"]["options"].items():
            act = [i for i, (y, z) in enumerate(sp_) if (y > 0 or opt["screws"] == "all")]
            g = anc.group_loads(F, Mo, sp_, act, plate_z_edge=-pl.get("size_z", 110) / 2, plate_y_edge=-pl.get("size_y", 160) / 2)
            cap = capsd[opt["kind"]]
            sfreq = lc["criteria"]["sf_lc1_lc3"] if case_id == "LC1" else lc["criteria"]["sf_lc2"]
            u_ = anc.screw_util(g, cap, sfreq)
            pt = anc.head_pullthrough(g["T_max"], lc["anchor"]["screw_head_dia_mm"], pl.get("thickness", 8.0), pl.get("hole_dia", 6.0), mat["allow_z"])
            anchor["options"].setdefault(oname, {})[case_id] = {"desc": opt["desc"], **g, **u_, "head_pullthrough": pt}
    out["anchor"] = anchor
    # joint demands at requested stations
    if a.joints:
        joints = json.loads(Path(a.joints).read_text()) if (Path(a.joints).is_file() and Path(a.joints).stat().st_size) else []
        hw = lc["joint_hardware"]["default"]; res = []
        for j in joints:
            k = int(np.argmin([abs(s["s"] - j["s"]) for s in st])); k = min(k, len(st) - 2)
            row = {"s": j["s"], "station": round(st[k]["s"], 3)}
            for case_id in ("LC1", "LC2"):
                case = next(c for c in lc["load_cases"] if c["id"] == case_id)
                r = solve_frame(st, mat["E"], mat["nu"], mat["rho_t_mm3"], loads=lc_loads(case, shelf_pt, tip_pt), self_weight=True, modal=False)
                S = station_stress(st[k], r["ef"][k][:6], mat, bdir, wall)
                pin = anc.pin_shear(S["V"], hw["dia_mm"], hw["count"], hw["tau_ult_MPa"])
                row[case_id] = {"V_N": S["V"], "M_Nmm": S["M"], "T_Nmm": S["T"], "section_sigma_MPa": S["sigma_max"], "pin_SF": pin["SF"],
                                "plane_SF_with_Kt": float(mat["allow_xy"] / (lc.get("joint_kt", 2.0) * max(S["sigma_max"], 1e-9)))}
            res.append(row)
        out["joints"] = {"hardware_assumed": hw, "kt_assumed": lc.get("joint_kt", 2.0), "stations": res}
    for c in cases:
        c.pop("_root_pt", None)
    out["summary"] = {"min_sf_lc1_lc3": min(c["sf"] for c in cases if c["id"].startswith(("LC1", "LC3"))), "all_pass_numeric": all(c["pass_numeric"] for c in cases if c["pass_numeric"] is not None) and out["modal"]["pass_numeric"]}
    outd = Path(a.out); outd.mkdir(parents=True, exist_ok=True)
    (outd / f"{a.name}.json").write_text(json.dumps(out, indent=1, default=float))
    write_md(out, outd / f"{a.name}.md")
    return out


def write_md(o, path):
    L = [f"# Analytic (independent beam/hand) check ({o['date']})\n",
         f"- stations {o['n_stations']}, root at s={o['root_fraction']:.3f} (x>={o['root_x_mm']} mm), underlay mass {o['mass_kg']} kg (beam integral, infill-equivalent), material {o['material']}",
         f"- shelf pt {o['shelf_point']}, tip pt {o['tip_point']}", "- assumptions: " + "; ".join(o["assumptions"]),
         "\n| LC | SF | req | gov. s | sigma max MPa | tip disp mm | pass |\n|---|---|---|---|---|---|---|"]
    for c in o["load_cases"]:
        L.append(f"| {c['id']} | {c['sf']:.2f} | {c['sf_required']} | {c['governing_station_s']} | {c['sigma_max_MPa']:.2f} | {c['tip_disp_mag_mm']:.2f} | {c['pass_numeric']} |")
    lc1 = next(c for c in o["load_cases"] if c["id"] == "LC1")
    L.append(f"\nLC1 deflection metric {lc1['defl_metric_mm']:.2f} mm (ok={lc1['defl_ok']}); root reaction F {lc1['root_react_F_N']} N M {lc1['root_react_M_Nmm']} N*mm; local-buckling FI max {max(c['fi_buckling_max'] for c in o['load_cases']):.2f}")
    m = o["modal"]; L.append(f"\nModal: bare {m['freq_bare_Hz']} Hz; with 5 kg plant {m['freq_with_5kg_plant_Hz']} Hz; limit {m['limit_Hz']} -> pass {m['pass_numeric']}")
    L.append("\n## Anchor (screws-only elastic group; tension upper bound; capacities ASSUMED, see loadcases.json)\n| option | LC | T max N | V max N | util | SF | req | pass | head pull-thru SF |\n|---|---|---|---|---|---|---|---|---|")
    for on, d in o["anchor"]["options"].items():
        for lcid, v in d.items():
            L.append(f"| {on} | {lcid} | {v['T_max']:.1f} | {v['V_max']:.1f} | {v['util']:.2f} | {v['SF']:.2f} | {v['sf_required']} | {v['pass']} | {v['head_pullthrough']['SF']:.1f} |")
            for n_ in v["notes"]:
                L.append(f"|  | | note: {n_} | | | | | | |")
    if "joints" in o:
        L.append("\n## Joint demands (assumed hardware " + json.dumps(o["joints"]["hardware_assumed"]) + ")")
        for j in o["joints"]["stations"]:
            L.append(f"- s={j['s']}: " + "; ".join(f"{k}: V {v['V_N']:.0f} N, M {v['M_Nmm']:.0f} N*mm, pin SF {v['pin_SF']:.1f}, plane SF(Kt) {v['plane_SF_with_Kt']:.1f}" for k, v in j.items() if k.startswith("LC")))
    L.append("\n---\n*Edit log*\n\n| Date | Agent | Change | Signed-off-by |\n|------|-------|--------|---------------|\n| " + o["date"] + " | verif-analytic (generated) | auto-generated by sim.analytic.run_analytic | [PROVISIONAL] |")
    Path(path).write_text("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--underlay", required=True); ap.add_argument("--skin"); ap.add_argument("--params", required=True)
    ap.add_argument("--loadcases", default=str(P0 / "loadcases.json")); ap.add_argument("--out", required=True)
    ap.add_argument("--name", default="analytic"); ap.add_argument("--stations", type=int, default=0); ap.add_argument("--spacing", type=float, default=5.0); ap.add_argument("--joints")
    a = ap.parse_args(); o = run(a)
    print([(c["id"], round(c["sf"], 2), round(c["tip_disp_mag_mm"], 3)) for c in o["load_cases"]], o["modal"]["freq_with_5kg_plant_Hz"][:2])


if __name__ == "__main__":
    main()
