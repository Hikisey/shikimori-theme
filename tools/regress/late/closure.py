# python3 closure.py  -> для каждого модуля: наибольший набор блоков late (по догадке плана), который можно перенести вместе
import sys,json,collections;sys.path.insert(0,'/workspace/rf')
from plan import *
EV={}
for a,b,r in json.load(open('comatch2.json')): EV[(a,b)]=r
def evid(x):
    r=EV.get((x[2],x[3]))
    if r is None or r.get('err') or r['co']: return False
    return bool(r['a'] and r['b']) or C.class_disjoint2(x[2],x[3])
late='overrides/late.css';L0=modstart[late];s=texts[late]
blocks=collections.OrderedDict()
for r in rules[L0:]: blocks.setdefault(r['top'],[]).append(r)
plan=json.load(open('plan.json'))
tg={tuple(b['top']):b['tgt'] for b in plan}
skip=set(json.loads(sys.argv[1])) if len(sys.argv)>1 else set()
cand={t:tg.get(t) for t in blocks if tg.get(t) and tg.get(t) not in skip}
it=0
while True:
    it+=1;drop=[]
    for t,tgt in cand.items():
        ign=set()
        for t2,g2 in cand.items():
            if M.index(g2)<=M.index(tgt): ign|=set(x['i'] for x in blocks[t2])
        c=[]
        for r in blocks[t]: c+=[x for x in conflicts(r,modend[tgt],r['i'],ignore=ign) if not evid(x)]
        if c: drop.append(t)
    print('iter',it,'cand',len(cand),'drop',len(drop),file=sys.stderr)
    if not drop: break
    for t in drop: del cand[t]
out=[]
for t,tgt in cand.items():
    a=t[0]
    while s[a] in ' \n\t': a+=1
    out.append((s.count('\n',0,a)+1,tgt,t[1]-t[0]))
json.dump(out,open('closure.json','w'))
agg=collections.Counter()
for l,tgt,n in out: agg[tgt]+=n
print(agg.most_common(),sum(agg.values()))
