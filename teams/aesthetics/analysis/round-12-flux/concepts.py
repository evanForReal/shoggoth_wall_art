"""Round-12 FLUX concepts: one base description carrying every locked essential (session log SL-83; volumetric mask per r11 verdict, SL-89)
plus one variation phrase per concept (axes from SL-83). Run: python3 teams/aesthetics/analysis/round-12-flux/concepts.py OUTDIR"""
import subprocess, sys, json, os
BASE = ("Museum photograph of a single horror bas-relief wall sculpture in the style of Zdzislaw Beksinski, attached directly to a dark charcoal wall, no backboard. "
 "A headless, faceless tentacled shoggoth: a tall narrow ribbed trunk of decayed ochre, umber and bone-colored flesh with fibrous root-like texture and thin perforated lace webbing between limbs. "
 "The top of the trunk is a stump covered by a seething cluster of bulging bloodshot veiny eyeballs of mismatched sizes, diseased and swollen. "
 "The mask is a solid ball with real volume, a slightly squashed sphere of smooth pale ivory bone, carved on its front with the classic smiley emoticon: two small solid black vertical ovals for eyes and one thin black upward-curved arc for the mouth. It is a round three-dimensional ball, not a flat disc, not a theatre mask, not a skull, not a head: no teeth, no nose, no ears. The creature holds this cheerful ball up to deceive the viewer. "
 "{MASK} "
 "{MOUTH} "
 "Three tentacles of very different thickness, one massive, one medium, one thin, each curl underneath a small flat wooden plant shelf and hold it up; each shelf has a potted plant. "
 "{WHIP} "
 "{BODY} "
 "Dramatic warm downlight, gothic, horrific, elegant, highly detailed sculpture.")
C = {
 "C1": dict(MASK="One tentacle holds the mask out to the upper left, a hand's width away from the body, gripping it with curled tendrils; the mask faces the viewer.",
            MOUTH="In the middle of the trunk, a tall vertical slit mouth lined with long jagged needle fangs.",
            WHIP="A long thin whip tentacle curls down the right side.", BODY="The bottom dissolves into a dense hanging cascade of root tendrils, no legs."),
 "C2": dict(MASK="A tentacle arches up over the top of the creature and dangles the mask above the eye cluster, tilted at an angle.",
            MOUTH="In the trunk, a round lamprey mouth: concentric rings of small hooked teeth spiralling inward.",
            WHIP="A long thin whip tentacle rises up the left side.", BODY="The bottom trails into long thin hanging root strands, no legs."),
 "C3": dict(MASK="The mask is being lowered: a tentacle holds it down beside the mouth, half revealing the eye cluster above as if the creature is taking off its mask.",
            MOUTH="A tall vertical slit mouth with long jagged fangs, just beside the lowered mask.",
            WHIP="A long whip tentacle curls under one shelf.", BODY="The body leans to the left; the bottom is a short dense knot of hanging tendrils, no legs."),
 "C4": dict(MASK="A thin tentacle is threaded through a hole bored through the mask ball and holds it up like a bead on a string, the mask hanging slightly crooked in front of the body.",
            MOUTH="A tall vertical slit mouth lined with long jagged fangs.",
            WHIP="A long thin whip tentacle reaches out to the edge of the frame.", BODY="Bulging eyes also trail down the trunk in a line; the bottom hangs into an asymmetric cascade of tendrils, no legs."),
 "C5": dict(MASK="A tentacle holds the mask out to the right, turned partly away from the viewer, so its smooth blank side shows; small bulging eyes grow along the holding tentacle.",
            MOUTH="A large gaping vertical maw, taller than wide, lined with long jagged fangs.",
            WHIP="A long thin whip tentacle curls down the right side.", BODY="The bottom dissolves into a long trailing cascade of root tendrils, no legs."),
 "C6": dict(MASK="A tentacle coils once around the mask ball and holds it out in front of the eye cluster, a hand's width from the body.",
            MOUTH="A vertical mouth with both a ring of small hooked lamprey teeth and a few long fangs.",
            WHIP="A long whip tentacle rises up the left side.", BODY="The bottom trails into long hanging root strands, no legs."),
 "C7": dict(MASK="A tentacle rises from below and lifts the mask up in front of the eye cluster, tilted.",
            MOUTH="A tall vertical slit mouth lined with long jagged fangs.",
            WHIP="A long thin whip tentacle curls under the lowest shelf.", BODY="The massive tentacle carries the highest shelf on the upper right; the bottom is a short dense knot of tendrils, no legs."),
 "C8": dict(MASK="A tentacle holds the mask out to the side, strongly tilted, about to slip from its grip.",
            MOUTH="A tall vertical slit mouth with long jagged fangs.",
            WHIP="A long whip tentacle reaches out to the edge of the frame.", BODY="The body leans to the right; bulging eyes spread down the trunk; the bottom is an asymmetric hanging cascade, no legs."),
 "C9": dict(MASK="One tentacle holds the mask out to the upper left, facing the viewer, gripping it with curled tendrils.",
            MOUTH="A round lamprey mouth with concentric rings of hooked teeth.",
            WHIP="A long thin whip tentacle curls down the right side.", BODY="Dense Beksinski lace webbing and perforated membranes stretch between all the tentacles; the bottom dissolves into a dense cascade of root tendrils, no legs."),
 "C10": dict(MASK="Seen from a three-quarter side angle: the mask hovers a hand's width in front of the body on its tentacle, and the seething eye cluster is visible in the gap behind it.",
            MOUTH="A tall vertical slit mouth lined with long jagged fangs.",
            WHIP="A long thin whip tentacle curls down one side.", BODY="The bottom dissolves into a hanging cascade of root tendrils, no legs."),
}
SEEDS = [101, 202]
if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True); log = []
    # seed-major order: one image per concept first, so a partial daily quota still covers every concept
    for s in SEEDS:
        for cid, v in C.items():
            p = BASE.format(**v)
            f = f"{out}/{cid}_s{s}.png"
            if os.path.exists(f): continue
            r = subprocess.run(["python3", "tools/concept_gen/flux.py", f, str(s), p], capture_output=True, text=True, timeout=240)
            ok = r.returncode == 0
            log.append({"concept": cid, "seed": s, "ok": ok, "err": None if ok else r.stderr.strip().splitlines()[-1][:200]})
            print(cid, s, "ok" if ok else log[-1]["err"], flush=True)
            if not ok and "ZeroGPU" in (log[-1]["err"] or ""): json.dump(log, open(f"{out}/gen_log.json", "a"), indent=1); sys.exit("quota exhausted")
    json.dump({"base": BASE, "concepts": C, "seeds": SEEDS, "log": log}, open(f"{out}/gen_log.json", "w"), indent=1)
