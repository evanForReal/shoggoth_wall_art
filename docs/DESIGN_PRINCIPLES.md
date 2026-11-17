# DESIGN_PRINCIPLES.md

Read before any composition work (silhouette, massing, layout, hero render). Applies to every team that places form on the wall: Aesthetics, CAD, Structural (when moving limbs), Fabrication (when splitting).

**Why this exists.** Evan, r05/r06 (issue #6): "weird clunky cluttered clockwork look. poor compositional skills. do some review on basic elements of design that draw the viewer's attention, and take notes in a log somewhere for agents to view." / "the actually integral body of the creature has been almost entirely lost. fully revise your design around a clearly defined organism. it should have an organic, defined body." / "tentacles are not obvious in the design ... looks more like a blob on the wall." Round-06: 11 of 12 disliked. Round-05: 10 of 13. The surface (Beksiński texture) was never the problem. Composition was.

**Status of numbers.** Thresholds below are proposals calibrated by eye from c01/c03 (904x1200 JPEG) and our renders. Recalibrate by measurement when a silhouette tool exists. Principles are standard; sources in section 7 are cited from memory, not re-verified online this session.

**Locked, do not re-open:** side-profile depth character (loved r05 and r06); Beksiński surface vocabulary; 3 plant shelves (flat top >=150x150 mm, >=300 mm clear above each); envelope ~914 x 914 mm; happy-face mask is the one clean, contrasting element.

**Reconciling "rich and detailed" (vision notes) with "simplify".** Richness lives in surface texture (fine frequency). Clarity lives in massing, silhouette and value (coarse frequency). The two are separate layers. c01 is both: legible creature at 64 px, lace-dense at 1 m. We fail when fine-scale forms (fingers, eyes, teeth, ribs) are also large-scale forms.

---

## 0. Viewing conditions (governs every test)

- Viewer at 2-4 m. A 914 mm piece subtends ~25 deg at 2 m, ~13 deg at 4 m.
- A 64 px-wide thumbnail of the full envelope = 14 mm per pixel. That is roughly the smallest unit of form that survives at 4 m in a dim room. Anything that exists only below ~15 mm is texture, not composition. 128 px = 7 mm/px ≈ 2 m reading.
- Room is dark, refined, lit by a few warm downlights/lamps (c01, c03). Wall is near-black brown. Reference wall luminance ~12% (30/255). Our renders use a ~30% (76/255) mid-brown backdrop: weaker figure-ground than the real target. **Render hero views against a wall at or below 15% luminance** or the tests below under-report problems.
- Initial gaze is decided in the first ~second by: brightest region, highest local contrast, largest uninterrupted shape, faces/eyes. Detail is read only after.

---

## 1. Core principles

Each: definition, why it matters here, TEST (apply to a render; pass/fail in plain terms). Tests use these standard views: **S** = silhouette (flat black on white, 128 px wide); **G64** = grayscale, 64 px wide, nearest or area downsample; **B** = grayscale, Gaussian blur sigma ~1.5% of image width (the "squint"); **V4** = grayscale posterized to 4 levels. Recipe in section 8.

### 1.1 Focal point and hierarchy (primary / secondary / tertiary)

**Definition.** A composition has one dominant point of attention, a clear second, and a supporting third. Attention is a ranked path, not a set. Equal-strength elements split the gaze and the eye oscillates.

**Why here.** The brief gives us a built-in primary: the pale smiley mask. Secondary: the maw (the horror payoff). Tertiary: tentacle tips/shelf plants. Our failures promoted everything (pale ribbons, eyes, teeth, fingers) to the same rank. In a dark room at 3 m the viewer needs to read "face, then mouth, then limbs, then plants" in 2 seconds, and then be rewarded by close inspection of texture.

**TEST (ranking).** On B, find the 3 brightest/highest-contrast blobs. Pass: #1 is the mask; #2 is the maw/chest core; #3 is a limb tip or plant. Fail: any non-mask blob within ~15% of mask luminance and >1% of envelope area; or #1 is not the mask. Cross-check on G64: cover the mask with a finger; the eye must still land on a defined second thing, not nowhere.

### 1.2 Value contrast and value structure (notan)

**Definition.** Value (light-dark) carries structure before hue or texture does. Good compositions use few, well-separated value masses (a "notan": 3-4 flat tonal shapes: dark ground, mid form, light accent). Contrast is relative: the brightest area dominates by being isolated, not by being bright in absolute terms (simultaneous contrast).

**Why here.** A pale cream mask on dark flesh on near-black wall is the strongest tool we have: ground ~12%, body ~35-50%, mask ~75-80% (c01). The mask is the only large smooth, light, clean-edged shape in a textured, dark field: value + texture + edge contrast stack. That is why it dominates at 4 m. Every other pale thing (bone ribbons, teeth, finger tips, rims, eye whites) spends that budget. Bone/teeth should be one step below mask, and clustered where the creature's anatomy puts them.

**TEST (V4).** Posterize to 4 levels. Top level (lightest) pixels: >=60% inside the mask, remainder confined to the maw teeth/rim; no top-level cluster elsewhere >0.5% envelope area. Bottom two levels carry >=65% of the envelope (dark piece in a dark room). Also fail if the piece median luminance is at or below the wall's (r06: median 67 vs wall 76 = body darker than the wall but without a lit mid-tone, so figure-ground is flat).

### 1.3 Shape hierarchy (big - medium - small)

**Definition.** Strong designs use a few large shapes, more medium shapes, many small shapes, in roughly geometric size steps, with one clear largest. Equal-sized shapes read as pattern or noise; shapes the same size as the focal point compete with it. (Cf. Loomis, Robertson: block in big forms first, then secondary, then detail.)

**Why here.** The creature needs: one big form (head+torso mass), several medium (limbs, maw, shelves), many small (texture, tooth, eye). r06 has ~10 features of similar size (mask ring, maw ring, 5 limbs, 3 shelf slabs, finger clusters) and no dominant mass. That is the "clunky clockwork": equal-size parts that read as assembled components.

**TEST.** List the 6 largest distinct features on S (segment by eye or connected components after removing texture with B). Pass: largest >= 2x the second by area; no two of the top 6 within a 0.8-1.25 area ratio unless they are same-class limbs that differ in length by >=15%. Small features (<1% envelope) must outnumber medium ones by >= 3:1.

### 1.4 Silhouette and readability

**Definition.** The outer contour alone should communicate the subject (animation practice: test characters in solid black). A good silhouette has a clear head, clear mass, limbs separated by negative space, and no tangents (two contours kissing at a point).

**Why here.** From 3 m, a relief in a dark room is mostly its silhouette against a lit-wall gradient. "Looks like a blob on the wall" is a silhouette failure: limbs merged into the mass, tips not distinct. c01 and c03 read as creatures in solid black; r05/r06 read as a rectangle with debris.

**TEST (S).** Fill the piece black, 128 px. (a) Name the creature class in one sentence with no mention of shelves (octopus-person, tentacled figure). (b) Count limb tips: >= 6 distinguishable. (c) Head is a separable round bump with a neck/shoulder step. (d) No axis-aligned straight silhouette run >120 mm equivalent (r06: left edge is a vertical wall with two horizontal slab shelves = the letter "E/F"; furniture, not creature). (e) No tangents between limb tips and the mask or each other.

### 1.5 Gesture and line of action

**Definition.** A single flowing curve (C, S, or diagonal) that runs through the whole figure and gives it motion and intent; everything else decorates that line. Limbs should echo or counter it, not fight it. (Disney "line of action"; Vilppu, Mattesi "Force"; Robertson on gesture.)

**Why here.** A Shoggoth is a mass in motion: pushing out of, or sliding down, the wall. c01's line is the vertical spine from mask through chest to root, with limbs fanning off like a figure with arms raised. Loved side profile = a vertical slab with limbs stepping outward: that's a depth gesture; the front needs a matching planar gesture. Our r06 has no line: components stacked in a column, branches at right angles.

**TEST.** Draw one smooth curve (<=2 inflections) from mask centre through torso to the longest limb tip on S. Pass: >=70% of silhouette mass lies within ~0.5 head-widths of that curve plus its fan of limbs, and the curve has no kink >30 deg over 100 mm. Fail: you need >=3 line segments, or the curve crosses the figure twice.

### 1.6 Negative space and rest areas

**Definition.** Empty or quiet areas give shapes room to be seen; they are part of the composition (figure-ground). Without rest, the eye has nowhere to recover and the whole reads as "busy."

**Why here.** Clutter = no rest. In c01 the lit dark wall between arms and tentacles is as designed as the creature: three big wedges of bare wall (upper notch around the head, left wedge between mid-left shelf arm and lower tentacles, right wedge ~200x220 px of 700 between right arm and right curl). The web arms also have ~6 round perforations 40-70 px (5-10% of piece width): internal rest. In r05/r06 the silhouette is a near-solid star with few open voids inside the hull and no rest holes on the body (eyeballed).

**TEST (S).** Fill ratio = silhouette area / bounding-box area: target 30-45% (c01 ~35-40% by eye; luminance-threshold crude estimate 26-29%). Negative-space ratio inside the convex hull: >= 25%. At least 3 negative-space wedges each >= 4% of envelope area, bounded by limbs and open to the outside. Detail areas (highest edge density on B-then-edge) must not exceed 50% of body area.

### 1.7 Rhythm and repetition vs monotony

**Definition.** Repeating a shape creates rhythm; varying size, spacing, angle keeps it alive. Identical spacing/size = monotony or mechanism. Odd counts and graded sequences read as organic; regular spacing reads as machinery.

**Why here.** Tentacles repeat by nature, so variation is mandatory. c01's lower limbs differ in length (330-450 px), angle (40-70 deg off vertical), curl direction. r06's fingers on shelves, eyes scattered across a limb, tooth ring, gear-like tentacle crown around the mask all repeat a same-size unit at regular intervals = "clockwork". The mask's finger crown (r06) around a circle is literally a gear.

**TEST.** For any repeated element (limbs, teeth, eyes, fingers): sizes vary by >=20% across the set, spacing varies by >=25%, and the set has no circular or evenly spaced arrangement. Reject regular polygons or rings of repeated units around any focal object (gear test). Repeated small units >= 6 in one cluster must be graded (largest nearest the focus).

### 1.8 Unity and grouping (Gestalt)

**Definition.** The eye groups by **proximity** (near = one group), **similarity** (alike in value/shape/colour = one group), **continuation** (smooth lines are followed through crossings), **closure** (it completes gaps), and **figure-ground** (it assigns a region as object vs background; small, convex, enclosed, dark/light consistent regions become figure). A design is unified when parts group into few wholes and the wholes belong to one subject. (Wertheimer 1923; Koffka; Arnheim ch. on grouping.)

**Why here.** The brief requires an *organism*: head, body, limbs perceived as one connected thing. In r05 pale small pieces (little human-like figures, hands, ribbons) group by similarity into a second "flock" in the lower half, separate from the dark body. In r06 the shelf planks group by similarity and orthogonality into a bookcase, separate from the creature. The maw ring and mask ring group by similarity (same ring, same pale rim) = a pair of eyes/binoculars. Use these deliberately: limbs must continue (continuation) smoothly out of the torso so they read as growing from it; shelves must be the same material/value as the limb they terminate.

**TEST.** On G64 / B, mark groups by eye. Pass: <= 3 perceptual groups total (head, body+limbs, plants/wall). Every limb is connected to the body mass at 64 px (no floating islands). Shelf value/texture within 10% of its parent limb. Fail: any group of >= 4 similar small pale items not anatomically part of one named organ.

### 1.9 Asymmetric balance and visual weight

**Definition.** Balance is perceived torque: weight = size x value contrast x isolation x complexity x position from the visual centre. Symmetry is static; asymmetric balance (a heavy mass near the centre balanced by lighter/longer extensions on the other side) is lively. (Arnheim: visual weight, vector/force fields.)

**Why here.** Horror wants unease, not a heraldic crest. c01: slightly asymmetric (two shelves left, one right; right limb curls out lower). r05/r06 are near-bilaterally arranged: planks left and right at similar heights, mask centred on the axis over a centred maw. The three shelves are plant-bearing and heavy-weighted (plants add colour and weight): they must sit in a triangle, not a ladder.

**TEST.** Compute luminance-and-area-weighted centroid on S/G64. Pass: horizontal centroid within +-8% of envelope width from centre and left/right weight ratio 1.1-1.5 (not 1.0, not >2); vertical centroid between 40-55% of height (head above, body mass lower-middle). Mirror-symmetry score (flip S, IoU) < 0.85. Shelves: the three plant positions form a non-collinear triangle with no two at the same height within 120 mm.

### 1.10 Edges: lost and found

**Definition.** Sharp, high-contrast edges attract attention (found); soft or value-merged edges recede (lost). Painters place hard edges at the focal point and let secondary forms dissolve into shadow or neighbours.

**Why here.** Beksiński works this way: forms dissolve into dark. In c01 the mask has a crisp edge, the maw has crisp teeth highlights, and the limbs' undersides dissolve into the wall in shadow. In our renders every edge is hard (everything was lit and modelled the same), so no edge says "look here."

**TEST (edge map).** Run an edge detector (Sobel/Canny) on the grayscale render; blur the edge map. The strongest edge-density peak must be at the mask/maw. Limb edges: >=30% of limb contour length should be low-contrast (<15% value step vs the wall), esp. on the shadow side. Fail: edge density roughly uniform across the piece, or the peak at a shelf, finger cluster, or tentacle tip.

### 1.11 Simplify, then detail

**Definition.** Block in mass and value first; add medium forms; add fine detail only where attention should land or where the form is already resolved. Detail is a spend: put it where the hierarchy says. (Standard painting/illustration/concept practice: big-medium-small, Loomis; Robertson "How to Draw".)

**Why here.** Rich detail is mandated, but spread uniformly it flattens hierarchy. Beksiński texture is fine-scale; it can cover limbs completely if the large forms and values are already unambiguous. The ordering of our pipeline must be: silhouette round -> value-mass round -> detail. We went straight to detail with an undefined mass.

**TEST (frequency separation).** Blur the render until sub-15 mm texture is gone (B). Pass: the blurred image alone still reads as the finished design (head, body, limbs, mask, maw all identifiable; value map intact). Then re-add detail: the *detail density map* (local variance of the high-pass) peaks at head/maw and body core; quieter on shelf tops (plants stand there), limb shafts mid-density, tips medium-low. Fail: the blurred render is a blob, or detail is equally dense everywhere.

### 1.12 Relief-specific: depth as hierarchy and light

**Definition.** In a monochrome relief, depth becomes value under directional light. Height variation defines both form and read order; the wall plane is the ground; the closer to the viewer, the more it competes.

**Why here.** The side profile is loved: wall-hugging low-relief body, limbs projecting progressively farther toward shelf ends, three clean flat tops stepping out. Preserve that. Rule of thumb: keep the head/mask at highest *clean* relief (it should catch light), keep the torso low-to-mid relief with wrapped, soft form, and let limb relief rise toward shelf ends. Do not add high-relief small parts (fingers, nubs) on shelf tops: they intrude into the 300 mm clear volume and turn the plant bays into clutter (r06 side render: finger nubs on all three shelves).

**TEST.** Render with a single raking light from upper left (and again from above-front). Pass: the mask is the brightest spot in both; limb forms read as continuous tubes/webs; shelf tops are blank. Side view: no protrusion on a shelf top above its flat plane.

---

## 2. Concept-art composition analysis

Sources viewed: `review/rounds/round-04/images/c01_baseline-velvet-salon.jpg` (loved, "absolutely excellent"), `c02_stone-smile.jpg` (loved, "oh my god also amazing"), `c03_mask-plus-maw-ochre.jpg`, Evan's sketch `aesthetics vision/initial human input/IMG_0073.HEIC` (opened; was readable), `init_vision.md`. Fractions are of the piece's own bounding box (W x H) unless stated. Eyeballed from 904x1200 images (+-3%).

### 2.1 c01 velvet-salon (the primary target)

Piece bounds ~700 x 680 px (about square, aspect 1.03:1) on a 904x1200 frame: 77% of frame width, 57% of height. Centre x ~ 455 (axis ~ 0.5).

**Organism read at a glance:** a tentacled humanoid with arms raised. One creature, instantly.

- **Head.** Pale smiley mask: ~115 x 155 px = 16% W x 23% H, tall oval (aspect ~0.74). Centre at x 0.52 W, y 0.18 H. Wrapped in a hair/hood halo of web strands (halo ~ 220 px = 31% W wide) that narrows to a neck. Mask is raised, slightly smaller than the head mass behind it: the mask sits *on* a head, not in a ring.
- **Torso/body.** Starts below the chin at y ~0.29 H, runs to ~0.58 H (pelvis/root cluster where limbs diverge). Torso 28% of H long; shoulders ~37% W wide at y ~0.31 H, narrowing to ~25% W at the waist. Body mass (head + torso) ~ 260 x 395 px, ~16% of envelope area, but because it is the centre and the darkest-edge-lit form it holds visual authority. Head:body mass height ≈ 1 : 2.6, head-to-total-height ≈ 1 : 4.4.
- **Maw.** Inset in the chest, directly below the mask, y 0.30-0.52 H, ~150 x 150 px opening = 21% W x 22% H (about 1.3x mask area; 1.7x with its rim). Inner value is the darkest in the piece. Teeth are thin, drawn as web-like fangs, low contrast. It reads as a chest cavity/ribcage opening rather than a second face. Key: mask and maw differ in **size** (1.3-1.7x), **value polarity** (light disc vs dark void), and **shape** (clean ellipse vs ragged-lipped irregular oval).
- **Gesture.** Vertical spine axis (mask, maw, root) plus two arm lines rising ~20-30 deg above horizontal from the shoulders, each reaching ~0.43 W from the axis. Whole silhouette ≈ "X/star with a head": arms up-and-out, legs down-and-out. Slight asymmetry: right shelf arm lower (tip y 0.25 H vs left 0.16 H), right lower limb curls out horizontally at 0.80 H, left side has an extra horizontal shelf arm at 0.60 H.
- **Limbs.** 3 shelf arms + 4 non-shelf lower tentacles = 7 major, plus a fringe of root tendrils at the bottom centre dissolving into the wall. Upper arms: thick web-lace, root ~100 px, bending once, flaring into a shelf platform at the tip. Mid-left arm: near-horizontal, slightly drooping 10 deg, flat top, shelf ends with a wrapped lip. Lower tentacles: fan from a pelvis point (~0.5 W, 0.60 H) at ~40-70 deg off vertical: tips at (0.15 W, 0.99 H), (0.85 W, 0.99 H)-ish, one curling out to (1.0 W, 0.80 H); length 330-450 px (0.47-0.64 W); root ~90-110 px, tip 14-25 px (taper ~5:1), each with one primary curve and a terminal hook/curl. Nothing crosses in front of anything else except at the roots.
- **Shelves vs limbs.** All 3 shelves are the **terminal flares of limbs**, at the outer extremes of the envelope: UL (x 0.0-0.28 W, y 0.17 H), UR (0.75-1.0 W, y 0.25 H), ML (x 0.0-0.3 W, y 0.60 H). Plants stand on lace-textured flat tops in the same material as the limbs. Plants (green, ~90 px) are the only hue accents; they are secondary focal points at the corners of a **triangle** (UL, UR, ML) with the mask at its upper centre.
- **Value structure.** Wall ~12% (spotlight pools at top ~25%), body mid-tones 35-50%, ochre ridges to ~65%, mask ~75-80%, deepest darks in maw and web holes. Notan: three tones (dark wall / mid body / pale mask) + green accents. Edges: mask crisp, teeth crisp, limb undersides lost into shadow.
- **Negative space.** Silhouette fills about 35-40% of the bbox. Three large bare-wall wedges (left: between mid-left arm and lower-left tentacle; right: between right arm and right curl ~ 200 x 220 px; top: notches flanking the head) plus ~6 web perforations of 40-70 px. The lower limbs are well separated: ~4 clear fingers of wall between them.
- **Focal hierarchy.** 1) mask (light, clean, isolated, upper-centre, spotlight above it). 2) maw (dark void directly under it, along the same axis = reads as one figure, "face and mouth"). 3) shelf plants (green hue) out along the arms. 4) tentacle tips/curls. The spotlights above reinforce the vertical read. Detail density: highest at maw and torso web; shelves moderate; tentacle shafts lower.
- **Viewing context.** The piece sits over a sofa, spans ~1/2 of the wall; the tentacles end ~0.4 H above the sofa back (clear horizon).

