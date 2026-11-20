#!/usr/bin/env python3
"""Разбор src/ на плоский список правил в порядке каскада + оценка безопасности переноса."""
import re, os
SRC=os.environ.get('SRC','/workspace/st/src')
def man(): return [l.strip() for l in open(os.path.join(SRC,'manifest.txt')) if l.strip() and not l.startswith('#')]
def skipc(s,i): return s.find('*/',i+2)+2
def blk_end(s,i):
    d=0;j=i
    while True:
        if s.startswith('/*',j): j=skipc(s,j); continue
        c=s[j]
        if c in '"\'':
            q=c; j+=1
            while s[j]!=q: j+=2 if s[j]=='\\' else 1
        elif c=='{': d+=1
        elif c=='}':
            d-=1
            if d==0: return j
        j+=1
def parse_blocks(s, base=0):
    """top-level блоки: (start,end,prelude,bodystart) — start включает ведущие комментарии/пробелы"""
    out=[];i=0;n=len(s);start=0
    while i<n:
        if s.startswith('/*',i): i=skipc(s,i); continue
        c=s[i]
        if c in '"\'':
            q=c;i+=1
            while s[i]!=q: i+=2 if s[i]=='\\' else 1
            i+=1;continue
        if c==';': i+=1; out.append((base+start,base+i,s[start:i],None)); start=i; continue
        if c=='{':
            e=blk_end(s,i); out.append((base+start,base+e+1,s[start:i],base+i+1)); i=e+1; start=i; continue
        i+=1
    return out
def clean(t): return ' '.join(re.sub(r'/\*.*?\*/','',t,flags=re.S).split())
def split_sel(pre):
    out,d,cur=[],0,''
    for c in pre:
        if c in '([': d+=1
        elif c in ')]': d-=1
        if c==',' and d==0: out.append(cur.strip()); cur=''
        else: cur+=c
    out.append(cur.strip()); return [x for x in out if x]
def spec(sel):
    """специфичность (a,b,c) с :is/:not/:has = максимум аргумента, :where = 0"""
    s=sel
    a=b=c=0
    i=0;n=len(s)
    while i<n:
        ch=s[i]
        if ch=='#':
            a+=1;i+=1
            while i<n and re.match(r'[\w-]',s[i]): i+=1
        elif ch=='.':
            b+=1;i+=1
            while i<n and re.match(r'[\w-]',s[i]): i+=1
        elif ch=='[':
            b+=1;i=s.index(']',i)+1
        elif ch==':':
            if s.startswith('::',i):
                c+=1;i+=2
                while i<n and re.match(r'[\w-]',s[i]): i+=1
                if i<n and s[i]=='(':
                    d=0
                    while True:
                        if s[i]=='(':d+=1
                        elif s[i]==')':
                            d-=1
                            if d==0:break
                        i+=1
                    i+=1
                continue
            m=re.match(r':([\w-]+)',s[i:]);name=m.group(1);i+=len(m.group(0))
            if name in ('before','after','first-line','first-letter','placeholder','selection','marker'):
                c+=1;continue
            if i<n and s[i]=='(':
                d=0;j=i
                while True:
                    if s[j]=='(':d+=1
                    elif s[j]==')':
                        d-=1
                        if d==0:break
                    j+=1
                arg=s[i+1:j];i=j+1
                if name in ('is','not','has','matches','-webkit-any'):
                    best=max((spec(x) for x in split_sel(arg)),default=(0,0,0))
                    a+=best[0];b+=best[1];c+=best[2]
                elif name=='where': pass
                elif name in ('nth-child','nth-last-child'):
                    b+=1
                    if ' of ' in arg:
                        best=max(spec(x) for x in split_sel(arg.split(' of ',1)[1]));a+=best[0];b+=best[1];c+=best[2]
                else: b+=1
            else: b+=1
        elif re.match(r'[a-zA-Z]',ch):
            j=i
            while j<n and re.match(r'[\w-]',s[j]): j+=1
            c+=1;i=j
        else: i+=1
    return (a,b,c)
