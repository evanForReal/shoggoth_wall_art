import json,sys
for s in sys.argv[1:]:
    d=json.load(open(f'checks/{s}.json'));print('=====',s,d['score'])
    for k in d['failed']:
        k=str(k); v=d['checks'][k]
        if k=='7': v={n:(l['taper'],l['tip_w'],l['len_over_W'],l['ok']) for n,l in v['limbs'].items()}
        elif k=='12': v={a:(b if a!='headroom' else {n:(h['clear_above_mm']) for n,h in b.items()}) for a,b in v.items() if a not in('note','pass_')}
        else: v={a:b for a,b in v.items() if a not in('note','pass_')}
        print(k,str(v)[:400])
