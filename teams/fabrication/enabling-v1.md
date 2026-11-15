# Fabrication Enabling Pass v1

**Status:** ACTIVE enabling work (RP-1 item 3). No final geometry exists; every number is an order-of-magnitude estimate from stated assumptions. Companion: `teams/cad/mesh-spec-v1.md`, `teams/structural/analysis/load-model-v1.md`.

## 0. Exec summary

1. **Segment count: plan on 16 for a 3x3 ft piece (range 12-20); 10-13 for 3x2 ft.** Audit estimate "12+" holds as a floor. Shelves 250-300 mm long add a tip segment each.
2. **Print time: ~17 printer-days nominal (range 5-45)** for ~12.6 kg of deposited material including supports at ~30 g/h. Two printers: ~9 calendar days nominal. Per segment ~26 h average.
3. **Material: PETG everywhere on the load path and body (ASA if the wall sees sun/heat); PLA only for decorative whips if wanted.** No project intel supports a material choice beyond structural's engineering judgment (see Section 3).
4. **Joint system: rear splice straps + pins/keys + adhesive for body seams; axial rod + dovetail for shelf tips.**
5. **Top-3 feasibility risks:** (1) undercut webbing needs supports that cannot be removed from lattice; (2) c01/c02 fine strands sit below the printable/handleable floor; (3) seam count and dimensional stack-up through lace-like geometry.
6. **Evan board probes:** seam visibility, material finish, perforation density (Section 6).

## 1. Segment count

### Assumptions
- Bed 256 x 256 mm (generic FDM, Z >= 250). Evan's real printer is unknown.
- Usable per-segment footprint 230 x 230 mm: 256 less ~8 mm margin each side (brim, skirt, first-layer flare) less ~5 mm for joint tongues/overlap.
- Piece envelope: 3x3 ft = 914 x 914 mm; 3x2 ft = 914 x 610 mm. Concept silhouettes measured on the c01/c02 images: c01 ~1:1 aspect, solid fill ~45% of its bounding box; c02 ~1.2:1 aspect, fill ~60%.

### Grid argument
- 914 / 230 = 3.97, so 4 columns. 3x3: 4 x 4 = 16 cells; 3x2: 4 x 3 = 12 cells (610 / 230 = 2.65, so 3 rows).
- Not every cell is occupied. c01 is spidery (empty bottom corners, empty sides between limbs): ~65-75% of cells touched = 10.5-12 cells. c02 is a blob: ~80-90% = 13-14 cells.
- Add shelf tip segments: shelves beyond ~240 mm from the root split (p = 250-300 mm shelves; mesh-spec Section 4). Assume 2 of 3 shelves split: +2. Plus mask/maw as separate hero pieces only if cut independently: +0-2.
- 3x3 total: c01 ~ 11 + 2 + 1 = 14; c02 ~ 13.5 + 2 + 1 = 16.5. Range 12-20 with an unlucky cut.

### Area cross-check (packing floor)
- Solid footprint area: c01 0.45 x 0.836 m^2 = 0.38 m^2; c02 (914 x 762 mm envelope at its 1.2:1 aspect, 0.70 m^2) 0.60 x 0.70 = 0.42 m^2.
- Per-segment usable area 0.23 x 0.23 = 0.0529 m^2. Perfect packing: 0.38 / 0.0529 = 7.2; 0.42 / 0.0529 = 7.9.
- Irregular limb-following cuts waste 30-50% of each cell (curved limbs do not tile a square). At ~60% packing efficiency: 7.2 / 0.6 = 12; 7.9 / 0.6 = 13. Add shelf tips and hero pieces (+3): 15-16. Matches the grid method.
- 3x2: solid 0.25-0.33 m^2 -> 4.7-6.2 perfect, 8-10 at 60% efficiency, plus 2-3 shelf/hero = 10-13.

**Planning number 16 (3x3), 12 (3x2).** The number is driven by the cut strategy, not the area: cutting limbs along their length (long thin segments through the diagonal of the bed, up to ~320 mm) reduces count by 10-15% at the cost of longer seams through webbing. Rule of thumb: fewer cuts equals fewer visible seams. Plates: segments + ~3 extra plates for small parts (tips, whips, pins, straps).