def decls(body):
    res=[];depth=0;cur=''
    b=re.sub(r'/\*.*?\*/','',body,flags=re.S)
    for ch in b:
        if ch=='(':depth+=1
        elif ch==')':depth-=1
        if ch==';' and depth==0: res.append(cur);cur=''
        else: cur+=ch
    res.append(cur)
    out=[]
    for d in res:
        if ':' not in d: continue
        p,v=d.split(':',1);p=p.strip().lower();v=v.strip()
        if not p: continue
        out.append((p,bool(re.search(r'!\s*important\s*$',v)),v))
    return out
def flatten(text, fname, ctx=(), base=0, out=None, top=None):
    if out is None: out=[]
    for (st,en,pre,bs) in parse_blocks(text):
        if bs is None: continue
        p=clean(pre)
        body=text[bs-0:en-1] if False else text[text.index('{',st+len(pre)-len(pre))+0:]  # placeholder
        bstart=st+len(pre)+1; body=text[bstart:en-1]
        t=top if top is not None else (base+st,base+en)
        if p.startswith('@'):
            if re.match(r'@(media|supports|container|layer)\b',p):
                flatten(body,fname,ctx+(p,),base+bstart,out,t)
            else:
                out.append(dict(file=fname,ctx=ctx,at=p,sels=[],decls=[],top=t))
        else:
            out.append(dict(file=fname,ctx=ctx,sels=split_sel(p),decls=decls(body),top=t,pre=p))
    return out
LOG={'margin':['margin-top','margin-right','margin-bottom','margin-left','margin-inline-start','margin-inline-end','margin-block-start','margin-block-end','margin-inline','margin-block'],
 'padding':['padding-top','padding-right','padding-bottom','padding-left','padding-inline-start','padding-inline-end','padding-block-start','padding-block-end','padding-inline','padding-block'],
 'inset':['top','right','bottom','left','inset-inline-start','inset-inline-end','inset-block-start','inset-block-end','inset-inline','inset-block'],
 'gap':['row-gap','column-gap','grid-gap','grid-row-gap','grid-column-gap'],
 'place-items':['align-items','justify-items'],'place-content':['align-content','justify-content'],'place-self':['align-self','justify-self'],
 'font':['font-size','font-family','font-weight','font-style','line-height','font-variant','font-stretch'],
 'overflow':['overflow-x','overflow-y','overflow-inline','overflow-block'],
 'border-radius':['border-top-left-radius','border-top-right-radius','border-bottom-left-radius','border-bottom-right-radius','border-start-start-radius','border-start-end-radius','border-end-start-radius','border-end-end-radius'],
 'border-color':['border-top-color','border-right-color','border-bottom-color','border-left-color'],
 'border-width':['border-top-width','border-right-width','border-bottom-width','border-left-width'],
 'border-style':['border-top-style','border-right-style','border-bottom-style','border-left-style'],
 'size':['width','height','inline-size','block-size'],
}
PHYS={'left':'inline','right':'inline','top':'block','bottom':'block','width':'inline-size','height':'block-size'}
def norm(p):
    if p.startswith('-webkit-') and p[8:] in ('transition','transform','animation','box-shadow','border-radius','filter','mask-image','mask-size','mask-repeat','user-select','appearance','background-size','backdrop-filter','font-feature-settings','hyphens','line-clamp','box-orient','text-fill-color'): return p[8:] if p[8:]!='backdrop-filter' else p
    if p.startswith(('-moz-','-o-','-ms-')): return re.sub(r'^-(moz|o|ms)-','',p)
    return p
