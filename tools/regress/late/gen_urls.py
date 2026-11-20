import re,random
random.seed(7)
out=[]
def pick(links,rx,n):
    c=[l for l in links if re.match(rx,l)]
    random.shuffle(c);return c[:n]
for s in ['io','rip']:
    L=[l.strip() for l in open(f'/tmp/links_{s}.txt')]
    base=f'https://shikimori.{s}'
    cur=['/','/animes','/animes/kind/tv','/animes/kind/movie/status/released','/animes/status/ongoing','/animes/genre/1-Action','/animes/season/2025','/animes/order-by/popularity','/animes/score/8','/mangas','/mangas/kind/manhwa','/ranobe','/ongoings','/animes/studio/2-Kyoto-Animation','/animes/1','/animes/1/franchise','/animes/1/screenshots','/animes/1/videos','/animes/1/similar','/animes/1/related','/animes/1/reviews','/animes/1/critiques','/animes/1/characters','/animes/1/staff','/animes/1/clubs','/animes/1/collections','/animes/1/stats','/animes/1/art','/animes/1/coub','/animes/1/files','/animes/1/cosplay','/animes/1/favoured','/animes/1/chronology','/animes/21','/animes/5114','/animes/5114/franchise','/animes/38000','/animes/52991','/mangas/2','/mangas/2/franchise','/mangas/2/characters','/mangas/2/reviews','/mangas/13','/ranobe/9115','/characters/1','/characters/1/seyu','/characters/1/animes','/characters/1/art','/characters/40','/people/1','/people/1/works','/people/1/roles','/people/1870','/clubs','/clubs/1','/clubs/1/members','/clubs/1/images','/clubs/1/animes','/clubs/1/mangas','/clubs/1/characters','/clubs/1/collections','/clubs/1/clubs','/forum','/forum/animanga','/forum/site','/forum/offtopic','/forum/clubs','/forum/news','/forum/reviews','/forum/critiques','/forum/collections','/forum/articles','/forum/contests','/forum/cosplay','/forum/games','/forum/vn','/forum/changelogs','/critiques','/collections','/articles','/morr','/morr/friends','/morr/clubs','/morr/favorites','/morr/history','/morr/achievements','/morr/reviews','/morr/critiques','/morr/comments','/morr/topics','/morr/collections','/morr/list/anime','/morr/list/manga','/morr/list/anime/mylist/watching','/morr/list/anime/mylist/completed/order-by/rate','/morr/list_export','/morr/feed','/morr/summaries','/users','/users?search=ann','/users/similar/anime','/contests','/achievements','/achievements/franchise','/achievements/author','/achievements/franchise/naruto','/about','/terms','/sitemap','/bb_codes','/tests','/tests/reset_styles_cache','/recommendations','/tierlists','/this-page-does-not-exist-404','/animes/999999999','/comments/smileys']
    if s=='rip': cur+=['/useful','/visual_novels','/forum/vn','/media/new']
    cur+=pick(L,r'^/forum/topics/\d+$|^/forum/(news|site|animanga|offtopic|clubs|collections|critiques|reviews)/[^/]+/?\d*$',8)
    cur+=pick(L,r'^/clubs/\d+[^/]*$',4)+pick(L,r'^/collections/\d+[^/]*$',3)+pick(L,r'^/articles/\d+[^/]*$',3)+pick(L,r'^/contests/\d+[^/]*$',3)
    cur+=pick(L,r'^/animes/z?\d+[^/]*$',8)+pick(L,r'^/mangas/z?\d+[^/]*$',4)+pick(L,r'^/ranobe/z?\d+[^/]*$',3)+pick(L,r'^/characters/\d+[^/]*$',3)+pick(L,r'^/people/\d+[^/]*$',3)
    cur+=pick(L,r'^/animes/\d+[^/]*/reviews/\d+$',2)+pick(L,r'^/achievements/author/\w+$',2)
    users=[l for l in L if re.match(r'^/[A-Za-z0-9_.-]+$',l) and l.strip('/') not in ('animes','mangas','ranobe','forum','clubs','users','collections','articles','contests','ongoings','terms','sitemap','recommendations','tierlists','useful','visual_novels','critiques','achievements','bb_codes','morr','morra','favicon.ico','search.xml') and '.' not in l[1:]]
    random.shuffle(users)
    for u in users[:4]: cur+=[u,u+'/list/anime',u+'/history']
    seen=set()
    for p in cur:
        if p in seen: continue
        seen.add(p)
        name=s+'_c_'+(re.sub(r'[^a-z0-9]+','_',p.lower()).strip('_') or 'home')[:60]
        out.append(f'{name}\t{base}{p}')
open('urls.txt','w').write('\n'.join(out)+'\n');print(len(out))
