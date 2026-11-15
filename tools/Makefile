# Usage (repo root):  make -f tools/Makefile p0 | validate | test | clean-reports
ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/..)
PY   := PYTHONPATH=$(ROOT) python
P0   := $(ROOT)/prototype/p0
OUT  := $(P0)/out
REP  := $(P0)/reports
PITCH ?= 1.6
GEN   ?= 1

.PHONY: p0 gen schema fea analytic crosscheck printcheck skinswap consolidate validate test clean-reports

p0: gen schema fea analytic crosscheck printcheck skinswap consolidate
	@echo "P0 chain done -> $(REP)/P0_REVIEW.md"

gen:
	@if [ "$(GEN)" = "1" ] && [ -f $(P0)/generate.py ]; then cd $(ROOT) && python $(P0)/generate.py --no-previews; else echo "generate skipped (GEN=$(GEN) or no generate.py)"; fi

schema:
	$(PY) $(ROOT)/tools/schema_check.py $(P0)/params.json $(P0)/loadcases.json

fea:
	$(PY) -m sim.run_fea --underlay $(OUT)/underlay.stl --skin $(OUT)/skin.stl --params $(P0)/params.json --loadcases $(P0)/loadcases.json --out $(REP) --pitch $(PITCH)

analytic:
	$(PY) -m sim.analytic.run_analytic --underlay $(OUT)/underlay.stl --skin $(OUT)/skin.stl --params $(P0)/params.json --out $(REP) $(if $(wildcard $(REP)/_joints.json),--joints $(REP)/_joints.json,)

crosscheck:
	$(PY) $(ROOT)/tools/crosscheck.py $(REP)/fea.json $(REP)/analytic.json --out $(REP)

printcheck:
	$(PY) -m printcheck.run_printcheck --underlay $(OUT)/underlay.stl --assembly $(OUT)/assembly.stl --segments $(OUT)/segments --params $(P0)/params.json --analytic $(REP)/analytic.json --fea-fields $(REP)/fea_fields.npz --out $(REP)

skinswap:
	$(PY) $(ROOT)/tools/skin_swap.py --underlay $(OUT)/underlay.stl --skin $(OUT)/skin.stl --params $(P0)/params.json --out $(REP)

consolidate:
	$(PY) $(ROOT)/tools/consolidate.py --reports $(REP) --p0 $(P0)

validate:
	$(PY) -m sim.validate
	$(PY) -m unittest tests.test_analytic_vs_closed_form -v

test:
	$(PY) -m unittest discover -s $(ROOT)/tests -t $(ROOT) -v

clean-reports:
	rm -f $(REP)/fea.* $(REP)/fea_fields.npz $(REP)/analytic.* $(REP)/printability.* $(REP)/crosscheck.* $(REP)/skin_swap.* $(REP)/P0_REVIEW.md
