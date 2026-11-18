#!/bin/bash
# build + render all r11 studies. H gets extra views.
cd "$(dirname "$0")"
for s in H V1 V2 V3 V4; do python3 build.py $s || exit 1; done
python3 render_comp.py H --views front,tq,side,sideL,close --samples 24 --mask
python3 render_comp.py H --views prof --samples 16 --clipx -150
for s in V1 V2 V3 V4; do python3 render_comp.py $s --views front,tq,side --samples 24 --mask; done
echo ALLDONE
