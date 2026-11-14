# Порт Misc::SanitizeEvilCss + Styles::Compile#camo_images (shikimori/shikimori) для проверки файлов темы.
import re,sys
def w(word): return ''.join(r'\\?'+re.escape(c) for c in word)
COMMENTS=re.compile(r'/\*.*?\*/\s*[\n\r]*',re.S|re.I)
IMPORTS=re.compile(r'''(?:@*import\s+url\(['"]?.*?['"]?\);|@*import\s+['"].*?['"]|'''+w('@')+'+'+w('import')+r''')\ ?[\n\r]*''',re.S|re.I)
EVIL=re.compile(r'\b(?:'+'|'.join(w(x) for x in ['eval','cookie','window','parent','this','javascript','vbscript','script','behavior','behaviour','expression'])+r')\b|'+w('moz-binding')+'|(?:'+w('@')+')*'+w('charset')+'|'+w('<'),re.I)
EVIL_CSS=[EVIL,re.compile(r'\\+[\n\r]+'),re.compile(r'[\x00-\x08\x0B\x0C\x0E-\x1F]+'),re.compile(r'&#'),COMMENTS,IMPORTS]
SPECIAL=re.compile(r'''((?>content: ?['"].*?['"]))|\\\w''')
FIX=re.compile(r'''(content: ?['"]\\)\\.?(\w{4}['"])''')
DATA=re.compile(r'(?:\b|^)(?:((?>data:(?:image/(?:svg\+xml|png|jpeg|jpg|gif)|application/octet-stream);base64,))|'+w('data:')+r'(?:\b|$))',re.I|re.M)
URL=re.compile(r'''(?<![\w+\-/])(?P<url>(?:(?:https?:)\\*/|(?:https?:)?/\\*/)(?:www\.)?(?:[^\s<\[\].,;:)(]|[.,;:)(](?!=\s|$|[<\[\] ;,]))+)''',re.I|re.M)
SUF=re.compile(r'''(?P<suffix>["'`;)]+(?:\s*!important)?)$''',re.I|re.M)
def sanitize(css):
    css=FIX.sub(r'\1\2',css)
    while True:
        new=css
        for r in EVIL_CSS: new=r.sub('',new)
        new=SPECIAL.sub(lambda m:m.group(1) or '',new)
        new=DATA.sub(lambda m:m.group(1) or '',new).strip()
        if new==css: break
        css=new
    return re.sub(';;+',';',css)
def camo(css):
    def rep(m):
        u=m.group('url');suf=''
        s=SUF.search(u)
        if s: suf=s.group('suffix');u=SUF.sub('',u)
        return 'https://camo.example/x?url='+re.sub(r'[^A-Za-z0-9._~-]',lambda c:'%%%02X'%ord(c.group()) if len(c.group().encode())==1 else ''.join('%%%02X'%b for b in c.group().encode()),u)+suf
    return URL.sub(rep,css)
for f in sys.argv[1:]:
    out=camo(sanitize(open(f,encoding='utf-8').read()))
    open(f+'.shiki','w',encoding='utf-8').write(out)