def group(p):
    p=norm(p)
    if p.startswith('--'): return {p}
    if p=='all': return {'*'}
    g={p}
    parts=p.split('-')
    for k in range(1,len(parts)): g.add('-'.join(parts[:k]))  # префиксы: border-top-color -> border-top, border
    for sh,lst in LOG.items():
        if p==sh or p in lst: g.add(sh); g.update(lst)
    # border-top-color <-> border-color
    m=re.match(r'border-(top|right|bottom|left|inline-start|inline-end|block-start|block-end|inline|block)-(color|width|style)$',p)
    if m: g.add('border-'+m.group(2))
    m=re.match(r'border-(color|width|style)$',p)
    if m: g.update('border-%s-%s'%(s,m.group(1)) for s in ('top','right','bottom','left','inline-start','inline-end','block-start','block-end'))
    if p.startswith('border-inline') or p.startswith('border-block') or re.match(r'border-(top|right|bottom|left)',p): g.update({'border-top','border-right','border-bottom','border-left','border-inline','border-block','border-inline-start','border-inline-end','border-block-start','border-block-end'})
    if p in ('width','height','inline-size','block-size','min-width','max-width','min-height','max-height','min-inline-size','max-inline-size','min-block-size','max-block-size'): g.update({'width','height','inline-size','block-size','min-width','max-width','min-height','max-height','min-inline-size','max-inline-size','min-block-size','max-block-size'})
    if p in ('grid-template-columns','grid-template-rows','grid-template-areas','grid-template','grid'): g.update({'grid','grid-template','grid-template-columns','grid-template-rows','grid-template-areas'})
    if p in ('flex','flex-grow','flex-shrink','flex-basis'): g.update({'flex','flex-grow','flex-shrink','flex-basis'})
    if p in ('flex-flow','flex-direction','flex-wrap'): g.update({'flex-flow','flex-direction','flex-wrap'})
    if p in ('text-decoration','text-decoration-line','text-decoration-color','text-decoration-style','text-decoration-thickness'): g.update({'text-decoration','text-decoration-line','text-decoration-color','text-decoration-style','text-decoration-thickness'})
    if p in ('list-style','list-style-type','list-style-image','list-style-position'): g.update({'list-style','list-style-type','list-style-image','list-style-position'})
    if p in ('columns','column-count','column-width'): g.update({'columns','column-count','column-width'})
    if p in ('outline','outline-color','outline-style','outline-width'): g.update({'outline','outline-color','outline-style','outline-width'})
    if p in ('mask','mask-image','mask-size','mask-repeat','mask-position','-webkit-mask','-webkit-mask-image','-webkit-mask-size','-webkit-mask-repeat','-webkit-mask-position'): g.update({'mask','mask-image','mask-size','mask-repeat','mask-position'})
    if p in ('text-fill-color','color'): g.update({'text-fill-color','color'})
    if p.startswith('scroll-margin') or p.startswith('scroll-padding'): g.update({p.rsplit('-',1)[0] if p.count('-')>1 else p})
    return g
def overlap(p,q):
    a,b=group(p),group(q)
    return '*' in a or '*' in b or bool(a & b)
def subject(sel):
    """последний компаунд, нормализованный псевдоэлемент"""
    s=re.sub(r'\([^()]*\)','()',sel)
    while '(' in s and re.search(r'\([^()]*\(',s): s=re.sub(r'\([^()]*\)','()',s)
    comp=re.split(r'\s*[>+~]\s*|\s+',s.strip())[-1]
    pe=None
    m=re.search(r'(?:::?(before|after|first-line|first-letter)(?![\w-])|::(placeholder|marker|selection|-webkit-[\w-]+|-moz-[\w-]+|backdrop|picker\([^)]*\)|picker-icon|checkmark|file-selector-button|scroll-button\([^)]*\)|[\w-]+))',comp)
    if m: pe=m.group(1) or m.group(2)
    tag=re.match(r'^([a-zA-Z][\w-]*)',comp); tag=tag.group(1).lower() if tag else None
    ids=set(re.findall(r'#([\w-]+)',comp))
    return pe,tag,ids
def compatible(s1,s2):
    p1,t1,i1=subject(s1);p2,t2,i2=subject(s2)
    if p1!=p2: return False
    if t1 and t2 and t1!=t2: return False
    if i1 and i2 and i1!=i2: return False
    return True