### Printer-flex sensitivity
| Bed | Usable cell | 3x3 count (approx) |
|---|---|---|
| 220 x 220 (Ender class) | 195 | 20-26 |
| 256 x 256 | 230 | 12-20 (plan 16) |
| 350 x 350 | 320 | 7-10 |

Count scales roughly with 1/cell^2. A bigger printer is the highest-leverage cost lever.

## 2. Joint shortlist

Precedent from the task brief (not in this repo, source unverified, cite before relying): Hexa-Waves, a 35-panel wall piece assembled with glue plus connectors. It supports glued-and-connected modular panels at 2x our segment count; it does not carry plant loads.

| Joint | Where | Strength | Pros | Cons | Verdict |
|---|---|---|---|---|---|
| **Rear splice strap** (printed PETG or aluminum strap, M4 heat-set inserts, bolts from the back across the seam) | all body seams (flat back plane) | high, reversible | hidden; tolerant of misalignment; disassemble for repair/transport | needs flat coplanar back; inserts in thin walls | PRIMARY body seam |
| **Pin + socket + adhesive** (6 mm steel/fiberglass pins in 6.3 mm printed holes, epoxy/PU) | alignment + shear on every seam | medium (pins), high with adhesive | simple; aligns visually; works through lattice nodes | permanent when glued; hole tolerance | PRIMARY alignment, with bonded clearance 0.15 mm |
| **Sliding dovetail + adhesive** | shelf tip joint; hero pieces | high along axis | locks; no fasteners | needs 0.25 mm slip clearance, ~25 mm solid land; hard in lattice | SHELF TIP + selective |
| **Axial rod** (>= 8 mm steel/carbon through shelf tentacle at the tip joint) | shelf tip, strut | high in bending | takes tip moment (<= 8 N.m) | needs straight channel and solid nodes | REQUIRED at tip joints |
| **Printed cleat tongue (interlocking ledge)** | shelf root to cleat | per load model (fastener-governed) | integral hang | PETG/ASA only; layers along tongue | structural interface, not a seam joint |
| Glue only (butt) | none | low | easy | weak on thin webs | rejected |

Joint placement rules: off shelf roots (>= 100 mm), off the strut node and foot (>= 75 mm); land seams on solid nodes or through valleys, not through thin web strands; limit seam length crossing lattice.

## 3. Material plan

Consistent with load-model-v1 Sections 3-4: PETG/ASA on the load path, PLA only non-load decorative. Intel check: DECISIONS.md and round-03 contain no material-selection intel. The only PLA mention is a "hand-painted PLA finish" aesthetics note. PLA-creep is structural's engineering judgment (Tg 55-60 C, sustained allowable ~5 MPa vs 7-10 MPa PETG/ASA); not independently verified, no creep test run.

| Material | Density | Role | Notes |
|---|---|---|---|
| PETG | 1.27 g/cm^3 | **baseline: shelves, roots, struts, body, splice straps** | easy to print, moderate creep, Tg ~80 C, strings on lattice; paints/sands acceptably |
| ASA | 1.07 g/cm^3 | **upgrade if wall sees sun or radiator (>~50 C)** | warps; needs enclosure; ~15% lighter; fumes; cracks on thin walls |
| PLA | 1.24 g/cm^3 | decorative whips and trim only | easy; creeps near 50 C; no load path |
| Aluminum 6061 cleat | 2.70 g/cm^3 | wall cleat, 6 x 50 mm x 450+ mm per shelf | preferred over printed cleat (structural) |
| Steel/carbon rod, pins | | shelf tip joint, spine, seam pins | |

One material for the whole body keeps finish and paint adhesion uniform. Hardware: heat-set inserts, #10 x 2.5 in stud screws, washers, epoxy/PU adhesive.

Material finish is cheaper to decide on a board than to reprint (Section 6).

## 4. Print time (order of magnitude)

