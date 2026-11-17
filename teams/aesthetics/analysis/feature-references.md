# Feature references and build specs (Evan r06 directives)

**Status:** [PROVISIONAL] Aesthetics analyst, 2026-11-17. Source: issue #6 notes on h3, h5, vb1, vb2. Inputs read: `teams/cad/fullpiece_v2_1/renders/{hero_rake,hero_maw,v2_tentacles5_front}.png`, `review/rounds/round-04/images/c01_baseline-velvet-salon.jpg`, `teams/fabrication/analysis/rp2-blind-pockets.md`.

## 0. Conventions and evidence grades

- **D** = mask face diameter. **W_p** = piece width (~914 mm). **s** = normalized 0..1 along a tentacle. All ratios are dimensionless; CAD scales them.
- Evidence grades: **[V]** = checked this session (Wikipedia page fetched through the proxy, fact read). **[U]** = URL returned HTTP 200 but only existence checked; the claim about the work is from analyst memory. **[M]** = from memory, no URL. Treat [M] as leads for the moodboard bot, not as facts.
- Numbers marked **[DERIVED]** are design values chosen by this analyst from the references plus the 3 m legibility rule below. They are not measurements of any source work. Anatomical values are approximate adult averages from memory (+-10%); anatomy is a ratio guide, not a medical spec.
- No images from any reference are stored in the repo. Links only.
- **3 m legibility rule [DERIVED]:** a feature reads at 3 m if its smallest dimension subtends >= 0.3 deg, i.e. >= 15 mm (3000 mm x tan 0.3 deg = 15.7 mm). Applies to the smiley stroke, eye whites, tentacle tips' visible width, and tooth crown width on the primary fangs. Finer detail is texture and reads only at <1 m.
- **Fab limits carried in** (`rp2-blind-pockets.md`): groove V >= 90 deg included; mouth width >= 2.0 mm (C3); pocket floor >= 2.6 mm (C5); walls lean <= 45 deg from vertical, no undercut (C2); mouths face print-up within 45 deg (C1); depth <= 3x mouth width default (C4); overhang limit 45 deg PETG / 40 deg ASA. Eyes only on outward-facing surfaces; lid chamfer <= 45 deg.

---

## 1. h3a/h3b/h3c: smiley face, hands, bone (mask assembly)

### 1.1 ICONIC SMILEY (h3b)

**What is wrong now** (`hero_rake.png`). Mask disc ~440 px across. Eyes are already vertical ovals, but each is ~0.11 D wide with soft, blurred edges and a gradient floor, so they read as shadows, not holes. The mouth is a thin (~0.045 D), tapering, blurry dark band; it shades into the cheek with no hard edge. The face surface carries a vertical seam, a chin crease, a cheek crease and mottled value breakup, so the three features compete with surface noise. The disc has no defined rim (it melts into surrounding flesh), and the top is partly covered by fingers. Net: low contrast, thin stroke, noisy field. That is "bland".

**Reference survey**

| Source | What to take | Grade |
|---|---|---|
| Harvey Ball, 1963 original | Three Wikipedia-documented signatures: narrow oval eyes (right one slightly larger), mouth not a perfect arc (creases at the sides, slightly off-center, right side higher and thicker), bright flat yellow. Drawn in ~10 min for State Mutual. The imperfection is part of the icon and is useful for horror asymmetry. https://en.wikipedia.org/wiki/Harvey_Ball | [V] |
| Smiley (ideogram) overview, WMCA "Good Guys" 1960s, Loufrani 1971 | Convergent design: flat disc, two solid dots/ovals, one bold arc. https://en.wikipedia.org/wiki/Smiley | [V] |
| Acid-house smiley (late 1980s) | Same glyph, maximum contrast, used as a mask-like face; shows the glyph survives distortion. https://en.wikipedia.org/wiki/Acid_house | [U] |
| Watchmen Comedian badge | Smiley with a single disfiguring mark; proves the glyph carries horror with one added insult. https://en.wikipedia.org/wiki/Comedian_(character) | [U] |
| c01 (round 04, loved) | Mask is a vertical oval, pale bone/clay, eyes small round dark holes, thin smile. Loved for the serene-uncanny read, not for the glyph fidelity. Evan now asks for the more iconic glyph. | in-repo |
| Bayon smiling faces (m01, loved in r04) | Monumental carved face; features are deep, wide-lipped, shadow-driven. Carving logic to copy. | in-repo / [M] |

**What makes it iconic, not bland [DERIVED from the above]:**
1. Only three features, nothing else on the field (no seam, no crease, no nose, no brow).
2. Bold, thick, constant stroke (no taper).
3. Maximum value contrast: recesses near black, face field pale and uniform (L* >= 75 field, <= 12 recess).
4. Hard edges: recess rim fillet <= 0.5 mm so the boundary reads as a line, not a gradient.
5. Features fill the disc: occupied area ~35-40% of the face, not 10%.
6. Keep Ball's small asymmetry (it is documented, it reads human-made, and it reads horror when carved).

**BUILD SPEC (all lengths x D; origin at disc center, +y up)**