WIDTH=re.compile(r'\((min|max)-width:\s*(\d+)px\)')
def ctx_range(ctx):
    lo,hi=0,99999;hov=None;rm=None;sup=[]
    for c in ctx:
        for m in WIDTH.finditer(c):
            v=int(m.group(2))
            if m.group(1)=='min': lo=max(lo,v)
            else: hi=min(hi,v)
        if '(hover: hover)' in c and '(pointer: fine)' in c: hov='fine'
        elif re.search(r'\(hover:\s*none\)',c) and ',' not in c: hov='none'
        if 'prefers-reduced-motion: reduce' in c: rm=True
    return lo,hi,hov
def ctx_disjoint(a,b):
    la,ha,va=ctx_range(a);lb,hb,vb=ctx_range(b)
    if ha<lb or hb<la: return True
    if va and vb and va!=vb: return True
    return False
# ---- page-scope disjointness (body classes/ids) ----
import json as _j
_COMBOS=[set(c) for c in _j.load(open('/workspace/rf/bodycombos.json'))]
_BODYTOK=set().union(*_COMBOS)
BASE={'.p-profiles','.p-db_entries','.p-animes','.p-people','.p-characters','.p-mangas','.p-ranobe'}
def strip_fn(sel):
    s=sel
    while re.search(r':[\w-]+\([^()]*\)',s): s=re.sub(r':[\w-]+\([^()]*\)','',s)
    return s
def page_req(sel):
    s=strip_fn(sel)
    return {t for t in re.findall(r'[.#][\w-]+',s) if (t.startswith('.p-') and t in _BODYTOK) or (t.startswith('#') and t in _BODYTOK and t!='#')}
def _co(a,b): return any(a in c and b in c for c in _COMBOS)
def page_disjoint(s1,s2):
    r1,r2=page_req(s1),page_req(s2)
    for a in r1:
        for b in r2:
            if a==b or _co(a,b): continue
            if a.startswith('#') and b.startswith('#'): return True   # у body один id
            # действия одного контроллера: .p-x-show vs .p-x-index
            if a in BASE or b in BASE:
                # базовый класс может сочетаться с неизвестными подконтроллерами; доверяем только явным "чужим"
                other=b if a in BASE else a
                if other in BASE: continue
                if any(other in c and (a if other==b else b) not in c for c in _COMBOS) and not other.startswith(('.p-user','.p-messages','.p-achievements','.p-userlist','.p-polls','.p-critiques','.p-reviews')):
                    return True
                continue
            return True
    return False
def vnorm(v): return ' '.join(v.replace('!important','').split()).lower()
import pickle as _p
_IDX=_p.load(open('/workspace/rf/clsidx.pkl','rb'))
def subj_classes(sel):
    s=sel
    while re.search(r'\([^()]*\)',s): s=re.sub(r'\([^()]*\)','',s)
    comp=re.split(r'\s*[>+~]\s*|\s+',s.strip())[-1]
    return set(re.findall(r'\.([\w-]+)',comp))
def class_disjoint(s1,s2):
    a,b=subj_classes(s1),subj_classes(s2)
    if not a or not b: return False
    u=a|b
    if any(c not in _IDX for c in u): return False
    it=None
    for c in sorted(u,key=lambda c:len(_IDX[c])):
        it=_IDX[c] if it is None else it&_IDX[c]
        if not it: return True
    return False
_IDX=_p.load(open('/workspace/rf/clsidx.pkl','rb'))
def subj_tokens(sel):
    s=sel
    while re.search(r'\([^()]*\)',s): s=re.sub(r'\([^()]*\)','',s)
    comp=re.split(r'\s*[>+~]\s*|\s+',s.strip())[-1]
    t=set(re.findall(r'\.([\w-]+)',comp))
    m=re.match(r'^([a-zA-Z][\w-]*)',comp)
    if m: t.add('<'+m.group(1).lower())
    return t
def class_disjoint2(s1,s2):
    a={c for c in subj_tokens(s1) if c in _IDX};b={c for c in subj_tokens(s2) if c in _IDX}
    if not a or not b: return False
    it=None
    for c in sorted(a|b,key=lambda c:len(_IDX[c])):
        it=_IDX[c] if it is None else it&_IDX[c]
        if not it: return True
    return False
