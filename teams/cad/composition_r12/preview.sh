#!/bin/bash
cd "$(dirname "$0")"
for s in C2 C3 C4 C5 C6 C7 C8 C9 C10; do python3 render_comp.py $s --views front,side --samples 10 > /dev/null 2>&1; echo done $s; done
echo PREVIEWDONE
