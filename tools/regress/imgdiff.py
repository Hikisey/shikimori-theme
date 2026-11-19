#!/usr/bin/env python3
# imgdiff.py dirA dirB outdir  -> prints per image % changed pixels (>24 on any channel)
import sys,os,glob
from PIL import Image,ImageChops
import numpy as np
A,B,O=sys.argv[1:4];os.makedirs(O,exist_ok=True);rows=[]
for fa in sorted(glob.glob(A+'/**/*.png',recursive=True)):
    rel=os.path.relpath(fa,A);fb=os.path.join(B,rel)
    if not os.path.exists(fb): rows.append((rel,'MISSING',0));continue
    a=Image.open(fa).convert('RGB');b=Image.open(fb).convert('RGB')
    if a.size!=b.size:
        h=min(a.size[1],b.size[1]);w=min(a.size[0],b.size[0]);note=f'size {a.size}->{b.size}'
        a=a.crop((0,0,w,h));b=b.crop((0,0,w,h))
    else: note=''
    d=np.abs(np.asarray(a,dtype=np.int16)-np.asarray(b,dtype=np.int16)).max(axis=2)
    pct=(d>24).mean()*100
    rows.append((rel,f'{pct:.3f}%',note))
    if pct>0.05:
        m=(d>24); ys=np.where(m.any(axis=1))[0]
        out=np.asarray(b).copy(); out[m]=[255,0,255]
        os.makedirs(os.path.dirname(os.path.join(O,rel)),exist_ok=True)
        Image.fromarray(out).save(os.path.join(O,rel))
        rows[-1]=rows[-1]+(f'rows {ys.min()}-{ys.max()}',)
for r in rows: print(*r)