| Element | Value |
|---|---|
| Disc | Circle D. Allowed squash: height <= 1.10 D (c01 oval echo), features scale with the ellipse. Face field gently domed: crown height 0.04 D above rim. Surface noise on the field <= 0.3 mm RMS; no creases, no seams. |
| Eyes (2) | Vertical ellipses. Left: width 0.090 D, height 0.210 D (aspect 2.33:1). Right: x1.06 (width 0.095 D, height 0.223 D). Centers at x = -0.165 D / +0.165 D (spacing 0.33 D), y = +0.160 D. Eye top at +0.265 D, bottom at +0.055 D. Right eye rotated 2 deg CW; left 0. |
| Smile centerline | Circular arc, radius r = 0.335 D, sweep 120 deg (half-angle 60 deg), center on the y axis at y = +0.0675 D so the endpoints sit at y = -0.080 D. Endpoint x = +-0.29 D. Lowest point y = -0.2475 D. Sagitta 0.1675 D. Chord (end to end centerline) 0.58 D. |
| Smile asymmetry (Ball) | Right endpoint raised 0.02 D (y = -0.060 D), left stays -0.080 D. Fit the arc through the three points (L end, bottom, R end) rather than keeping the symmetric circle. |
| Stroke | Constant 0.065 D on the left half, 0.072 D on the right half (blend over the bottom 20%). No taper. |
| End caps | Round (radius = half stroke). Add optional Ball cheek creases: one short arc per end, length 0.05 D, radius 0.05 D, curling upward-outward, same stroke width x0.5, same depth x0.7. |
| Clearances | Eye bottom (0.055 D) to mouth end top (-0.080 D + stroke/2 = -0.047 D): gap >= 0.10 D. Mouth outer edge to disc rim: >= 0.18 D. Eye top to rim >= 0.20 D. |
| 3 m rule | Stroke >= 15 mm -> **D >= 230 mm** (0.065 D = 15 mm). At D = 230: eye 21 x 48 mm, smile chord 133 mm, sagitta 39 mm. If D < 230, widen the stroke to 15 mm absolute and shrink clearances, do not shrink the stroke. |

**Carving in relief (carved bone, not painted)**
- Features are recesses in the disc. Mouth: flat-floor U-groove, floor width = stroke - 2 x wall run; walls 30 deg from vertical (inside the C2 45 deg limit, wider than the 90 deg V floor). Depth = 0.5 x stroke width (7.5 mm at 15 mm stroke); never less than 0.4 x width or the groove reads as a gray line.
- Eyes: elliptical flat-floor pockets, walls 20-30 deg from vertical, depth = 0.5 x minor width (~10 mm at D = 230). Floor >= 2.6 mm above build plane (C5).
- Mouth width 15 mm >= 2.0 mm (C3) and depth 7.5 mm <= 3x width (C4); both pass without relaxation. Wider grooves instead of deeper ones is the fab lever.
- Rim fillet <= 0.5 mm on all feature edges; floors matte-dark in finish (wash pools in the recess, fab doc: wash the pockets, spray the crests). Geometry alone must hold the read; paint is the bonus.
- Light: overhead/raking light. A 7-10 mm deep recess of this width is fully shadowed under typical 45-70 deg downlight; if CAD's renderer shows them gray, increase depth to 0.7 x width within C4.
- Rim of the disc: a distinct raised bezel, width 0.04 D, height 0.03 D, crisp both sides; this is what lets the disc read as an object seated in flesh (see 1.3).

### 1.2 HANDS (h3a)

**What is wrong now** (`hero_rake.png`). About seven finger-like digits enter from the top, left, and bottom-right at unrelated angles. No palm, no metacarpals, no wrist, no knuckle structure; each digit is a uniform sausage. Digit thickness varies 2:1 with no logic. The pale value jumps abruptly mid-finger (reads as a paint-dipped tip, not bone). There is no nail and no dorsal/palmar logic, so the viewer cannot tell which way a hand faces. "Sporadic" = unrelated axes + no grouping into hands.

**Reference survey**

| Source | What to take | Grade |
|---|---|---|
| Pale Man, Pan's Labyrinth (del Toro, 2006) | Gaunt elongated fingers, taut skin over bone, long joints, strict hand anatomy kept. https://en.wikipedia.org/wiki/Pan%27s_Labyrinth | [U]; creature detail [M] |
| Nosferatu (1922), Count Orlok | Elongated fingers with long curved nails; a canonical "same hand, too long". https://en.wikipedia.org/wiki/Nosferatu | [U] |
| Slender Man | Elongation by uniform scaling of limbs, not by adding joints. https://en.wikipedia.org/wiki/Slender_Man | [U] |
| Arachnodactyly (real condition) | Believable elongation: phalanges and metacarpals lengthen, joint order and count unchanged, digits slim. https://en.wikipedia.org/wiki/Arachnodactyly | [U] |
| Giger biomechanical work | Bone-like fingers fused with tubing; clean continuous bone surfaces with knuckle bulbs. https://en.wikipedia.org/wiki/H._R._Giger | [U]; specific works [M] |
| Beksinski | Emaciated skeletal figures, taut membranes over bone, no ornamental texture on bone. https://en.wikipedia.org/wiki/Zdzis%C5%82aw_Beksi%C5%84ski | [U]; specifics [M] |
| Phalanx / metacarpal anatomy | Joint order and bone lengths. https://en.wikipedia.org/wiki/Phalanx_bone , https://en.wikipedia.org/wiki/Metacarpal_bones | [U] |
| Durer, Study of Praying Hands (c.1508); Bridgman/Loomis hand construction | Classic hand-anatomy drawing references for a sculptor/CAD reviewer. https://en.wikipedia.org/wiki/Albrecht_D%C3%BCrer | [U]; works [M] |
| The Thing (1982) | Hands/limbs that deform while staying readable as the base anatomy. https://en.wikipedia.org/wiki/The_Thing_(1982_film) | [U] |

**BUILD SPEC**

