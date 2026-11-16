#!/bin/sh
# Full-piece composition pipeline: for each variant, field -> mesh -> grain pass -> renders.  Usage: run_all.sh OUTDIR
set -e
D=$(cd "$(dirname "$0")" && pwd); O=$1
for v in hero v1_smiley v2_nomaw v3_diagonal v4_shelvesB; do
  python3 $D/gen_fullpiece.py --variant $v --vox 2.0 --out $O
  if [ "$v" = hero ]; then VIEWS=front,tq,rake,side; else VIEWS=front,tq; fi
  python3 $D/render_full.py $O $v $D/renders --views $VIEWS --w 1200 --h 900 --samples 48
done