### Assumptions
- 0.4 mm nozzle, 0.2 mm layer height, 0.45 mm line width.
- 2-3 perimeters in decorative skin, 4 in the load path, infill 10-15% (gyroid) in solid mass, 100% local at the cleat seats and strut foot (load model Section 2).
- Mass from load model: 5-14 kg, nominal 9 kg; +5-10% joints/inserts -> 5.3-15.4 kg (nominal 9.7 kg).
- Supports add 20-40% extra deposited material and time (organic undercuts; Section 5). Use x1.3 nominal, x1.2 low, x1.4 high.
- Average effective throughput 30 g/h nominal (range 20-50 g/h). Basis: PETG 1.27 g/cm^3 at 4.5-11 mm^3/s averaged over detailed organic geometry with acceleration limits, retractions in lattice, and layer cooling. Hobby 256 mm printers peak higher on simple parts; lattice walls average lower. **Not measured on any real printer; a test patch is the first calibration.**
- Failures/reprints: +15% allowance not in the numbers below.

### Arithmetic
| Case | Mass printed | Rate | Hours | Printer-days (24 h) |
|---|---|---|---|---|
| Low | 5.3 kg x 1.2 = 6.4 kg | 50 g/h | 128 | 5.3 |
| **Nominal** | 9.7 kg x 1.3 = 12.6 kg | 30 g/h | 420 | **17.5** |
| High | 15.4 kg x 1.4 = 21.6 kg | 20 g/h | 1080 | 45 |

Per segment (16 segments, nominal): 12.6 kg / 16 = 0.79 kg, 26 h each, i.e. mostly overnight single-plate jobs; hero pieces and shelf roots with 100% local infill exceed 30-40 h. With +15% reprints nominal rises to ~20 printer-days.

Calendar time: 1 printer ~ 3 weeks continuous; 2 printers ~ 9-10 days; 3 printers ~ 1 week. Add finishing, assembly, paint: material-dependent, not estimated. Filament: ~13-15 kg of PETG, 13-15 spools (more with waste) of 1 kg.

## 5. Feasibility read: c01/c02 perforated webbing at scale

Basis: images read at ~1 px = 1.0-1.3 mm for a 914 mm piece. c01 is limbs with fenestrated webbing, hanging drips, perforated shelves, and a toothy maw with fine tooth/strand structure. c02 is a dense lattice sheet with ~20-80 mm voids, curling thin edges, loose strands, and a rust-ochre surface.

### Risk 1 (top): overhangs, undercuts, and supports in lattice
- Bridging: voids of 30-80 mm exceed bridge limits (PETG 20 mm, mesh-spec Section 2). Tops of voids need an arch/teardrop profile (<= 45 deg from vertical) or they sag.
- Undercut limbs: crossing limbs, tentacles overhanging the body, the maw interior (teeth, strands hanging in a cavity), and shelf undersides are undercut relative to a back-down print.
- Supports inside a perforated lattice are inaccessible: tree supports weld to thin strands, damage the surface, and can add the 20-40% material and hours assumed above. Dissolvable supports (dual-extruder PVA) would work but add cost, machine requirements, and failures.
- Mitigation (sculpt must obey): design relief as **2.5D with limited undercut**. Back face flat on the bed; every outward face self-supporting (<= 45 deg from vertical) for >= 90% of the down-facing area; voids arched; shelves printed top-down on the bed so their web underside rises without support; the maw printed as a separate hero piece with its own orientation. Accept supports only in marked, reachable zones.

### Risk 2: thin strands, fragility, resolution
- c02 fine web strands and c01 drips look 1-3 mm in the images: below the 2.0 mm decorative floor (3.0 mm near the load path). On a 0.4 mm nozzle, walls < 0.9 mm print as single lines or fail. Hair-like strands, fine teeth tips, and loose barbs in c02 are not printable and would break in handling.
- Z resolution: 0.2 mm layers are visible as stair-stepping on sloped webs; that may read as "calcified" or as "3D printed". Strand cross-sections of 2 mm print with 4-5 lines, poor surface.
- Mitigation: thicken strands ~2x relative to the concept images; replace fine hair with thicker "root" strands; keep sub-1.5 mm flourishes to a post-print add-on (resin, hot-glue web, paint) or omit. Handling: ship segments with seam-edge reinforcement; keep strands braced by cross-links (lattice, not dangling).
- Shell mass is also high: 1000s of strands x perimeters x travel moves leads to retraction/stringing in PETG and large time cost (Section 4 low-end rate).

