# python3 selsmap.py map.tsv [map2...]  (SRC = дерево, к которому относятся строки) -> sels.json
import sys,os,json,collections;sys.path.insert(0,'/workspace/rf');import cascade as C
SRC=C.SRC;late=open(os.path.join(SRC,'overrides/late.css'),encoding='utf-8').read()
tops={}
for (st,en,pre,bs) in C.parse_blocks(late):
    a=st
    while a<en and late[a] in ' \n\t': a+=1
    tops[late.count('\n',0,a)+1]=(st,en);tops.setdefault(late.count('\n',0,st)+1,(st,en))
sels=set()
for f in sys.argv[1:]:
    for l in open(f):
        if not l.strip(): continue
        st,en=tops[int(l.split()[0])]
        for r in C.flatten(late[st:en],'x'):
            sels.update(r['sels'])
json.dump(sorted(sels),open('sels.json','w'));print(len(sels))
