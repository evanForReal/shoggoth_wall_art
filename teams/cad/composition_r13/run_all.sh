#!/bin/bash
# r13 pipeline: build, measure, render. H13 on the 914 grid, E1 needs R13_VAR=E1.
cd "$(dirname "$0")"
for v in H13 E1; do
  export R13_VAR=$v
  python3 build.py $v >/dev/null 2>&1 || exit 1
  OUTJSON=arm_report_$v.json python3 measure_arm.py $v >/dev/null 2>&1
  OUTJSON=measure_extra_$v.json python3 measure_extra.py $v >/dev/null 2>&1
  python3 render_comp.py $v --views front,tq,side --samples 24 --mask >/dev/null 2>&1
  python3 render_comp.py $v --views front --samples 24 --plants --ortho 1.85 >/dev/null 2>&1
  echo done $v
done
unset R13_VAR; python3 measure_gap.py
echo ALLDONE
