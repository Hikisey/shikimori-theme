import re,glob,pickle,collections
idx=collections.defaultdict(set);n=0
tagre=re.compile(r'<([a-zA-Z][\w-]*)\b([^>]*)>')
for f in sorted(glob.glob('pages/*.html')+glob.glob('corpus/*.html')):
    s=open(f,encoding='utf-8',errors='ignore').read()
    for m in tagre.finditer(s):
        a=m.group(2); c=re.search(r'\sclass="([^"]*)"',a)
        if not c: c=re.search(r"()","")
        n+=1
        for k in set(c.group(1).split())|{"<"+m.group(1).lower()}: idx[k].add(n)
pickle.dump(dict(idx),open('clsidx.pkl','wb'));print(n,len(idx))