### 2.2 c02 stone-smile

- No maw. One large asymmetric mass (~1.25:1 landscape, 85% of frame width): a torn drape/web sheet with a long diagonal from upper-right down to lower-left and tattered tips at left (two) and right (one), bottom point.
- Mask at x 0.70 W, y 0.27 H, ~80 x 110 px (10% W): pale, smooth, closed-eyed, nestled into the web upper-right; the only smooth shape on a field of lace and holes. Rust/orange patches at the centre-left give a second tonal zone (warm patch vs cream web).
- **Gesture:** one continuous diagonal flow; silhouette is one big C-curve opening to the right. Shelves at three points around the mass: UL end, lower-left end, one inside the web at right (plant in a niche under the mask).
- **Lessons:** (a) a single *unified silhouette* with ragged edges reads as one thing even with no body/limb anatomy; (b) a clean smooth pale mask alone wins focal hierarchy against intense texture; (c) large holes are rest areas; (d) edges fray out into the wall at the tips = lost edges; (e) texture density is uniform here, but value zones (cream vs rust vs dark holes) give the large-scale structure.

### 2.3 c03 mask-plus-maw-ochre

- Radial octopus: dome head/body ~0.4 W wide x 0.55 H, mask on the dome top (circle ~120 px dia), maw immediately below (opening ~130 x 150 px; with rim ~155 x 180; about 1.65x the mask area, 2.4x with rim), stacked on the vertical axis; two horn-like arcs up from the head, 8 limbs total (3 shelf-bearing, 5 curling).
- Very high silhouette legibility; limbs taper cleanly with spiral curls at the tips; shelf tips are flat ledges at the arm ends. Value: mask white/cream disc brightest; maw interior dark with pale teeth (higher contrast than c01, so it competes more); body ochre-uniform.
- **Lessons:** the stacked mask/maw pair works when the maw is **larger and dark**, the mask smaller, clean, and brightest. It is more cartoon/less Beksiński than c01 because the body is a smooth dome and the silhouette is symmetric. Limbs show how to taper and curl.

