#!/bin/bash
cd "$(dirname "$0")"
for s in "$@"; do python3 render_comp.py $s --views front,tq,side --samples 24 --mask > /dev/null 2>&1; echo rendered $s; done
echo ALLDONE2
