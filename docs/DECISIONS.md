# DECISIONS.md — Human Verdict Log

**Append-only.** Never delete or modify existing entries.

## Schema

| Field | Description |
|-------|-------------|
| `date` | ISO date of verdict |
| `round/topic` | Review round ID or decision topic |
| `verdict` | Evan's decision |
| `notes` | Supporting detail, constraints, follow-ups |

---

## Log

| Date | Round/Topic | Verdict | Notes |
|------|-------------|---------|-------|
| 2026-11-13 | Seed / Project kickoff | See notes | Aesthetic pole = sculptural horror (Giger + Beksiński surface language, Lovecraft conceptual). Format = undecided, explore in mood board (relief vs full-sculpture). Size ~3×2–3×3 ft. Review UX = phone swipe board (GitHub Pages) + email ping; verdicts via GitHub issue JSON. Hierarchy = 3 levels (Evan → Orchestrator → Leads → Workers). Batch 1 = 12 images across 3 axes: (1) Giger-vs-Beksiński surface language, (2) wall-format relief vs full-sculpture, (3) mask treatment. |
| 2026-11-14 | Review methodology restructure | Approved (Evan, direct chat) | Problem: linear axis-walk mixing structural/aesthetic/decor/artistic wires. Fix: 48 cards per round = 4 parallel groups × 12, each searching one aspect independently — (1) artistic: Shoggoth/Lovecraft art from DeviantArt/ArtStation etc., heavy Beksiński lean; (2) surface-aesthetic: texture/palette/finish; (3) interior-decor: horror piece in real rooms; (4) structural-format: mount/relief typologies. Much higher search temperature — ~1/3 of slots per group are deliberate outliers. Copyrighted art hotlinked from artists' hosts, never committed to repo (Evan OK). Review-app edited (Evan OK, overrides DO NOT EDIT once) to pass through absolute image URLs. |
| 2026-11-14 | round-03 | 14 love / 13 like / 21 dislike (issue #3) | Artistic: Beksiński sweep — AA78, 1984, Y, 1957 relief all loved + Beksiński-idiom digital art (docchannard, Bolzak, ink-drawing) loved; historic-medium outliers (ukiyo-e, tapestry, stained glass) all dead. Surface core locked: calcified webbing (s01), mummified ochre (s02), bone crust (s03), flowstone (s05), rust (s06) loved; coral/barnacle repeat textures dead; gloss (urushi/scarab/raku/verdigris) mild positive → accent-only. Decor: refined dark rooms win (velvet salon d03 love; minimal d10, moody-light d07/d08 like); cluttered gothic + whole-room Giger dead. Format: Ghiberti bas-relief (f02) + Wu Zei multi-anchor freeform spread (f04) both loved — depth-variance hybrid; trophy/plaque dead (f06); tensegrity assist liked (f11). |
| 2026-11-14 | round-02 | 1 love-equiv / 3 like / 4 dislike (issue #2) | Chibi/plush = hard no ("should not be chibi at all... focus on the artwork of beksinski"). Gaudí organic architecture "great great direction" (05). Mosaic sprawl: right volume, wrong venue — points to initial design vision (07). Coral texture out (10, confirmed by r03 s07). |
| 2026-11-14 | Vision sketch ingested (IMG_0073) | Standing constraints | Sketch: smiley mask + separate toothy maw on body; freeform tentacle sprawl. Three load-bearing tentacle spans are PLANT SHELVES — flat enough for plants, protruding enough that plants are vertically unobstructed; supported (e.g. nails) to carry plant load safely. Whole structure wants "lots of horizontal protrusion variance from the wall." Orchestration notes: generative tools to be used heavily in aesthetic design. |
| 2026-11-15 | Structural design case | Confirmed (Evan, direct chat) | Wall: drywall on wood studs. Drilling: approved ("smallish holes but any needed") → French cleat + stud screws is the primary mount (D/C 0.3-0.7); sketch's nails formally retired (fail ~2x over capacity). Buttress tentacle approved for shelves ≥25 cm (sculpted limb; foot needs bearing pad + shear fastener, ~74 N horizontal). Plant load ceiling confirmed: 5 kg/shelf with 1.5 safety factor. |
| 2026-11-14 | round-04 | 6 love / 18 like / 19 dislike (issue #4) | CONCEPTS VALIDATED: c01 velvet-salon baseline + c02 stone-smile both loved ("absolutely excellent"; "oh my god also amazing"). Directives: horrific asymmetry + sleek Beksiński (c03 note); less octopus-literal, more horrific (c07); not a centerpiece — dial back attention-grabbing (c05); mask deserves a dedicated design round (c04). Mask: Bayon m01 loved, m12 + smiley graphic m07 + Bomarzo void-mouth m08 liked; ALL applied-object masks dead (gold/Noh/Budai/comedy/Venetian/folk) → mask is carved into the mass (serene monumental or flat graphic), never worn. Plants: root-over-rock bonsai p07 loved → tentacle-grips-pot geometry; trailing/kokedama/planter-tile/living-wall liked; creature-covered-in-plants dead. Depth: Gaudí gradient v03 + Shlian crisp projection v08 loved; Rodin v01 / Pergamon v04 / El Transparente v06 / clay-model v11 liked; dead: Bernini niche-drama v02, Trevi burst v05, false-perspective v07, acoustic panels v09, climbing wall v10, figurehead v12. Corner-wrap concept shelved for later per c05 note ("worth exploring down the road", dial back attention-grabbing). |
| 2026-11-14 | Correction (r02/r03 tallies) | Supersedes counts in two rows above | Round-03 is 15 love / 13 like / 20 dislike (not 14/21). Round-02 is 0 love / 3 like / 4 dislike — "great great direction" was a note on like-05, not a love. Takeaway content in both rows stands. Caught by docs-reviewer (haiku). |
| 2026-11-14 | round-01 | 4 love / 3 like / 5 dislike (issue #1) | Surface: Beksiński decay palette wins (03 like, 04 love); Giger biomech skin + gothic vertebral rejected (01, 02) except where sculpture merges with wall architecture (08 love). New constraint: must blend with interior decor + carry mild-cutesy element (01 notes). Format: all wall-relief/trophy formats loved (06, 07, 08); 05 liked with note "much more freeform and concentrated on the wall". Mask: all literal mask refs rejected (09, 10, 11); 12 (shoggoth body context) liked. Round-02 axes set: cutesy-horror balance, wall-integration/relief depth, surface-finish. |

---
*Edit log*

| Date | Agent | Change | Signed-off-by |
|------|-------|--------|---------------|
| 2026-11-13 | docs-lead | Initial creation + seed entry | docs-reviewer |
| 2026-11-14 | orchestrator | Appended round-01 verdict entry | docs-reviewer |
| 2026-11-14 | orchestrator | Appended review-methodology restructure (Evan, direct) | docs-reviewer |
| 2026-11-14 | orchestrator | Appended r02+r03 verdicts, vision-sketch constraints | docs-reviewer (haiku) |
| 2026-11-14 | orchestrator | Appended round-04 verdict row | docs-reviewer (haiku) |
| 2026-11-15 | orchestrator | Appended structural design case (Evan answers) | [PROVISIONAL] |
