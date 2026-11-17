import sys, importlib.util, numpy as np
spec=importlib.util.spec_from_file_location('g','/home/user/shoggoth_wall_art/tools/composition_gate.py'); g=importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
for s in sys.argv[1:]:
    sil=np.load(f'build/{s}_sil.npy'); m=sil.T[::-1]; sq,box=g.envelope(m); t,f=g.torso_blob(sq); ys,xs=np.where(t); print(s,'torso w',round((xs.max()+1-xs.min())/g.N,3),'x',round(xs.min()/g.N,3),round(xs.max()/g.N,3))
