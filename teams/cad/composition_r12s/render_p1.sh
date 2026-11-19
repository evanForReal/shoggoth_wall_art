#!/bin/bash
cd "$(dirname "$0")"
python3 render_comp.py S1 --views tq,side,rake --samples 24 >/dev/null 2>&1
for s in S2 S3; do python3 render_comp.py $s --views front,tq,side,rake --samples 24 >/dev/null 2>&1; done
echo P1DONE
