#!/bin/bash
cd "$(dirname "$0")"
for s in S1 S2 S3; do python3 render_comp.py $s --views front,tq,side,rake --samples 24 >/dev/null 2>&1; echo $s; done
echo P1DONE
