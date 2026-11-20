# python3 move.py map.tsv [--apply]   map.tsv: <late line> <target module>   (target '-' = оставить)
import sys,collections,json;sys.path.insert(0,'/workspace/rf')
from plan import *
late='overrides/late.css';L0=modstart[late];s=texts[late]
blocks=collections.OrderedDict()
for r in rules[L0:]: blocks.setdefault(r['top'],[]).append(r)
byline={s.count('\n',0,t[0])+1:t for t in blocks}
# старт блока по строке: строка, где начинается первый непробельный символ блока
def first_line(t):
    st=t[0]
    while st<t[1] and s[st] in ' \n\t': st+=1
    return s.count('\n',0,st)+1
byfl={first_line(t):t for t in blocks}
EV={}
if '--evidence' in sys.argv:
    for a,b,r in json.load(open(sys.argv[sys.argv.index('--evidence')+1])): EV[(a,b)]=r
def evidenced(x):
    r=EV.get((x[2],x[3]))
    if r is None or r.get('err') or r['co']: return False
    return bool(r['a'] and r['b']) or C.class_disjoint2(x[2],x[3])
mp=[l.split() for l in open(sys.argv[1]) if l.strip() and not l.startswith('#')]
moves=collections.defaultdict(list);bad=0
tgt_of={}
for ln,tgt in mp:
    t=byfl.get(int(ln)) or byline.get(int(ln))
    if t: tgt_of[t]=tgt
for ln,tgt in mp:
    ln=int(ln);t=byfl.get(ln) or byline.get(ln)
    if not t: print('NO BLOCK at',ln);bad+=1;continue
    rs=blocks[t];P=modend[tgt];c=[]
    # правила late, которые переезжают в тот же модуль или раньше, окажутся перед R — не мешают
    ign=set(x['i'] for x in rs)
    for t2,tg2 in tgt_of.items():
        if t2!=t and M.index(tg2)<=M.index(tgt): ign|=set(x['i'] for x in blocks[t2])
    for r in rs: c+=conflicts(r,P,r['i'],ignore=ign)
    if EV:
        ev=[x for x in c if evidenced(x)];c=[x for x in c if not evidenced(x)]
        if ev: print('EVIDENCE',ln,len(ev),'пар разведены корпусом')
    if c:
        bad+=1;print('CONFLICT',ln,tgt);[print('   ',x[1],x[2][:70],'|',x[3][:70],x[4],x[5]) for x in c[:6]]
    moves[tgt].append(t)
if bad or '--apply' not in sys.argv: print('moves',sum(len(v) for v in moves.values()),'bad',bad);sys.exit(1 if bad else 0)
cut=sorted([t for v in moves.values() for t in v])
for tgt,ts in moves.items():
    add=''.join('\n'+s[t[0]:t[1]].strip('\n') for t in sorted(ts))
    p=os.path.join(SRC,tgt);txt=open(p,encoding='utf-8').read().rstrip('\n')
    open(p,'w',encoding='utf-8').write(txt+'\n'+add+'\n')
out=[];pos=0
for t in cut: out.append(s[pos:t[0]]);pos=t[1]
out.append(s[pos:]);ns=''.join(out)
ns=re.sub(r'\n{3,}','\n\n',ns)
open(os.path.join(SRC,late),'w',encoding='utf-8').write(ns)
print('applied',len(cut),'blocks; late',len(s),'->',len(ns))
