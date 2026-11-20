import re,os,sys,collections
sys.path.insert(0,'/workspace/rf');import cascade as C
SRC=C.SRC;M=C.man()
texts={f:open(os.path.join(SRC,f),encoding='utf-8').read() for f in M}
rules=[];modstart={}
for f in M:
    modstart[f]=len(rules);C.flatten(texts[f],f,out=rules)
for i,r in enumerate(rules): r['i']=i
modend={f:(modstart[M[k+1]] if k+1<len(M) else len(rules)) for k,f in enumerate(M)}
def toks(sel):
    return set(re.findall(r'[.#][\w-]+',sel))
tokmod=collections.defaultdict(collections.Counter)
for r in rules:
    if r['file']=='overrides/late.css': continue
    for s in r['sels']:
        for t in toks(s): tokmod[t][r['file']]+=1
PAGE={'.p-profiles':'pages/profile.css','.p-profiles-show':'pages/profile.css','#profiles_show':'pages/profile.css','.profile-head':'pages/profile.css',
 '.p-dashboards-show':'pages/dashboard.css','.p-dashboards':'pages/dashboard.css','#dashboards_show':'pages/dashboard.css',
 '.p-topics':'pages/forum.css','.p-forum':'pages/forum.css','.b-comment':'pages/forum.css',
 '.p-animes_collection-index':'pages/catalog.css','.p-animes_collection':'pages/catalog.css',
 '.p-user_rates':'pages/lists.css','.p-user_rates-index':'pages/lists.css',
 '.p-clubs':'pages/clubs.css','.p-messages':'pages/messages.css','.p-achievements':'pages/achievements.css','.p-contests':'pages/contests.css',
 '.p-profiles-edit':'pages/settings.css','.p-user_preferences':'pages/settings.css',
 '.p-animes-show':'pages/anime.css','.p-db_entries':'pages/anime.css','.p-db_entries-show':'pages/anime.css','.mfp-wrap':'components/modals.css',
 '.l-top_menu-v2':'layout/header.css','.b-shiki_editor':'components/editor.css','.b-shiki_editor-v2':'components/editor.css'}
def guess(rs):
    sc=collections.Counter()
    for r in rs:
        for s in r['sels']:
            for t in toks(s):
                if t in PAGE: sc[PAGE[t]]+=5
                tot=sum(tokmod[t].values())
                if tot:
                    for f,c in tokmod[t].items(): sc[f]+=c/tot
    return sc.most_common(3)
def conflicts(R,P,L,ignore=set()):
    out=[]
    for i in range(P,L):
        X=rules[i]
        if i in ignore or not X['decls']: continue
        if C.ctx_disjoint(R['ctx'],X['ctx']): continue
        for (p,imp,v) in R['decls']:
            for (q,imp2,v2) in X['decls']:
                if imp!=imp2 or not C.overlap(p,q): continue
                if C.norm(p)==C.norm(q) and C.vnorm(v)==C.vnorm(v2): continue
                for s in R['sels']:
                    sp=C.spec(s)
                    for t in X['sels']:
                        if C.spec(t)==sp and C.compatible(s,t) and not C.page_disjoint(s,t) and not C.class_disjoint(s,t):
                            out.append((i,X['file'],s,t,p,q));break
    return out
if __name__=='__main__':
    late='overrides/late.css';L0=modstart[late]
    blocks=collections.OrderedDict()
    for r in rules[L0:]:
        blocks.setdefault(r['top'],[]).append(r)
    s=texts[late]
    tot_ok=0
    for top,rs in blocks.items():
        g=guess(rs);tgt=g[0][0] if g else None
        line=s.count('\n',0,top[0])+1
        size=top[1]-top[0]
        if tgt:
            P=modend[tgt];c=[]
            for r in rs: c+=conflicts(r,P,r['i'],ignore=set(x['i'] for x in rs))
        print(f"{line:5} {size:6} {tgt or '-':28} conf={len(c) if tgt else '-':<4} {clean if False else ''}{rs[0].get('pre',rs[0].get('at',''))[:70]!r}  ctx={rs[0]['ctx'][:1]}")