*Count and placement.* Two hands, one on each side, dorsum (back of hand) facing the viewer, fingers pointing at the disc center. Wrists emerge from the flesh mass outside the disc.
- Hand A: arrives from outside at **10:30** (wrist at ~315 deg compass-from-up = upper-left), fingertips land on the rim arc **9:45-11:15** (arc ~45 deg of the rim).
- Hand B: arrives at **1:30**, tips land on **12:45-2:15**.
- Handedness rule (determines thumb side): dorsum-up, fingers toward center. Hand A = RIGHT hand, thumb on the top side (toward 12). Hand B = LEFT hand, thumb on the top side. Both thumbs point toward the crown of the disc. Do not mirror exactly: B is 0.92 x scale, wrist rotated +8 deg, curl angles +/-10 deg different. Exact mirror = "clip-art".
- Thumb: rests on the rim crest, tip lands on the face ~0.08 D inward of the rim. No digit outside this hand set. No stray fingers anywhere else on the piece (the shelves' fingers are a separate question; fingers on shelves must follow 1.2 handedness rules or be removed).
- Face clear zone: all fingertips and distal phalanges stay >= 0.09 D clear of eye boxes (eye top at 0.265 D; fingertip inner reach <= 0.36 D from center at the 12 o'clock side). The face glyph must read >= 85% unobstructed.

*Scale.* Build the hand in real-proportion units (mm at D = 200) then multiply by D/200 and by the elongation factors below. Hand length wrist to middle fingertip ends ~1.3-1.5 D.

*Skeleton table (average adult bone lengths, mm, +-10%; [M] from anthropometric norms).*

| Digit | Metacarpal | Proximal | Middle | Distal | P:M:D |
|---|---|---|---|---|---|
| Index | 66 | 40 | 23 | 18 | 1 : 0.58 : 0.45 |
| Middle | 63 | 44 | 27 | 19 | 1 : 0.61 : 0.43 |
| Ring | 56 | 41 | 26 | 19 | 1 : 0.63 : 0.46 |
| Little | 52 | 31 | 17 | 16 | 1 : 0.55 : 0.52 |
| Thumb | 46 | 32 (prox.) | - | 25 (dist.) | 1 : - : 0.78 |

Fingertip length order: middle > index ~ ring > little (tips form a shallow arc). Knuckle (MCP) arch: middle highest, index and ring ~2 mm lower, little ~6 mm lower. Thumb has 2 phalanges only; its CMC joint sits at the wrist side, with the thumb metacarpal axis rotated ~45-60 deg out of the palm plane (opposed).

*Elongation (believable).* Multiply every phalanx x1.6 (keep P:M:D ratios; optionally middle x1.7 and distal x1.8 for a "reaching" look, but do not exceed 1.9). Multiply metacarpals x1.25-1.30. Multiply shaft thickness x0.60-0.65 of real. Keep joint heads at x0.85 of real: shaft:joint ratio ~1 : 1.4 gives visible knuckle bulbs (the "bony" read). Do not add phalanges, do not curve the bone shafts sideways, do not branch fingers. Total hand length x1.4-1.5 of real is the ceiling before it reads as a rake.

*Finger geometry.*
- Cross-section of each phalanx: ellipse, dorsal-palmar depth 0.8 x lateral width. Distal phalanx tapers to a pointed pad, ending in a **nail** (dorsal): long, narrow, curved, 0.5 x distal length, dark (bone-brown or near-black) with a crisp edge.
- Joints: knuckle bulbs at MCP, PIP, DIP: spheroid width 1.4 x shaft, length 0.5 x shaft width along the axis. Each knuckle ringed by 1-2 transverse skin folds on the dorsum (tight skin, 1.0-1.5 mm raised ridges; fab: widths >= 2 mm to print, else paint).
- Flexion planes: each finger's three phalanges lie in one plane (finger axis + surface normal). Abduction only at the MCP. Joints flex only toward the palm side; no hyperextension.
- Finger axes inside one hand converge toward a common point near the disc center. Gap between adjacent finger axes 6-10 deg (gripping) / 10-15 deg (rest). Finger-to-finger clear gap >= 3 mm (visible dark seam).

*Grip pose (flexion angles, rim crest at the PIP, fingers crossing a 12-20 mm high rim wall onto the face):*

| Digit | MCP | PIP | DIP |
|---|---|---|---|
| Index | 20 deg | 55 deg | 25 deg |
| Middle | 22 deg | 62 deg | 30 deg |
| Ring | 26 deg | 70 deg | 35 deg |
| Little | 30 deg | 80 deg | 40 deg |
| Thumb (MCP / IP) | 15 / 30 deg | - | - |

Each finger from index to little adds +4 deg MCP and +8-10 deg PIP (finger cascade, the signature of a real grip). Rule: proximal phalanx lies on the rim crest and outer flank; PIP knuckle at the crest; middle phalanx on the inner rim wall; only the distal phalanx plus <= 1/3 of the middle phalanx touches the face. Tip pad indents the face 1-2 mm; nail faces the viewer at 40-60 deg to the face plane.

*Dorsum structure (the "bony, not sausage" read).* Dorsum is a gaunt fan: four extensor tendon ridges (width 2-3 mm x scale, height 1.5 mm) from the wrist to each MCP knuckle; hollows (interosseous valleys) between metacarpals 3-6 mm deep; wrist narrows to 0.55 x palm width with two visible bone bumps (ulnar styloid, radial). Skin = taut sheet stretched ridge to ridge: smooth, no wrinkles except the knuckle folds.

*Bone vs skin on the hand.* Skin material = body flesh palette. Knuckle caps and nails use bone palette (section 1.3), but only on **anatomically exposed bone**: the three knuckle heads per finger and the wrist bumps, each as a cap that is a smooth continuation of the finger surface with a crisp thin margin (0.6 mm-wide dark line). No pale band on mid-shaft (this is the current paint-dip failure). Whole-finger pale = acceptable if the hand is "skeletal"; do not mix.

*Fab.* Finger widths after x0.62: proximal shaft ~11 mm real-scale, x D/200 -> ~12.5 mm at D = 230; gaps >= 3 mm; nail edges 1 mm min feature (paint carries nail edge). Keep fingertip pad axes within 40 deg of +z (print-up): fingers hook over a rim with pad pointing toward the wall, so shape the tips' underside as a flat chamfer <= 45 deg; confirm with fab.

### 1.3 BONE vs TEXTURE (h3c)

**What is wrong now.** Bone-white parts (fingertips, mask, ridge shards, teeth) carry the same noisy displacement as flesh and share the flesh mesh, so the only difference is a color step. The grain makes ivory read as suede, and the cut boundary is arbitrary.

**Reference survey**

| Source | What to take | Grade |
|---|---|---|
| Giger "biomechanical" skulls and ribs | Bone as smooth, continuous, curvy surface over a textured ground. | [M]; https://en.wikipedia.org/wiki/H._R._Giger [U] |
| Beksinski dystopian paintings | Ivory bone, exposed knuckles and ribs, against decayed dark ground. | [M] |
| Real bone anatomy | Cortical bone: smooth, dense, slightly glossy; flesh: pitted, folded. https://en.wikipedia.org/wiki/Bone | [U] |
| Bloodborne: bone-white beast claws/horns on dark-blue-black flesh | Value separation + smooth against rough. | [M] |
| The Thing: spidered bone protrusions through wet flesh | Bone emerges from flesh with a wet dark margin. | [M] |
| Anglerfish/viperfish teeth | Translucent-smooth enamel against dark gum. https://en.wikipedia.org/wiki/Viperfish | [V] |

**BUILD SPEC (rules)**
1. **Surface:** bone = zero grain. Displacement noise amplitude on bone <= 0.2 mm, wavelength >= 40 mm (a gentle lump), vs flesh 1-4 mm amplitude across 3-30 mm wavelengths. The gate2 note says grain <= 1.0 mm does not print; use the saved resolution for smoothness. Bone must be the smoothest surface in the piece.
2. **Edges:** crisp. Bone silhouettes break at a clean edge: fillet <= 1.0 mm (<= 0.5 mm on teeth/nails). Flesh edges are rounded >= 3 mm.
3. **Value:** pale ivory (L* 82-90, slight yellow, #E4D8C0 +-), flesh L* 30-50. Tonal gap >= 35 L*. No intermediate value ramp on bone: no gradient dirt except in cervical/cleft crevices, painted.
4. **Gloss:** bone = satin/semi-gloss (clear coat); flesh = matte. The highlight is the second separator.
5. **Margin:** bone is separated from flesh by a dark margin: either (a) an undercut-free groove 1.5-3 mm wide, 1-2 mm deep, V >= 90 deg, rimmed by a flesh swell 1-2 mm high (flesh gathers up against bone), or (b) a swollen flesh collar at the junction. Do not let bone surface and flesh surface be flush. Fab: groove width >= 2.0 mm (C3).
6. **Continuity:** a bone element is one convex(ish) continuous shape from end to end (no stepped value inside it, no texture patches). A bone that is partly buried stops where flesh covers it, with a margin as in rule 5.
7. **Where bone appears:** mask disc, knuckle caps and nails, teeth/fangs, a limited number of spines/rib shards (<= 8). Not on the tentacles or body.
8. **Allocation:** bone <= 12% of the surface area, so it reads as intentional accents; flesh remains the field.
9. **CAD implementation:** a separate "bone" SDF region with its own displacement field (amplitude ~0), unioned with a smooth-min k = 1.5 mm into the flesh, plus a flesh-side bulge ring 2 mm wide on the contact curve. Tag faces by material id for painting.

---

## 2. h5: maw (mouth)

**What is wrong now** (`hero_maw.png`, `v2_tentacles5_front.png`).
- Opening is near-round (~1.2:1 wide:tall in the close render; ~1.1:1 in the full front), set in a bulging ring, ~21% of W_p wide. A round hole reads as a lamprey sucker or a porthole, not a mouth. No corner commissures, no upper/lower jaw logic, no lip shape.
- Teeth: bulbous rounded pegs (rounded-cone/thumb shapes, base ~ 0.7 x length), one ring of nearly uniform size, no crown/root distinction, no gum line (they sit on a thin pale rim with a frosted white fringe), no wear, no recurved fangs, uniform spacing. They read as knuckles or grapes.
- Four thin ivory strands cross the opening (the "throat strands" Evan wants removed); they also stand out as straight sticks with unconnected ends.
- Interior is a mottled flat dark wall with no depth gradient, so the cavity does not feel deep.

**Reference survey**

| Source | What to take | Grade |
|---|---|---|
| c01 (loved) | Tall vertical oval maw below the mask, ~1 : 1.15-1.3 w:h, hooked fangs converging inward from both sides, dark throat. The mouth is the dominant lower-body feature. | in-repo |
| H.R. Giger, Alien/xenomorph (1979), Necronom series | Long jaw, rows of needle teeth that recede in depth, tongue/inner jaw. Mouths are anatomically structured: lips, gum shelf, palate. https://en.wikipedia.org/wiki/H._R._Giger , https://en.wikipedia.org/wiki/Xenomorph | [U]; details [M] |
| The Thing (1982), chest-mouth (Dr. Copper scene) | A mouth in a torso: vertical split, wet flesh, irregular teeth, lips that tear. Matches the "mouth set in body" brief. https://en.wikipedia.org/wiki/The_Thing_(1982_film) | [U]; scene [M] |
| Junji Ito | Mouths wider than anatomical, each tooth individually inked and different, gums drawn, no strand clutter. https://en.wikipedia.org/wiki/Junji_Ito | [U]; specifics [M] |
| Berserk (Miura) apostle designs | Human jaw taken past its limit: distended gape, irregular tusk-teeth. https://en.wikipedia.org/wiki/Berserk_(manga) | [U]; [M] |
| Bloodborne (FromSoftware) | Beast jaws with long irregular fangs, heavy gums. https://en.wikipedia.org/wiki/Bloodborne | [U]; [M] |
| Annihilation (2018) | Mouth-in-wrong-place biology (the bear-skull creature) with human-scale teeth detail. https://en.wikipedia.org/wiki/Annihilation_(film) | [U]; [M] |
| Silent Hill | Mouth-less or maw-like heads with flat-cut tooth rows. https://en.wikipedia.org/wiki/Silent_Hill | [U]; [M] |
| Sarlacc / lamprey | Radial teeth into a funnel; rows recede into the throat. https://en.wikipedia.org/wiki/Sarlacc , https://en.wikipedia.org/wiki/Lamprey | [U] |
| Viperfish | Fangs so long they would pierce the brain if misaligned; wide-opening loose jaw. https://en.wikipedia.org/wiki/Viperfish | [V] |
| Anglerfish | Wide mouth around the front of the head; bands of inwardly inclined, hinged teeth. https://en.wikipedia.org/wiki/Anglerfish | [V] |
| Goblin shark | Large parabolic mouth; prominent nail-like teeth, protrusible jaws; fangs front, flatter teeth behind. https://en.wikipedia.org/wiki/Goblin_shark | [V] (nail-like, parabolic); front/rear tooth difference [M] |
| Human dentition | Counts: 8 incisors, 4 canines, 8 premolars, 12 molars; canine has the longest root; gingiva with papillae. https://en.wikipedia.org/wiki/Tooth , https://en.wikipedia.org/wiki/Gingiva | [U]; counts [M] |

**BUILD SPEC**

*Opening shape and size (relative to the mask D and W_p).*
- Orientation: **vertical** (matches c01, which Evan loved). Lens/almond with a heavier upper third (widest point 40% from the top), pointed commissures at top and bottom, not an ellipse.
- Width : height = **1 : 1.5** (allowed 1 : 1.35 to 1 : 1.7). Current 1.1 : 1 is wrong in both aspect and orientation.
- Size: width = **1.0-1.15 D** (230-265 mm at D = 230), height 1.5 x width (345-400 mm). Piece-width share ~26-29% (current 21%). Top of the opening sits 0.15-0.25 D below the mask bottom; the mouth is on the body axis, the mask above it. Check the fab area: depth of cavity <= 3 x mouth width (C4) is satisfied (<= 700 mm); use depth 55-75 mm.
- Outline superellipse: |x/a|^2.4 + |y/b|^2.4 = 1 on the heavier upper half, then pinch to commissure points over the last 12% of height each end. Add 4-6% asymmetry (left side 3-5% longer than right; commissure offset 0.03 W).

*Lips and gums.*
- Lip: rolled flesh rim, thickness 0.10-0.14 x W (25-35 mm), thickest at mid-height, tapering to 0 at the commissures. Lip outer surface smooth with 2-3 radial wrinkle creases at the commissures (0.4 W long). Lip crest is the flesh-to-mouth transition; no frosted/pale fringe.
- Gum shelf: band 0.05-0.07 W (12-18 mm) wide along both lateral jaws, lying on a slope <= 25 deg from the viewing axis (keeps teeth axes within the print overhang limit, below), dark maroon, wet gloss. Gum margin is a scalloped line: arch height 1.5-2 mm between teeth and a triangular papilla (2-3 mm) filling each interdental gap.
- Interior: deep smooth black-brown void, no strands. Darken with depth: 0 to 100% darkening across the first 0.4 W. Optional: 4-6 palate rugae (transverse ribs, spacing ~0.05 W, height 2 mm) on the upper wall, and a single tongue-like ridge down the center is allowed but **no strands, no filaments, no tendon sticks**. Wall angle <= 45 deg from vertical, no undercut (C2).

*Tooth layout (jaws run down the left and right sides; the opening is vertical).*
- Rows: **2 rows per side**. Front row: 9-11 teeth per side (18-22 total). Second row set 0.45 x tooth spacing behind and offset half a pitch, 5-7 per side (10-14 total), each 0.6-0.7 x the front-row neighbor length. Total visible: 28-36 (not 12 uniform pegs).
- Row curvature: both rows follow the lips' curve; teeth lie on the gum shelf with the row parameterized by arclength along the lip. Back row conforms to the same curve offset inward, so perspective rows narrow toward the commissures.
- Size gradient: length L(u), u in [-1, 1] along the row (0 at the widest point): L(u) = L_max x (0.22 + 0.78 x (1 - u^2)^1.3). L_max (primary fangs) = **0.28-0.32 x W** (65-75 mm at W = 235). Corner teeth ~0.2 x L_max, with the last 2-3 teeth tiny needles (0.08-0.12 W).
- Primary fangs: 2 canines per side, **at 28% and 72% of the row**, x1.45 neighbors, recurved 15-25 deg toward the throat. Between them: shorter incisor-like (flat-edge) or conical teeth 0.55-0.75 x L_max. Corner teeth: fish-like needles (viperfish, goblin shark): length 4-6 x base diameter, smooth, inward-inclined.
- Spacing: pitch = 1.1-1.5 x tooth base width; jitter +-20%; crowding at one commissure (pitch 0.7x), a gap at the other.
- Variation (biological asymmetry): axis tilt jitter +-8 deg about the row normal; length jitter +-15%; one tooth per row missing or snapped (broken tooth has a flat/ragged top at 60% of its length; the gum has a socket dimple); 2-3 teeth with chipped tips (0.5-1.5 mm flat); one doubled tooth (two crowns, one root). Left and right jaws not symmetric in count (e.g., 10 vs 9).

*Tooth geometry (the believable-tooth rules).*
- Crown: flattened cone/blade, not a round peg. Cross-section at base: ellipse, lateral width : depth = 1 : 0.65-0.75 (i.e., a blade). Two keel edges (front and back) 0.5-1.0 mm sharp from base to tip; tip radius 0.6-1.0 mm (printable) with point axis offset toward the back by 5-12%.
- Taper: base-diameter-to-length 1 : 3 (molar-like/incisor shapes use 1 : 1.5-1 : 2), fangs 1 : 4-1 : 5, corner needles 1 : 6-1 : 8. **Base width = L / 4 = 16-19 mm at fang length 70 mm** (about 0.07 W).
- Recurve: 10-25 deg tip curl toward the throat; a tooth centerline = circular arc, radius 1.2-2.0 x length.
- Root: 40-60% of total tooth length is buried (the crown seen above the gum is 0.5-0.6 of total). Emerges through a sulcus: a 1-1.5 mm wide dark groove ringing the base, gum rolls up around the base 2-4 mm (gingival collar).
- Enamel surface: smooth, semi-gloss, 1-2 shallow vertical ridges (0.3 mm) only; wear flats on 20% of teeth; cervical staining (dark yellow-brown 15-25% of crown from the gum, painted).
- Layout orientation: tooth axes tilt from the gum normal by 5-20 deg toward the mouth center. **Fab:** gum shelf slope <= 25 deg from print-up plus tooth lean <= 20 deg = 45 deg max total; recurve must keep every tooth tangent within 40-45 deg of +z. If a fang needs more lean, shorten its inward reach or add a tapered support rib on the gum.
- Min feature: tip radius >= 0.6 mm; gap between neighboring crowns >= 2.0 mm at half-height (C3); needle teeth base >= 3 mm.

*Don't:* strands, filaments, a uniform ring, round teeth, pale frosted fringe, a round opening.

---

## 3. vb1: eyes

**What is wrong now** (`hero_maw.png`, `v2_tentacles5_front.png`). Eyes are flat white almond decals pressed on the skin: lid line is a thin ring at the surface, sclera is flush (no globe protrusion), pupil is a small dark dot on a flat plane, edges hard and bright as a sticker. All in clean groups of 4-6, same size, same orientation, and set in rows. No socket, no skin stretch, no lid thickness. Eyes are tiny on the piece (3-4 px at full view), so at 3 m they read as noise dots.

**Reference survey**

| Source | What to take | Grade |
|---|---|---|
| Junji Ito | Over-wide eyes: tiny pupils floating in wide white sclera, ring of white visible around the iris; stare reads instantly. https://en.wikipedia.org/wiki/Junji_Ito | [U]; [M] |
| Bloodborne (Amygdala, many eyes on a body; Moon Presence imagery) | Eyes studded on limbs/head in clusters of different sizes. | [M] (the Amygdala wiki URL tried returned 404) |
| Exophthalmos (bulging eyes), real | Sclera visible above the iris, lids retracted, globe protrudes beyond the orbital rim. https://en.wikipedia.org/wiki/Exophthalmos | [U] |
| Sclera anatomy | https://en.wikipedia.org/wiki/Sclera | [U] |
| Chameleon, frog, pufferfish | "Turret" eye: globe in a conical flesh mound, lid fused to the globe leaving only a pupil aperture; flesh-wrapped, not plastered. https://en.wikipedia.org/wiki/Chameleon | [U]; [M] |
| Prosthetic SFX eyes (The Thing, An American Werewolf in London, Pan's Labyrinth Pale Man palm eyes) | Resin/acrylic eyes with glossy clear cornea, tinted yellowed sclera, painted vein network, slightly overscaled globe. | [M] |
| Beksinski, Giger | Sparse eyes: one or two, set deep in a socket under a heavy brow. | [M] |

**BUILD SPEC** (all in units of **G** = globe diameter; G >= 20 mm so the pupil clears the 2 mm pocket rule)

*Globe and protrusion.*
- Globe is a sphere radius r = G/2. Protrusion p above the surrounding flesh = **0.8 r to 1.0 r** (1.0 r = hemisphere, the printable maximum: no region beyond hemisphere, as that overhangs > 45 deg; C2). Current is ~0.1 r.
- Cornea: a secondary dome on the front of the globe, radius 0.55 r, height 0.10-0.14 G (real cornea sits ~0.12 G proud of the sclera). This is the highlight carrier.
- Sclera exposure: lids retracted, **visible sclera ring all around the iris** (the Ito look): iris diameter = 0.36-0.45 G, so the visible sclera band around it >= 0.2 G on the narrowest side. Iris offset from center by 0.05-0.15 G (gaze), different in each eye.
- Pupil: choose per cluster: (a) pinpoint, 0.12-0.18 x iris diameter (creepy stare); (b) horizontal slit, width 0.65 x iris, height 0.18 x iris (cephalopod/goat). Pupil as a recess: diameter >= 3.5 mm (C3: >= 2.0 mm), depth 2-3 mm, flat floor >= 2.6 mm remaining; iris as a 0.8-1.0 mm shallow ring recess (step between iris and sclera, so a painted ring has an edge to follow).
- Cornea finish: clear gloss varnish on the globe alone; sclera tinted off-white/yellow (#E8DFC0 +-), not pure white. Veins and redness at the lid corners **by paint** (veins < 1.0 mm do not print).

*Lids and socket (where "plastered" gets fixed).*
- **Eyes sit in flesh:** a collar of flesh ringing the globe: width 0.25-0.40 G, raised to 55-70% of the globe protrusion at the globe edge, blending outward over >= 0.5 G with radius >= 0.3 G. So the flesh swells up and around the globe.
- **Lids** (choose one per eye, mix across the cluster):
  - Tight-retracted (terror/bulging): upper lid margin 0.08-0.12 G above the iris top (covers <= 5% of the globe), lower lid margin 0.10-0.15 G below the iris bottom; lid rim thickness 0.08-0.12 G, rolled outward, with a crisp inner margin. Lid opening width 1.05-1.25 G, height 0.85-1.0 G (nearly round: exposure of the whole globe, plus corners).
  - Heavy-hooded (sleepy horror): upper lid covers 25-40% of the globe, thick (0.15-0.20 G) with a deep supratarsal fold 0.2 G above the lid margin; lower lid slightly pushed up 0.05 G. Opening height 0.55-0.7 G.
  - Turret (frog/chameleon): lid fused to the globe, one pupil aperture, flesh cone 0.8-1.0 G tall.
- Socket rim: a raised rim around the lids, 0.06-0.10 G wide, 0.05-0.08 G high; around it a dark margin (groove 2 mm wide, V >= 90 deg) so the eye reads as a separate organ in a socket.
- Skin tension: 5-9 radial stress creases radiating from the lid corners, length 0.3-0.6 G, width >= 2 mm (print), depth 1-2 mm, spaced irregularly; creases follow the flesh flow (+-15 deg).
- Fab: eyes on outward-facing surfaces only (mouth normal within 45 deg of print-up). Lid chamfer <= 45 deg: lid overhang over the globe is the one risk; implement the upper lid as a ramp from the globe up at <= 45 deg (not a hood), so shadow comes from the groove below and the globe's own curvature. Heavy-hooded lids are acceptable only as <= 45 deg ramps.

*Clustering (organic, not stickers).*
- Cluster size 3-7 globes; size distribution log-normal: 1 dominant at G_max, 2 at 0.65, 2 at 0.4, 1-2 at 0.25. G_max = 38-55 mm (**not smaller than 20 mm for any**). Smallest-to-largest >= 1:3.
- Spacing: neighboring globes at 0.15-0.5 G apart; two merge collars (shared flesh) rather than a gap. Positions follow a ridge line or a spiral, not a grid; no straight rows of more than 2.
- Orientation: lid axes tangential to the local flesh flow +-15 deg, individual tilt jitter +-30 deg; gaze directions not parallel (at most two within 20 deg).
- Total eye count: **<= 12 on the whole piece**, 3-4 clusters, one of which is in the region right above the maw (framing). Fewer, larger eyes beats many small ones (current ~15 tiny).
- Cluster centers should avoid shelf edges and structural ribs.

---

## 4. vb2: tentacles

**What is wrong now** (`v2_tentacles5_front.png`). The lower body is a mass of 3-4 lumps ~1-1.5 widths long, with blunt ends, no consistent taper, no S-curve, and no negative space between them; they read as a blob. The shelf arms are rectangular slabs (shelves) with stub fingers, not tentacles. The upper-right wing and the left leg are separate lumps. Silhouette outline has jagged flaps (loose "ribbons") rather than a limb silhouette. Surface cues along the length: none (just the same mottling as the body).

**Reference survey**

| Source | What to take | Grade |
|---|---|---|
| c01 (loved) | Five long limbs: two shelf arms (S-curved up-and-out), three lower tentacles with large S-curves, thin curling tips; strong negative space between limbs; texture is rope/root fiber aligned with the limb axis. Limbs are 8-10x longer than wide. | in-repo |
| Tree-root architecture, Ta Prohm strangler figs | Root-like limbs: taper, branch, fiber ridges along the length; reads as tentacle without being an octopus. https://en.wikipedia.org/wiki/Ta_Prohm | [U] |
| Hokusai, The Dream of the Fisherman's Wife (1814) | Classic legible tentacle: smooth taper, sucker rows only on the inner face, strong S-curves. https://en.wikipedia.org/wiki/The_Dream_of_the_Fisherman%27s_Wife | [U] |
| Kraken illustration (Denys de Montfort, 1801) | Tentacle read at scale: long, tapering, coiling over a ship. https://en.wikipedia.org/wiki/Kraken , https://en.wikipedia.org/wiki/Pierre_Denys_de_Montfort | [U] |
| Cthulhu | The silhouette archetype (tentacled face), but r04 said less octopus-literal. https://en.wikipedia.org/wiki/Cthulhu | [U] |
| Giger | Tubular limbs with ribbed (annular) surface, no suckers. https://en.wikipedia.org/wiki/H._R._Giger | [U]; [M] |
| Giant squid | Tentacle club with stalked suckers/hooks near the tip, thin stalk; tip is different from the shaft. https://en.wikipedia.org/wiki/Giant_squid | [U]; [M] |
| Beksinski | Organic, flowing, sleek limbs rather than a lumpy blob. | [M] |

**BUILD SPEC**

*Count and layout (c01 pattern).* 5 limbs minimum clearly readable: 2 shelf arms (upper-left and upper-right, each holding a pot, as in c01), 3 lower tentacles fanning down/out. **At least 3 lower limbs, each independently traceable root to tip.** Angular separation of axes at the roots >= 25 deg (>= 35 deg preferred). Their free tips reach: lengths 0.35-0.55 x W_p (320-500 mm).

*Taper (root to tip), width w(s) with s in [0,1] from root to tip, w0 = root width 0.10-0.14 x W_p (90-130 mm).*
- **w(s) = w0 x (1 - s)^0.75 for s <= 0.88; then linear to w_tip = 0.04 w0 at s = 1**. Width at s = 0.5 ~ 0.6 w0; at s = 0.8 ~ 0.29 w0. Floor: w >= 6 mm everywhere except the last 5% (min 3 mm tip; fab 2.0 mm rule for ridges).
- Length : root width = **6 : 1 to 10 : 1** (current ~1.5 : 1).
- Taper is monotonic: no bulges, no re-widening, except the root flare (below).
- Root flare: the first 12% of length flares to 1.25 w0 and merges into the body with a fillet of radius 0.5 w0; the body edge continues into the tentacle edge (tangent continuity, no step).

*Centerline.* One dominant S-curve plus a tip curl:
- Lateral amplitude 0.25-0.35 x length; 1.5 half-waves along the shaft; curvature peaks at the first inflection (s ~ 0.35) and again at the tip.
- Tip curl: last 10-15% of length wraps 180-270 deg, radius 1.5-3 x local tip width (log-spiral), curling in the same direction as the last half-wave, away from the wall at most 15 mm (fab).
- No two adjacent tentacles with the same curvature sign for more than 30% of their length (parallel limbs read as a ribbon). Mix: one S-left, one S-right, one with a hook.
- Coplanar with the wall plane for 60%+ of length; allow lift off the wall for the last 40% (the shadow cue).

*Cross-section.* Half-ellipse, base width w(s) on the wall, height 0.45-0.60 w(s) at the root, down to 0.40 w(s) at the tip; keep the aspect ratio nearly constant along the length (rule: height/width varies by <= 20% across s). Flanks are steep (65-85 deg) near the edges, rounding on the crest, so the limb casts a shadow line on each side. Fab: flank <= 90 deg (vertical, no undercut), mouths of flank cavities per C6.

*Silhouette and negative space (legibility at 3 m).*
- Between adjacent tentacles the gap >= 0.5 x local width and >= 25 mm along the whole length except at the roots.
- Each tentacle's silhouette is a clean single-valued outline (no side lobes); drop secondary flaps and ribbons within 1.0 w of a tentacle. Remove the lumps present in the current render.
- Hierarchy: the tentacle count and taper must be readable in a 200 px thumbnail of the front view (squint test); if the lower half reads as one blob there, fail.
- Value: tentacles slightly paler on their crest (+8 L*) than the body, with a dark margin at both flanks, so edges are traced by a line of shadow.

*Surface cues along the length (not octopus-literal).*
- **Primary cue (c01 fiber):** 3-5 longitudinal ridges along the axis (cord/tendon look), ridge width 0.12-0.16 w(s), 2.0 mm min, spacing ~ equal, converging as the limb tapers. Heightmap amplitude 0.04 w. This matches c01's rope-root look and avoids the octopus.
- **Secondary cue:** annular rings ("segment bands") every 0.6 x local width along the lower 2/3 of two of the three lower tentacles; groove depth 0.04 w, width >= 2.0 mm, V >= 90 deg; stop before the tip.
- **Suckers:** one row only, on the **inner (concave) side** of the curve, on at most one tentacle (the hooking one): cup diameter 0.5-0.55 w(s), pitch 0.9-1.1 x w(s), shallow recess depth 0.25 x diameter, raised rim 1.0 mm. 10-16 suckers, ending 20% before the tip. Fab: cup diameter >= 6 mm.
- **Optional:** 2-3 small hooked spines near the tip of the hooking tentacle (squid club logic), each 8-12 mm.
- Do not: two sucker rows, uniform bead-like rows on all limbs, a bulb "mantle", a round head.

*Shelf arms.* Same taper and S-curve rules: the pot platform is the flattened terminal bulb (spoon) of the arm, **not** a rectangular slab. Root width >= 100 mm; the shelf platform (hold >= pot footprint) is a widening of the last 20% into a shallow cup with its top face horizontal; the arm beneath curves from the body. This gives a tentacle with a pot-holding palm, as in c01 and the p07 tentacle-grips-pot decision.

---

## 5. Cross-feature cautions
- Elements stay distinct: bone (mask, teeth, nails) = smooth/pale; flesh = rough/matte; eyes = glossy globes. Three surfaces, three finishes.
- Competition for attention (Evan r04 c05 and h1 notes): the smiley, maw, and the tentacle silhouette are the only three primaries. Eyes are secondary: at most 12, clustered.
- Fab conflicts to flag to CAD: tooth recurve vs. 45 deg overhang (2), finger tip hooks (1.2), globe protrusion <= hemisphere (3), tentacle lift-off (4).
- Open items for Evan (none required): whether he prefers a perfect circle or a Ball-asymmetric smiley, and whether the maw should be vertical (c01) rather than horizontal.

---
*Edit log*

| Date | Agent | Change | Signed-off-by |
|------|-------|--------|---------------|
| 2026-11-17 | aesthetics-analyst | Initial creation (Evan r06 feature directives) | FLAG OPEN: numeric defects a builder would copy. (1) s.1.1 smile arc: centre y +0.0675 D with r 0.335 D puts endpoints at -0.100 D and bottom at -0.2675 D; the stated endpoints -0.080 D and bottom -0.2475 D need centre y +0.0875 D. (2) s.4 c01 row "five long limbs: two shelf arms, three lower tentacles" contradicts c01 (3 shelf arms with plants, visible in c01_ref and the gate overlay; gate trace 6 limbs, DESIGN s.2.1 says 7), and the s.4 layout "2 shelf arms + 3 lower" conflicts with the locked 3 shelves and DESIGN #6/#12. (3) s.4 "length : root width 6:1 to 10:1" is unreachable with the stated 320-500 mm lengths and 90-130 mm roots (2.5-5.5:1); CAD README s.4.3 already reports 3.8-6.5. (4) s.3 "G >= 20 mm for any globe" vs cluster sizes 0.25-0.4 x G_max (38-55 mm gives 9.5-22 mm); pinpoint pupil 0.12-0.18 x iris (iris 0.36-0.45 G) is about 1 mm at G 20 vs the >= 3.5 mm recess rule. (5) s.2 "piece-width share ~26-29%" computes 25-29% (230-265 over 914). Fix: owner corrects or marks the lines [DERIVED] with the conflict named. Verified OK: grades [V]/[U]/[M] defined in s.0 and applied per source row; [V] rows checked against Wikipedia (Harvey Ball: right eye slightly larger, mouth not a perfect arc, ~10 min; Viperfish: teeth would pierce the brain if misaligned; Anglerfish: wide mouth, inwardly inclined teeth; Goblin shark: nail-like teeth, parabolic mouth); design values declared as analyst choices (s.0 [DERIVED] rule, BUILD SPEC blocks), anatomy marked [M] +-10%; no images stored; rest of smile arithmetic (chord 0.58 D, sagitta 0.1675 D, D >= 230, eye 21 x 48 mm), skeleton P:M:D ratios, taper law at s 0.5/0.8, tooth base L/4 = 17.5 mm all check. Body [PROVISIONAL] status line stays |
