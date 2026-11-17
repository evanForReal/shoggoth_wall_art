#!/bin/sh
# Full-piece v2 pipeline: per variant, field -> mesh -> grain -> renders. Usage: run_all.sh OUTDIR
set -e
D=$(cd "$(dirname "$0")" && pwd); O=$1; mkdir -p $D/renders
for v in hero v1_liftedge v2_eyes_heavy v3_maw_big v4_weathered v5_tentacles5; do
  python3 $D/gen_fullpiece.py --variant $v --vox 2.0 --out $O
  if [ "$v" = hero ]; then VIEWS=front,tq,rake,side,maw; else VIEWS=front,tq; fi
  python3 $D/render_full.py $O $v $D/renders --views $VIEWS --w 1200 --h 900 --samples 48
done
