#!/usr/bin/env python3
# mkstyle.py <parts_dir> <site.css> <out.css> : emulate shikimori filter, undo camo, append palette
import sys,glob,os,re,subprocess,urllib.parse,shutil,tempfile
T=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d,site,out=sys.argv[1:4]
tmp=tempfile.mkdtemp()
parts=sorted(glob.glob(os.path.join(d,'part_*.css')))
fs=[]
for p in parts:
    q=os.path.join(tmp,os.path.basename(p)); shutil.copy(p,q); fs.append(q)
s=re.sub(r'@import url\("[^"]*"\);','',open(site,encoding='utf-8').read())
sp=os.path.join(tmp,'site.css'); open(sp,'w',encoding='utf-8').write(s); fs.append(sp)
subprocess.run([sys.executable,os.path.join(T,'shiki_compile.py')]+fs,check=True)
css=''.join(open(f+'.shiki',encoding='utf-8').read()+'\n' for f in fs)
css=css.replace('https://camo.example/x?url=','')
css=re.sub(r'url\((["\']?)(https?%3A[^)"\']*|%2F%2F[^)"\']*)',lambda m:'url('+m.group(1)+urllib.parse.unquote(m.group(2)),css)
open(out,'w',encoding='utf-8').write(css)
print(out,len(css.encode()))
