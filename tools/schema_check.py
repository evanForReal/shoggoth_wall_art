"""JSON-schema check: python tools/schema_check.py params.json loadcases.json [report.json ...]. Exit 1 on failure.
Schemas are deliberately tolerant of Geometry's extra keys (additionalProperties allowed) but require the spec keys."""
import json, sys
from pathlib import Path
import jsonschema

S = {
 "params": {"type": "object", "required": ["span_length", "root_diameter", "tip_diameter", "shell_wall", "material"],
            "properties": {"span_length": {"type": "number", "exclusiveMinimum": 0}, "root_diameter": {"type": "number", "exclusiveMinimum": 0},
                           "tip_diameter": {"type": "number", "exclusiveMinimum": 0}, "shell_wall": {"type": "number", "minimum": 0.8},
                           "material": {"enum": ["PETG", "PLA"]}, "anchor_plate": {"type": "object"}, "body_stub": {"type": "object"}}},
 "loadcases": {"type": "object", "required": ["materials", "load_cases", "criteria", "anchor"],
               "properties": {"load_cases": {"type": "array", "minItems": 5, "items": {"type": "object", "required": ["id", "kind"]}},
                              "materials": {"type": "object", "minProperties": 1}}},
 "report_fea": {"type": "object", "required": ["tool", "model", "load_cases", "modal", "summary", "solver_validation"]},
 "report_analytic": {"type": "object", "required": ["tool", "load_cases", "modal", "anchor", "summary"]},
 "report_printability": {"type": "object", "required": ["tool", "checks", "summary", "underlay"]},
 "report_crosscheck": {"type": "object", "required": ["tool", "rows", "summary"]},
 "report_skin_swap": {"type": "object", "required": ["tool", "checks", "summary"]},
}

def kind(p, d):
    n = Path(p).name
    if n == "params.json": return "params"
    if n == "loadcases.json": return "loadcases"
    for k in ("fea", "analytic", "printability", "crosscheck", "skin_swap"):
        if n.startswith(k + ".json"): return "report_" + k
    return None

def main(argv):
    bad = 0
    for p in argv:
        d = json.loads(Path(p).read_text()); k = kind(p, d)
        if k is None:
            print("SKIP (unknown kind)", p); continue
        errs = sorted(jsonschema.Draft202012Validator(S[k]).iter_errors(d), key=str)
        if errs:
            bad += 1; print("FAIL", p); [print("  -", e.message[:200]) for e in errs[:8]]
        else:
            print("OK  ", p, f"({k})")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
