#!/bin/bash
# build + render all r12 concepts
cd "$(dirname "$0")"
for s in C1 C2 C3 C4 C5 C6 C7 C8 C9 C10; do [ "$1" == "build" ] && python3 build.py $s; done
for s in C1 C2 C3 C4 C5 C6 C7 C8 C9 C10; do python3 render_comp.py $s --views front,tq,side --samples 24 --mask > /dev/null 2>&1; echo rendered $s; done
echo ALLDONE
