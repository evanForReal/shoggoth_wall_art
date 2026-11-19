#!/bin/bash
cd "$(dirname "$0")"
for c in C1 C2 C3 C4 C6 C8 C9 C10; do python3 render_comp.py ${c}_S2 --views front,tq,side --samples 24 >/dev/null 2>&1; echo $c; done
echo P2DONE
