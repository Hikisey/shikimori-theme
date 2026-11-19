// node cdiff.js A.css B.css out.json [pagesGlob...]  — computed-style diff, Chromium, widths 1366/1100/390
const fs=require('fs'),path=require('path');const pw=(()=>{try{return require('playwright-core')}catch(e){return require('/workspace/pw/node_modules/playwright-core')}})();const nc=require('./netcache');
const [A,B,out,...pages]=process.argv.slice(2);
const ca=fs.readFileSync(A,'utf8'),cb=fs.readFileSync(B,'utf8');
const KILL='*,*::before,*::after{transition:none!important;animation:none!important}';
const W=(process.env.WIDTHS||'1366,390').split(',').map(Number);
(async()=>{
 const b=await pw.chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
 const res={};let total=0;
 for(const w of W){
  const ctx=await b.newContext(w<800?{viewport:{width:w,height:844},deviceScaleFactor:1,isMobile:true,hasTouch:true}:{viewport:{width:w,height:900}});
  for(const pg of pages){
   const p=await ctx.newPage();await nc(p,{block:['image','font','media']});
   const h=fs.readFileSync(pg,'utf8').replace('<!--THEME-->','<style id="tt"></style><style>'+KILL+'</style>');
   await p.setContent(h,{waitUntil:'load',timeout:60000}).catch(()=>{});
   const r=await p.evaluate(async([ca,cb])=>{
    const st=document.getElementById('tt');
    const els=[...document.querySelectorAll('body, body *')];
    const snap=()=>{const o=[];for(const e of els){for(const pe of [null,'::before','::after']){const cs=getComputedStyle(e,pe);if(pe&&cs.content==='none'){o.push(null);continue}let s=[];for(let i=0;i<cs.length;i++){const n=cs[i];if(n.startsWith('--sg-p'))continue;s.push(n+':'+cs.getPropertyValue(n))}o.push(s.sort().join('\u0001'))}}return o};
    
    st.textContent=ca;document.body.offsetHeight;const sa=snap();
    st.textContent=cb;document.body.offsetHeight;const sb=snap();
    const diffs=[];const byProp={};let n=0;
    const desc=e=>{let s=e.tagName.toLowerCase();if(e.id)s+='#'+e.id;if(e.classList.length)s+='.'+[...e.classList].slice(0,3).join('.');const p=e.parentElement;return (p?(p.className&&typeof p.className=='string'?'.'+p.className.split(' ')[0]:p.tagName.toLowerCase())+' > ':'')+s};
    for(let i=0;i<sa.length;i++){if(sa[i]===sb[i])continue;n++;const e=els[Math.floor(i/3)],pe=[null,'::before','::after'][i%3];
     const x=(sa[i]||'').split('\u0001'),y=(sb[i]||'').split('\u0001');const props=[];
     if(!sa[i]||!sb[i])props.push(['(pseudo exists)',!!sa[i],!!sb[i]]);else{const X=new Set(x),Y=new Set(y);for(const v of x)if(!Y.has(v)){const k=v.split(':')[0];const w=y.find(t=>t.startsWith(k+':'));props.push([k,v.slice(k.length+1,k.length+61),(w||'').slice(k.length+1,k.length+61)]);byProp[k]=(byProp[k]||0)+1}for(const v of y)if(!X.has(v)){const k=v.split(':')[0];if(!x.some(t=>t.startsWith(k+':'))){props.push([k,'',v.slice(0,60)]);byProp[k]=(byProp[k]||0)+1}}}
     if(diffs.length<40)diffs.push([desc(e)+(pe||''),props.slice(0,6)]);}
    return {n,els:els.length,diffs,byProp};
   },[ca,cb]);
   total+=r.n;res[path.basename(pg)+'@'+w]=r;process.stderr.write(`${path.basename(pg)}@${w}: ${r.n} diffs / ${r.els}\n`);
   await p.close();
  }
  await ctx.close();
 }
 fs.writeFileSync(out,JSON.stringify(res,null,1));console.log('TOTAL DIFFS',total);
 await b.close();
})();
