# python3 remap.py map.tsv TAG > newmap.tsv : строки map (по late.css из TAG) -> строки в текущем late.css
import sys,subprocess,re,collections;sys.path.insert(0,'/workspace/rf');import cascade as C
old=subprocess.check_output(['git','-C','/workspace/st','show',sys.argv[2]+':src/overrides/late.css']).decode()
cur=open('/workspace/st/src/overrides/late.css',encoding='utf-8').read()
def blocks(s):
    out={}
    for (st,en,pre,bs) in C.parse_blocks(s):
        a=st
        while a<en and s[a] in ' \n\t': a+=1
        out[s.count('\n',0,a)+1]=s[a:en]
        out.setdefault(s.count('\n',0,st)+1,s[a:en])
    return out
ob=blocks(old);cb=blocks(cur);rev=collections.defaultdict(list)
seen=set()
for (st,en,pre,bs) in C.parse_blocks(cur):
    a=st
    while a<en and cur[a] in ' \n\t': a+=1
    rev[cur[a:en]].append(cur.count('\n',0,a)+1)
for l in open(sys.argv[1]):
    if not l.strip() or l.startswith('#'): continue
    ln,tgt=l.split();t=ob[int(ln)];c=rev.get(t,[])
    if len(c)!=1: print('#AMBIG',ln,len(c),file=sys.stderr);continue
    print(c[0],tgt)
