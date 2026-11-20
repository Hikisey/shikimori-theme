import sys,collections,json;sys.path.insert(0,'/workspace/rf')
from plan import *
late='overrides/late.css';L0=modstart[late]
blocks=collections.OrderedDict()
for r in rules[L0:]: blocks.setdefault(r['top'],[]).append(r)
pairs=set();plan=[]
for top,rs in blocks.items():
    g=guess(rs);tgt=g[0][0] if g else None
    c=[]
    if tgt:
        P=modend[tgt]
        for r in rs: c+=conflicts(r,P,r['i'],ignore=set(x['i'] for x in rs))
    for x in c: pairs.add((x[2],x[3]))
    plan.append(dict(top=top,tgt=tgt,guess=g,conf=[list(x) for x in c]))
json.dump(plan,open('plan.json','w'))
json.dump(sorted(pairs),open('pairs.json','w'));print(len(pairs))
