#!/bin/sh
# Gate 2 pipeline: field -> min-wall clamp+fill -> pre-sculpt validate -> bpy sculpt -> re-validate -> renders.  Usage: run_all.sh OUTDIR
set -e
D=$(cd "$(dirname "$0")" && pwd); O=$1
python3 $D/gen_patch.py --vox 0.5 --out $O
python3 $D/minwall.py $O --clamp --fill
python3 $D/validate_patch.py $O/raw_mesh_clamped.npz $O
python3 $D/sculpt.py $O --tag strong --amp-rib 1.3 --amp-mem 0.5 --along-scale 1.8 --grain-scale 0.9
python3 $D/validate_sculpt.py $O strong --stl
python3 $D/render_views.py $O/sculpt_strong.npz $D/renders --w 1200 --h 900 --samples 80