### 2.4 Evan's sketch (IMG_0073)

- Front view: smiley circle top-left (~10% of page width), a separate toothy wedge/crescent maw immediately right of it (~12-13% wide, similar size to mask; side by side, not stacked). Thin wavy "corona" tendrils radiate from the head across the top and left edge.
- **No drawn torso.** Instead: fat ribbon limbs. A long band sweeps from below the maw out to the right and ends in a tight spiral with a horizontal bar (shelf 1); a second S-ribbon loops to a central spiral with a bar (shelf 2); a third ribbon descends to a lower shelf bar at the bottom (shelf 3) with a trailing tail. Limb thickness ~8-10% of page width, long S-curves, terminal spirals. The sketch's *line quality* is the gesture: sinuous, ribbon-like, 2-3 big loops.
- Side view: an upright slab against a vertical wall line, face bulging at top, stacked bulges below.
- **Lessons:** (1) mask and maw are separate, adjacent objects (Evan's, vs the stacked pair in c01/c03: both fine); (2) limbs are broad flowing ribbons with spiral ends; thick enough that "tentacle" is obvious; (3) shelf = flat bar on the top of a spiral/curl end; (4) a gesture with large loops, not stacked parts.
- Note: vision constraints say "visually rich; no sparse/minimal interpretations". The sketch is simple line drawing; do not read it as a request for minimalism either.

### 2.5 What c01/c02/c03 share (the rules our work broke)

1. One mass, one silhouette, one head. 2. The mask is the brightest and cleanest thing, with dark surroundings. 3. Maw differs from mask in size and value. 4. Limbs taper from thick roots to thin tips, curve once, curl at the end, are separated by wall. 5. Shelves are limb ends, at the periphery, in the limb's own texture. 6. Ground is dark and large areas of it are visible inside the hull. 7. Fine texture everywhere, but never fine *forms*.

---

## 3. Critique of our failures (r05 hero, r06 hero + variants)

Files: `teams/cad/fullpiece/renders/hero_front.png` (r05), `teams/cad/fullpiece_v2_1/renders/hero_front.png`, `variants_sheet.png`, `hero_side.png` (r06). Pixel estimates on 1200x900 renders.

**What made them read as "clockwork":** (1) three orthogonal plank shelves with hatch/blind-slat texture and square edges = bookcase brackets; (2) mask surrounded by a ring/collar (r05) or a crown of equal-size finger-nubs (r06) = gear/sun-dial/cog; (3) mask ring and maw ring stacked, both pale-rimmed circles = two dials; (4) a hard vertical wall at the left joining the shelves (E/F silhouette, with the leg as a square-footed post) = furniture; (5) repeated small units (eyes, teeth, finger tips) at regular intervals = pegs and rivets; (6) every part lit and edged the same = machine-shop diorama.

| Principle | r05 hero | r06 hero / variants |
|---|---|---|
| 1.1 Focal hierarchy | Mask in a bright oval collar is #1, but pale human-like figures and ribbons in the lower half (same lightness) form a second bright cluster almost as large as the head zone. Gaze splits: face / bottom-centre flock. | Mask (face disc ~130 px dia + ring ~150) and maw ring (~200 x 170) are two pale-rimmed rings on the same axis, touching: two equal competing focal points. Teeth, eye dots (>12), finger tips, bright upper-right claw all in the same value. Variants a/b/c move one knob and leave this intact: no axis signal (as DECISIONS notes). |
| 1.2 Value | Pale bone ribbons (~85% of mask value) scattered through the bottom; dark hatched shelves; wall at 30% so the dark body has little separation. | Same: piece median (67) darker than wall (76) without a mid-tone body to bridge; mask rim, maw rim, teeth, claws, fingers share the top value; no single "brightest thing". |
| 1.3 Shape hierarchy | No dominant mass: ~15 features of 2-5% envelope each (oval collar, 3 slabs, 4-5 figure fragments, hand cluster, upper blob). | ~10 features of similar size: mask ring, maw ring, 3 shelves, 5 limbs (v2), right claw, left leg-post. Largest is the maw ring ≈ mask ring ≈ one shelf. |
| 1.4 Silhouette | Flat slab wings left/right + debris below: reads as a winged plaque, not a creature. No head/neck step. | E/F left edge (vertical wall + 2 horizontal slabs + post); limbs hang from the bottom as short stubs; a whole bottom half is 3-4 thick stumps crossing in an X; no distinguishable tentacle tips. Confirms Evan: "blob on the wall". |
| 1.5 Gesture | None: shelves arranged left/right/left at fixed heights; body a cloud. | Vertical stacking (mask over maw over X-legs) = a totem, not a flowing line; limbs leave at right angles to the "wall" edge, then X. |
| 1.6 Negative space | Hull has few voids (eyeballed), mostly inside shelves and between figure fragments (noisy, not restful); no large clean wedge. | Hull nearly solid: few voids; two small wall pockets between limbs. No rest area. |
| 1.7 Rhythm | Hatched slats, repeated figurines. | Crown of 5-7 finger nubs around the mask, 3 finger nubs on each shelf, ring of fangs, 12+ eyes: equal-size units, even spacing = mechanical. |
| 1.8 Unity | Figurines/ribbons group by similarity into a separate flock; shelves group as slats with each other; body mass unidentifiable. | Shelves group into "bookshelf"; mask+maw group into "face with big eyes"; limbs and body fail to connect into one organism (body lost, per Evan). |
| 1.9 Balance | Near-bilateral: wing shelves at left/right, mask near centre-left. | Shelf pairs at left at two heights + one at right; mask central: ladder arrangement, no triangle. Heavy pale weight in the upper half only. |
| 1.10 Edges | All edges hard, shadows crisp on the wall, no lost edges. | Same: every form outlined by a bright rim light; nothing dissolves. |
| 1.11 Simplify/detail | Detail uniform: fibrous slat texture on shelves rivals the face. | Detail uniform; eyes/teeth/fingers are fine-scale *forms* (30-50 mm) not texture, so the blurred image has no readable large structure (G64 test: mask+maw rings, then noise). |
| 1.12 Relief | Shelves read as flat boards on blades. | Finger nubs on shelf tops intrude into the plant clear volume; the side view is the loved depth stack, but only because nothing competes there. |

Quick diagnosis of root cause: we added organs (fingers, eyes, maw teeth, bone) onto a stack of components instead of growing limbs from one body. The organism never existed as a silhouette. Fixing means a silhouette-and-value round first, with detail banned.

---

## 4. CAD-actionable composition checklist

Run on a front-orthographic silhouette + a G64/V4 value render *before* adding detail (no fingers, eyes, teeth, ribs). All pass/fail. Fail any = stop and revise. Log results in the CAD STATUS exec summary as `COMP: 16/16` or list failures.

| # | Check | Pass |
|---|---|---|
| 1 | **Creature read (S, 128 px).** Silhouette only. | A reviewer names a creature class (tentacled figure/octopus-person) in one sentence without referencing shelves; head, body, limbs are all findable. |
| 2 | **Defined body mass.** Head + torso region (everything within the limb roots) as a single connected shape on S. | 12-20% of envelope area; at least 1.8x the area of the largest single limb; has a neck/shoulder step below the head. |
| 3 | **One head, one mask.** | Exactly one head mass, mask area 2-4% of envelope, tall oval aspect 0.7-0.9 (or circle); centre at y 0.15-0.30 H. No ring/collar/crown of repeated units around it. |
| 4 | **Mask is the single brightest region (V4).** | Top value level >= 60% inside the mask; no non-mask connected region >0.5% area at >= 85% of mask luminance. |
| 5 | **Maw differs from mask.** | If a maw is present: area ratio maw:mask is <=0.7 or >=1.3 (references 1.3-2.4), interior darker than body mean, rim no lighter than body mean; maw is inset in the torso, not stacked as a second ring; centres separated by >= 1.0 mask-height. |
| 6 | **Limb count and legibility (G64).** | >= 6 limbs with distinguishable tips at 64 px, of which exactly 3 are shelf-bearing; minimum 2 non-shelf limbs rise or extend outward (not all hanging). |
| 7 | **Tentacle continuity and taper.** Each limb on S. | One connected skeleton root to tip; width non-increasing (+-10%) root to tip; root:tip >= 5:1 (limb min tip 12-25 mm); one dominant curve plus optional terminal curl; length 0.4-0.65 W; no pinch or bulb mid-shaft. Shelf limbs flare only at the tip. |
| 8 | **No equal rivals.** Top-6 features by area on S. | Largest >= 2x second; no pair among the rest within a 0.8-1.25 area ratio unless same-class limbs differing >=15% in length. Limb tip angles and lengths all distinct. |
| 9 | **Gesture line.** | One smooth curve (<=2 inflections, no kink >30 deg/100 mm) from mask centre to longest tip carries >= 70% of body mass within +-0.5 head width. Documented as the named gesture option (section 5). |
| 10 | **Negative space.** | Silhouette fill 30-45% of bbox; >= 3 open wall wedges each >= 4% of envelope; interior empty-hull ratio >= 25%; no two limbs closer than 60 mm over >150 mm of length unless they merge at a root. |
| 11 | **No furniture geometry.** | No straight silhouette run >120 mm (any angle) and no axis-aligned right angle in silhouette; shelf silhouettes have organic, curved fronts; no vertical wall-parallel post >150 mm; shelf is the tangent-continuous flare of its limb centreline. (Locked shelf spec still holds: flat top >= 150x150 mm, >= 300 mm clear above.) |
| 12 | **Shelf layout.** | 3 shelf tops form a non-collinear triangle, no two within 120 mm height, at least one at upper third, all at limb tips on the envelope periphery (outer 30% of width or height); plants never overlap the head halo or another limb. |
| 13 | **Balance.** | Weighted centroid within +-8% W of centre horizontally, vertical 40-55% of H; L/R weight ratio 1.1-1.5; mirror IoU < 0.85. |
| 14 | **Blur read (B).** | Blurred render at sigma 1.5% W still shows head > chest/maw > limbs; the first and second brightest blobs are mask then chest core. Blob test on 64 px: viewer names focal order mask, maw, limbs/plants. |
| 15 | **Detail budget (before detail pass).** | Detail layer adds only texture < ~15 mm scale; the blurred G64 of the detailed render still matches the silhouette-stage G64 (SSIM >= 0.9 on B). Highest edge-density at mask/maw; shelf tops blank; zero repeated-unit rings/rows. |
| 16 | **Side profile preserved.** | Side-view stack of wall-hugging body + limbs stepping outward to three flat tops; no protrusions above shelf planes; depth range per r05/r06 side render maintained (do not flatten). |

(16 checks; #14-16 apply at later stages. #1-13 at silhouette stage.)

---

## 5. Organism blueprint (proposal, not a verdict)

Proportion-level description for a 914 x 914 mm envelope (W = H = 914). Source: c01 + sketch. All numbers are starting points for a silhouette round; Evan decides.

**Head.** Mask 150 W x 190 H mm (16.4% W x 20.8% H; tall oval 0.79, or a more iconic smiley disc: the verdict in r06 asks for a *more iconic* smiley, so a near-circle of 170 mm is fine). Carried on a hooded/web head mass ~270 x 320 mm so the mask is raised, not ringed. Centre of mask: x 0.50-0.54 W (c01) or off-centre per gesture option, y 0.17-0.22 H (155-200 mm from top edge). Smile features >= 60 mm wide to be readable at 4 m. Mask is the only clean smooth glossy/light form. Hand/finger crown: none.

**Torso/body.** Hanging directly below the head: neck at y 0.28 H, shoulders ~340 mm (37% W) wide at y 0.31 H, waist ~230 mm at y 0.52 H, pelvis/root cluster at y 0.56-0.62 H from which lower limbs diverge. Body mass height ~0.34 H (310 mm) under the head. Low relief (wall-hugging, ~40-70 mm), rising to mid relief around chest. Total body mass (head + torso) ~16-18% of envelope area.

**Maw.** Inset in the chest, directly below the mask: opening ~190 x 180 mm (about 1.3-1.7x mask area), centre y ~0.40 H; dark interior (below body mean), rim in body colour (not pale), teeth thin and graded (large at the corners, small at the centre; sparse; value no lighter than 70% of mask). Lip is organic/irregular. Sets maw as the second focal point and mask as the first.

**Limbs (7 total: 3 shelf, 4 free).**
- *Shelf limbs.* Root width 110-140 mm at the shoulder/body, rising or extending outward, one bend, tip flaring into a flat platform (>=150 x 150 mm top, usually 190-230 mm long, organic front edge). Reach 0.35-0.5 W from the axis. Heights: upper-high (y ~0.15-0.20 H), upper-mid (y ~0.25-0.32 H) on opposite sides, and one low (y ~0.55-0.62 H); no two within 120 mm. Each has >=300 mm clear above its flat top (the head halo and other limbs stay away).
- *Free limbs (4).* From pelvis cluster, fanning 35-70 deg off vertical, tips reaching y 0.85-1.0 H; lengths 380-560 mm, different from each other by >=15%; root 90-120 mm, tip 12-25 mm; one dominant curve + terminal curl on 2-3 of them (c03 curls, sketch spirals). At least one lifts outward and up (c01 right curl) to break the "all hang down" read. A fringe of fine root tendrils (<10 mm) at the base melts into the wall (lost edge).
- Limbs cross only near their roots; thickest portion is at body.

**Gesture line.** Named per option below.

**Value map.** Wall dark (render at <=15%). Body 35-50%, with lit ridges to 60-65% facing the key light. Mask 75-85% (only region above 70%, apart from small rim sparkle on teeth at <= 60%). Maw interior 5-10% (darkest). Plant pots and green foliage are expected tertiary accents. Limb undersides fall off into wall value (lost edge).

**Silhouette/negative-space target.** Fill 33-42% of bbox. 3-4 open wedges: upper-notch around the head, left of the lower limbs, right of the lower limbs, and between the shelf arms and the free limbs.

### Gesture options (silhouette round candidates; test 3-5 in flat black, no detail)

**G1. Descending Figure (c01-derived).** Vertical spine. Head top-centre (x 0.5, y 0.19), torso straight down, two arms rising out to upper shelves, one extended low, free limbs fan from the pelvis. Line of action: vertical with a slight S (head offset 3-5% to one side). Shelves: UL high (0.12 W, 0.17 H), UR (0.88 W, 0.27 H), ML low (0.10 W, 0.60 H). Closest to Evan's loved c01; lowest risk, highest chance of "reads as organism". Risk: formulaic if copied outright; vary arm heights and asymmetry.

**G2. Diagonal Emergence (c02-derived).** Body a sweeping diagonal from lower-left to upper-right, like a creature pulling itself up the wall. Head at upper-right (x 0.68, y 0.25), torso a 35-45 deg band, limbs trailing and reaching out along the diagonal and flanking it; shelves along the diagonal at upper-left, centre-right under the head, and lower-left. Line of action: one long C opening to the right. Note: r05 "v3 diagonal" was disliked; but that variant had no defined body. Test a diagonal with a body, don't dismiss. Risk: moves mask off axis; depth stack for the side profile needs rechecking.

**G3. Low Crouch, limbs rising.** Head low (x 0.45, y 0.58-0.65), broad hunched body mass on the lower half, limbs rising up and out like a spider or a squid thrown against the wall, shelves at the elevated limb tips (upper-left, upper-right, and mid-left). Line of action: inverted U/arch over the head. Most menace, inverts c01. Check shelf clearance >=300 mm above each; head must not sit under a shelf. Risk: mask sits low near the furniture line; heavy lower mass.

**G4. Sinuous Spiral (sketch-derived).** Head upper-left (x 0.22, y 0.18); body a broad diagonal-S ribbon sweeping to the lower right; three thick ribbon limbs with large loops terminating in spirals, shelf bars on the tops of three spirals (sketch). Line of action: large S curve. Most faithful to Evan's drawing, most different from c01. Risk: thick ribbon "limbs" can read as a swirling blob again unless the head and the spiral tips are clean and wall gaps are protected (checklist #10).

*Suggested round-07 structure.* 8-12 silhouette cards: each of G1-G4 in 2-3 gesture-level variations (flat dark silhouette + one-tone value, with the mask pale and the maw dark, against the dark wall, the 3 shelves and plants drawn as flat marks). Question to Evan per card: which reads as one creature, and which would you hang? No surface texture. Same envelope. Include c01 as reference card.

---

## 6. Usage rules for agents

1. Before composing: read sections 0 and 4. Before reviewing: sections 1 and 3.
2. Order of work: gesture -> silhouette -> value masses -> hierarchy tests (checklist #1-14) -> detail layer -> checklist #15-16. Do not skip stages. Do not add anatomy details (fingers, eyes, teeth, bone) before silhouette + value pass.
3. Each composition artifact lists the checklist result in its notes (`COMP n/16`, fail list).
4. When you change one thing in a variant, say what principle it tests; "single-axis variants" must differ in a principle-relevant axis (gesture, hierarchy, value) not an accessory (finger count).
5. New design lessons from Evan verdicts get appended to section 3 (critique) and the checklist tweaked here; log in the edit log.

---

## 7. Sources (from knowledge, not re-verified online this session; no quotations used)

- Rudolf Arnheim, *Art and Visual Perception: A Psychology of the Creative Eye* (1954; rev. 1974): visual weight, balance, structural skeleton/force vectors, figure-ground, grouping, the role of simplicity.
- Max Wertheimer, "Laws of Organization in Perceptual Forms" (1923); Kurt Koffka, *Principles of Gestalt Psychology* (1935): proximity, similarity, continuation, closure, figure-ground, Prägnanz. Overview: Wikipedia "Gestalt psychology" and "Principles of grouping".
- Andrew Loomis, *Figure Drawing for All It's Worth* (1943) and *Creative Illustration* (1947): big-to-small construction, value grouping, light and shadow, simplification, gesture.
- Scott Robertson and Thomas Bertling, *How to Draw* (2013): silhouette, form-before-detail, perspective for creature/product design; Scott Robertson, *How to Render* (2014): value and light on form.
- Frank Thomas and Ollie Johnston, *The Illusion of Life* (1981): line of action, staging, silhouette clarity, appeal.
- Glenn Vilppu, *Vilppu Drawing Manual*; Mike Mattesi, *Force: Dynamic Life Drawing for Animators*: gesture and rhythm.
- Bruce Block, *The Visual Story* (2001/2007): contrast and affinity of value, shape, space as attention tools.
- Arthur Wesley Dow, *Composition* (1899) and Japanese notan tradition: dark-light balance in few masses. Wikipedia "Notan".
- Donis A. Dondis, *A Primer of Visual Literacy* (1973): visual elements and contrast techniques.
- Ian Roberts, *Mastering Composition* (2008) and general illustration teaching (squint test, thumbnails, value studies).
- Johannes Itten, *The Art of Color*: simultaneous contrast.
- Reference artists for tone/edges: Zdzisław Beksiński (lost edges in dark ground), H. R. Giger (organism-from-surface continuity).

## 8. Test recipes (Python, PIL + numpy; run with `python3 -I`)

```python
from PIL import Image, ImageFilter
import numpy as np
im = Image.open(PATH).convert("L")
w, h = im.size
g64  = im.resize((64, round(64*h/w)), Image.BOX)                     # G64
blur = im.filter(ImageFilter.GaussianBlur(0.015*w))                  # B
sil  = (np.asarray(im, float) > WALL_LEVEL + 25)                     # S (use a mask render if you have one)
a = np.asarray(im, float)
v4 = np.digitize(a, np.percentile(a, [25, 50, 75]))                  # V4 (3 cut points = 4 levels)
fill = sil.mean()                                                    # fill ratio (use bbox-crop first)
# focal ranking: top blobs on blur
y, x = np.unravel_index(np.argmax(np.asarray(blur)), a.shape)         # brightest blob centre -> must be in the mask bbox
```

Method used for this document: grayscale + 64 px + blur contact sheet of c01, c03, r05 hero, r06 hero (visual review). Observed: c01/c03 read as creature at 64 px and under blur (head, limbs, maw dark); r05 reads as pale clutter below a bright oval; r06 reads as two bright rings over a dark box.

---
*Edit log*

| Date | Agent | Change | Signed-off-by |
|------|-------|--------|---------------|
| 2026-11-17 | aesthetics-analyst | Initial creation (Evan r06 directive) | [PROVISIONAL] |
