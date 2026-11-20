import json,sys
# шум: io_about/картинки без сети, версия в подвале, ::placeholder при фокусе
def noise(d):
    s=json.dumps(d)
    return ('1.7.' in s and 'content' in s) or ('b-image' in s and ('width' in s)) 
for l in open(sys.argv[1]+'/results.jsonl'):
    r=json.loads(l)
    if r.get('err'): print('ERR',r['fx'],r['cfg'],r['err'][:80]);continue
    if not r['n']: continue
    ds=[d for d in r['diffs'] if not noise(d)]
    if r['cfg'].startswith('st'):
        ds=[[t,[x for x in sub if not noise(x)]] for t,sub in r['diffs']]
        ds=[d for d in ds if d[1]]
    if ds: print(r['fx'],r['cfg'],r['n'],json.dumps(ds)[:300])
