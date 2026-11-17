#!/bin/sh
# Full-piece v2.1 pipeline. Usage: run_all.sh OUTDIR
set -e
D=$(cd "$(dirname "$0")" && pwd); O=$1; mkdir -p $D/renders
for v in hero v1_liftedge v2_tentacles5 v3_maw_big; do
  python3 $D/gen_fullpiece.py --variant $v --vox 2.0 --out $O
  if [ "$v" = hero ]; then VIEWS=front,tq,rake,side,maw; else VIEWS=front,tq; fi
  python3 $D/render_full.py $O $v $D/renders --views $VIEWS --w 1200 --h 900 --samples 48
done
echo PIPELINE_DONE
