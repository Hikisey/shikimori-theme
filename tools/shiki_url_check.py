# Повторяет camo-замену Шикимори (Styles::Compile#camo_images) и ищет ссылки,
# которые «съедают» соседние символы CSS (кавычки, скобки, фигурные скобки).
import re,sys
URL=re.compile(r'''(?<![\w+\-/])(?P<url>(?:(?:https?:)\\*/|(?:https?:)?/\\*/)(?:www\.)?(?:[^\s<\[\].,;:)(]|[.,;:)(](?!=\s|$|[<\[\] ;,]))+)''',re.I|re.M)
SUF=re.compile(r'''(?P<suffix>["'`;)]+(?:\s*!important)?)$''',re.I|re.M)
bad=0
for f in sys.argv[1:]:
    s=open(f,encoding='utf-8').read()
    # комментарии Шикимори вырезает раньше
    s=re.sub(r'/\*.*?\*/\s*[\n\r]*','',s,flags=re.S)
    n=0
    for m in URL.finditer(s):
        u=SUF.sub('',m.group('url'))
        if re.search(r'''["'(){};]''',u):
            n+=1
            if n<=5: print('  BAD',f,repr(u[-60:]))
    print(f,'urls broken:',n); bad+=n
sys.exit(1 if bad else 0)
