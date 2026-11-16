#!/bin/sh
# Gate 1B pipeline: field -> min-wall measure/clamp -> validate -> renders.  Usage: run_all.sh OUTDIR
set -e
D=$(cd "$(dirname "$0")" && pwd); O=$1
python3 $D/gen_patch.py --vox 0.5 --out $O
python3 $D/minwall.py $O --clamp --fill
python3 $D/validate_patch.py $O/raw_mesh_clamped.npz $O --stl
python3 $D/render_views.py $O/patch_clean.npz $D/renders --w 1200 --h 900 --samples 80