### Risk 3: seams, tolerance stack, and flatness
- 16+ segments through web geometry: seam faces cut across strands leave weak, glue-poor joints; seam lines can show as straight cuts across an organic surface (c01 is a smooth-ish figure, c02 a continuous skin; both are unforgiving).
- Shrinkage and warp (ASA worst) accumulate ~2-6 mm over 4 segments if not compensated; large flat back faces can lift/warp, breaking the +-1 mm coplanarity needed for the cleat/bearing pad arrangement (mesh-spec Section 7).
- Mitigation: seam-ready solid knuckles, 0.15/0.25 mm clearances validated by a coupon, rear splice straps tolerate mismatch, print back-down, brims/enclosure for ASA, finish-fill plus paint (hand-painted finish noted in aesthetics) to hide seams.

### Other risks (lower)
- Gloss accent: layer lines show in gloss; the verdict is gloss accent-only.
- Shelf underside vs headroom: top-down printing yields clean planting surface but underside webs must be self-supporting.
- Creep of PETG shelves over service life (load model: tip deflection 1.2 mm initial, ~3 mm after creep); acceptable. Sunlit wall prompts ASA.

### Simplifications the sculpt will need (summary)
1. 2.5D relief with flat back and bounded undercut; no free-floating lattice in 3D.
2. Min strand 2.0 mm (3.0 near the load path), min void 6 mm, voids arched.
3. Webbing replaced by thicker rooted lattice; fine hairs, tooth tips, and drips omitted or post-added.
4. Maw as a separate hero piece.
5. Solid seam knuckles and cut-friendly zones.
6. Mask as a carved low-relief field rather than free-standing form (matches the r04 verdict anyway).

These simplifications will not reproduce c01/c02 literally. The sculpture will read as c01/c02 at a viewing distance of 1.5-3 m but not at 30 cm. A test patch (Section 6) is the correct gate.

## 6. Future Evan board probes

| Probe | Why | Card idea |
|---|---|---|
| **Seam visibility** | seam style is the highest-impact assembly decision; r04 rejected applied objects and loved carved mass | 4 comps: hidden in void, chamfered shadow-gap, filled-and-painted, deliberate strap/joint expression |
| **Material finish** | PETG matte vs painted vs aged-ochre vs bone-crust coating; layer-line tolerance; gloss accent-only | physical render or photo of a real test patch if produced; else generated comps |
| **Perforation density / lace fineness** | tradeoff between c02-like fine lacework and printable thickness; also mass/time | 3 densities rendered from the real mesh |
| **Layer height / surface smoothness** | 0.2 vs 0.12 mm is 1.7x print time | optional, low priority |
| Whips | whether decorative whips (PLA) are wanted | after geometry |

Audit RP-1 item 5 already calls for a seam-tolerance/material/finish card in round-05/06. These are the cards to put there; renders must come from real geometry or a honest test patch to avoid asking Evan about a surface that cannot be built.

## 7. Open items

- Machine lock: Evan's printer model and count. Bed size changes everything in Section 1.
- Throughput calibration: print the test patch (one limb, one shelf stub, 200 mm of web); measure g/h, strand survival, seam fit.
- Support strategy decision after the patch.
- Verify Hexa-Waves precedent source.

---
*Edit log*

| Date | Agent | Change | Signed-off-by |
|------|-------|--------|---------------|
| 2026-11-15 | fabrication-lead (via cad-lead) | Initial creation (segment count, joints, materials, print time, feasibility) | docs-reviewer (flagged: 3x2 range, spool count) |
