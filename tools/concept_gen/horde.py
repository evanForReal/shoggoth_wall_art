"""Minimal AI Horde client (anonymous key). usage: python3 horde.py <model> <outfile> <prompt> [negative]"""
import json, sys, time, urllib.request
API='https://aihorde.net/api/v2'; KEY='0000000000'
H={'apikey':KEY,'Content-Type':'application/json','Client-Agent':'shoggoth-concepts:0.1:anonymous'}
def req(method, path, body=None):
    r=urllib.request.Request(API+path, data=json.dumps(body).encode() if body else None, headers=H, method=method)
    with urllib.request.urlopen(r, timeout=60) as f: return json.load(f)
model,out,prompt=sys.argv[1],sys.argv[2],sys.argv[3]
neg=sys.argv[4] if len(sys.argv)>4 else 'cartoon, cute, chibi, text, watermark, signature, blurry, lowres, deformed'
body={'prompt':f'{prompt} ### {neg}','params':{'width':1024,'height':1024,'steps':30,'cfg_scale':7,'sampler_name':'k_euler_a','n':1},
      'models':[model],'nsfw':False,'censor_nsfw':False,'r2':True,'shared':False}
j=req('POST','/generate/async',body); jid=j['id']; print('job',jid,j.get('kudos'),flush=True)
t0=time.time()
while True:
    s=req('GET',f'/generate/check/{jid}')
    if s.get('done'): break
    if s.get('faulted') or not s.get('is_possible',True): sys.exit(f'failed: {s}')
    if time.time()-t0>1500: sys.exit('timeout')
    time.sleep(10)
st=req('GET',f'/generate/status/{jid}'); g=st['generations'][0]
urllib.request.urlretrieve(g['img'], out); print('done',round(time.time()-t0),'s','worker',g.get('worker_name'),'model',g.get('model'),'seed',g.get('seed'))
