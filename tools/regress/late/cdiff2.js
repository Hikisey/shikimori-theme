// Полная сверка вычисленных стилей двух тем на корпусе фикстур.
// node cdiff2.js A.css B.css outdir fixtures...   (env: JOBS=4, SKIPP=regex свойств, которые не сравнивать,
//   CONFIGS=список через запятую: pc1920,pc1280,rm1280,an1280,st1280,tab1024,ph390,rm390,an390,st390)
// Для каждой фикстуры грузятся две одинаковые страницы (тема A и тема B), элементы сопоставляются по порядку.
// rest: transition/animation выключены (KILL) — сравниваются итоговые значения;
// an*:  без KILL, сравниваются только свойства transition-* / animation-* (объявленные значения в покое);
// rm*:  prefers-reduced-motion: reduce, rest + anim;
// st*:  принудительные :hover/:focus/:focus-visible/:active/:focus-within (CDP CSS.forcePseudoState)
//       на элементах, подходящих под селекторы тем с этими состояниями; сравниваются предки цели и поддерево родителя.
const fs=require('fs'),path=require('path'),cp=require('child_process');
const pw=(()=>{try{return require('playwright-core')}catch(e){return require('/workspace/pw/node_modules/playwright-core')}})();
const nc=require('./netcache');
const [A,B,out,...fx]=process.argv.slice(2);
const JOBS=+(process.env.JOBS||4);
const CONFIGS=(process.env.CONFIGS||'pc1920,pc1280,rm1280,an1280,st1280,tab1024,ph390,rm390,an390,st390').split(',');
if(!process.env.WORKER){
 fs.mkdirSync(out,{recursive:true});const res=path.join(out,'results.jsonl');
 if(process.env.RESUME&&fs.existsSync(res)){const done={};for(const l of fs.readFileSync(res,'utf8').split('\n').filter(Boolean)){try{const r=JSON.parse(l);(done[r.fx]=done[r.fx]||new Set()).add(r.cfg)}catch(e){}}
  const need=CONFIGS.length;const before=fx.length;for(let i=fx.length-1;i>=0;i--){const d=done[path.basename(fx[i])];if(d&&(d.size>=need||[...d].some(c=>/^(pc|tab|ph)$/.test(c))&&d.size>=need-2))fx.splice(i,1)}
  console.log('RESUME: skip',before-fx.length,'left',fx.length)} else fs.writeFileSync(res,'');
 const slices=[...Array(JOBS)].map((_,i)=>fx.filter((_,j)=>j%JOBS===i));let left=JOBS;const t0=Date.now();
 for(let i=0;i<JOBS;i++){const ch=cp.spawn(process.execPath,[__filename,A,B,out,...slices[i]],{env:{...process.env,WORKER:String(i)},stdio:['ignore','inherit','inherit']});
  ch.on('exit',()=>{if(--left===0)summary(res,t0)})}
 return;
}
function summary(res,t0){
 const L=fs.readFileSync(res,'utf8').trim().split('\n').filter(Boolean).map(JSON.parse);
 let tot=0,err=0;const byProp={},byCfg={};
 for(const r of L){if(r.err){err++;continue}tot+=r.n;byCfg[r.cfg]=(byCfg[r.cfg]||0)+r.n;for(const [k,v] of Object.entries(r.byProp||{}))byProp[k]=(byProp[k]||0)+v}
 const s={fixtures:new Set(L.map(r=>r.fx)).size,runs:L.length,errors:err,totalDiffs:tot,byCfg,byProp:Object.fromEntries(Object.entries(byProp).sort((a,b)=>b[1]-a[1]).slice(0,40)),minutes:((Date.now()-t0)/60000).toFixed(1)};
 fs.writeFileSync(path.join(out,'summary.json'),JSON.stringify(s,null,1));console.log('SUMMARY',JSON.stringify(s));
}
const ca=fs.readFileSync(A,'utf8'),cb=fs.readFileSync(B,'utf8');
const KILL='*,*::before,*::after,*::placeholder{transition:none!important;animation:none!important;caret-color:transparent!important}';
const SK=process.env.SKIPP||'';
// селекторы с состояниями из обеих тем
function stateTargets(css){
 const o={hover:new Set(),focus:new Set(),'focus-visible':new Set(),active:new Set(),'focus-within':new Set()};
 const noC=css.replace(/\/\*[\s\S]*?\*\//g,'');
 for(const m of noC.matchAll(/([^{}@;]+)\{/g)){
  for(let sel of m[1].split(/,(?![^()]*\))/)){
   sel=sel.trim();
   for(const st of Object.keys(o)){
    const re=new RegExp(':'+st+'(?![\\w-])');const i=sel.search(re);if(i<0)continue;
    let pre=sel.slice(0,i);let rest=sel.slice(i);const cut=rest.search(/[\s>+~]/);const tail=cut<0?'':'';
    // компаунд с состоянием: всё до первого комбинатора после него
    let comp=pre+(cut<0?rest:rest.slice(0,cut));
    comp=comp.replace(/::?(before|after|placeholder|marker|selection|first-line|first-letter|-webkit-[\w-]+|-moz-[\w-]+)(\([^)]*\))?/g,'')
             .replace(/:(hover|focus-visible|focus-within|focus|active|visited|open|checked)(?![\w-])/g,'').trim();
    if(comp&&!/[>+~]$/.test(comp))o[st].add(comp);
   }
  }
 }
 return Object.fromEntries(Object.entries(o).map(([k,v])=>[k,[...v]]));
}
const ST=(()=>{const a=stateTargets(ca),b=stateTargets(cb);const o={};for(const k of Object.keys(a))o[k]=[...new Set([...a[k],...b[k]])];return o})();
const pageFns=`
window.__hash=s=>{let h1=0x811c9dc5,h2=0;for(let i=0;i<s.length;i++){const c=s.charCodeAt(i);h1=Math.imul(h1^c,16777619);h2=(h2*31+c)|0}return (h1>>>0).toString(36)+(h2>>>0).toString(36)};
window.__els=()=>window.__E||(window.__E=[...document.querySelectorAll('body, body *')]);
window.__ser=(e,pe,mode,SK)=>{const cs=getComputedStyle(e,pe);if(pe&&(pe==='::before'||pe==='::after')&&cs.content==='none')return null;
 const R=SK?new RegExp(SK):null;const s=[];for(let i=0;i<cs.length;i++){const n=cs[i];if(n.startsWith('--sg-p')||(R&&R.test(n)))continue;
  if(mode==='anim'&&!/^(transition|animation)/.test(n))continue;s.push(n+':'+cs.getPropertyValue(n))}return s.sort().join('\\u0001')};
window.__pes=e=>{const t=e.tagName;const p=[null,'::before','::after'];if(t==='INPUT'||t==='TEXTAREA')p.push('::placeholder');if(t==='LI'||t==='SUMMARY')p.push('::marker');return p};
window.__settle=()=>{for(const a of document.getAnimations()){try{const t=a.effect&&a.effect.getComputedTiming();if(t&&isFinite(t.endTime)&&!(a.timeline&&a.timeline.constructor.name!=='DocumentTimeline'))a.finish();else{a.pause();a.currentTime=0}}catch(e){try{a.pause();a.currentTime=0}catch(_){}}}};
window.__snap=(idx,mode,SK)=>{__settle();const E=__els();const o=[];for(const i of idx){const e=E[i];for(const pe of __pes(e)){const v=__ser(e,pe,mode,SK);o.push(v===null?'-':__hash(v))}}return o};
window.__detail=(i,pe,mode,SK)=>__ser(__els()[i],pe,mode,SK);
window.__keys=idx=>{const E=__els();const o=[];for(const i of idx){const e=E[i];for(const pe of __pes(e))o.push([i,pe])}return o};
window.__desc=i=>{const e=__els()[i];let s=e.tagName.toLowerCase();if(e.id)s+='#'+e.id;if(e.classList.length)s+='.'+[...e.classList].slice(0,3).join('.');const p=e.parentElement;return (p?(p.classList[0]?'.'+p.classList[0]:p.tagName.toLowerCase())+' > ':'')+s};
`;
async function load(ctx,html,css){const p=await ctx.newPage();await nc(p,{block:['image','font','media']});
 await p.addInitScript(pageFns);
 await p.setContent(html.replace('<!--THEME-->','<style id="tt">'+css.replace(/<\/style/gi,'')+'</style><style id="kk">'+KILL+'</style>'),{waitUntil:'load',timeout:90000}).catch(()=>{});
 await p.evaluate(pageFns);await p.evaluate(()=>{document.body&&document.body.offsetHeight});return p}
async function setKill(p,on){await p.evaluate(([on,K])=>{document.getElementById('kk').textContent=on?K:'';document.body.offsetHeight},[on,KILL]).catch(()=>{});}
async function compare(pa,pb,idx,mode){
 let [ha,hb]=await Promise.all([pa.evaluate(([i,m,s])=>__snap(i,m,s),[idx,mode,SK]),pb.evaluate(([i,m,s])=>__snap(i,m,s),[idx,mode,SK])]);
 if(ha.some((v,k)=>v!==hb[k])){await new Promise(r=>setTimeout(r,150));[ha,hb]=await Promise.all([pa.evaluate(([i,m,s])=>__snap(i,m,s),[idx,mode,SK]),pb.evaluate(([i,m,s])=>__snap(i,m,s),[idx,mode,SK])]);}
 const keys=await pa.evaluate(i=>__keys(i),idx);const diffs=[];let n=0;const byProp={};
 if(ha.length!==hb.length)return {n:1,diffs:[['LENGTH MISMATCH',ha.length,hb.length]],byProp};
 for(let k=0;k<ha.length;k++){if(ha[k]===hb[k])continue;n++;
  if(diffs.length<25){const [i,pe]=keys[k];const [da,db]=await Promise.all([pa.evaluate(([i,pe,m,s])=>__detail(i,pe,m,s),[i,pe,mode,SK]),pb.evaluate(([i,pe,m,s])=>__detail(i,pe,m,s),[i,pe,mode,SK])]);
   const x=new Map((da||'').split('\u0001').map(t=>[t.split(':')[0],t.slice(t.indexOf(':')+1)])),y=new Map((db||'').split('\u0001').map(t=>[t.split(':')[0],t.slice(t.indexOf(':')+1)]));
   const props=[];if(!da||!db)props.push(['(pseudo exists)',!!da,!!db]);else for(const kk of new Set([...x.keys(),...y.keys()]))if(x.get(kk)!==y.get(kk)){props.push([kk,(x.get(kk)||'').slice(0,70),(y.get(kk)||'').slice(0,70)]);byProp[kk]=(byProp[kk]||0)+1}
   if(!props.length){n--;continue}
   diffs.push([await pa.evaluate(i=>__desc(i),i)+(pe||''),props.slice(0,8)])}}
 return {n,diffs,byProp};
}
const DEV={pc:{viewport:{width:1280,height:900}},tab:{viewport:{width:1024,height:768},isMobile:true,hasTouch:true,deviceScaleFactor:1},ph:{viewport:{width:390,height:844},isMobile:true,hasTouch:true,deviceScaleFactor:1}};
(async()=>{
 const b=await pw.chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
 const res=fs.createWriteStream(path.join(out,'results.jsonl'),{flags:'a'});
 const emit=(o)=>res.write(JSON.stringify(o)+'\n');
 for(const f of fx){
  const html=fs.readFileSync(f,'utf8');const name=path.basename(f);
  for(const dev of ['pc','tab','ph']){
   const cfgs=CONFIGS.filter(c=>c.startsWith(dev)||(dev==='pc'&&/^(rm|an|st)1280$/.test(c))||(dev==='ph'&&/^(rm|an|st)390$/.test(c)));
   if(!cfgs.length)continue;
   let ctx;try{
   ctx=await b.newContext(DEV[dev]);
   const [pa,pb]=await Promise.all([load(ctx,html,ca),load(ctx,html,cb)]);
   const N=await pa.evaluate(()=>__els().length),NB=await pb.evaluate(()=>__els().length);
   if(N!==NB){emit({fx:name,cfg:dev,err:'element count '+N+' vs '+NB});await ctx.close();continue}
   const all=[...Array(N).keys()];
   for(const cfg of cfgs){
    const w=+cfg.replace(/\D/g,'');
    for(const p of [pa,pb]){await p.setViewportSize({width:w,height:dev==='ph'?844:dev==='tab'?768:900});await p.emulateMedia({reducedMotion:cfg.startsWith('rm')?'reduce':'no-preference'})}
    if(cfg.startsWith('st')){
     await setKill(pa,true);await setKill(pb,true);
     const tg=await pa.evaluate(ST=>{const E=__els();const pos=new Map(E.map((e,i)=>[e,i]));const o=[];
       for(const [st,sels] of Object.entries(ST)){const seen=new Set();let cnt=0;
        for(const s of sels){let m;try{m=document.querySelectorAll(s)}catch(e){continue}let k=0;
         for(const e of m){if(!pos.has(e)||seen.has(e))continue;seen.add(e);o.push([st,pos.get(e)]);if(++k>=2)break}
         if(++cnt>4000)break}}
       return o},ST);
     // ограничим: не больше 140 целей на состояние
     const per={};const T=tg.filter(([st])=>(per[st]=(per[st]||0)+1)<=140);
     const [sa,sb]=await Promise.all([pa.context().newCDPSession(pa),pb.context().newCDPSession(pb)]);
     const ids={};for(const [s,p] of [[sa,pa],[sb,pb]]){await s.send('DOM.enable');await s.send('CSS.enable');
       await p.evaluate(T=>{const E=__els();for(const [,i] of T)E[i].setAttribute('data-hz',i)},T);
       const doc=await s.send('DOM.getDocument',{depth:0});const r=await s.send('DOM.querySelectorAll',{nodeId:doc.root.nodeId,selector:'[data-hz]'});
       const order=await p.evaluate(()=>[...document.querySelectorAll('[data-hz]')].map(e=>+e.getAttribute('data-hz')));
       ids[s===sa?'a':'b']=new Map(order.map((hz,k)=>[hz,r.nodeIds[k]]));}
     let n=0;const diffs=[];const byProp={};
     for(const [st,i] of T){
      const region=await pa.evaluate(i=>{const E=__els();const pos=new Map(E.map((e,k)=>[e,k]));const e=E[i];const o=new Set();let a=e;while(a&&a!==document.documentElement){if(pos.has(a))o.add(pos.get(a));a=a.parentElement}
        const par=e.parentElement||e;let c=0;for(const d of [par,...par.querySelectorAll('*')]){if(pos.has(d)){o.add(pos.get(d));if(++c>500)break}}return [...o].sort((x,y)=>x-y)},i);
      await Promise.all([sa.send('CSS.forcePseudoState',{nodeId:ids.a.get(i),forcedPseudoClasses:[st]}),sb.send('CSS.forcePseudoState',{nodeId:ids.b.get(i),forcedPseudoClasses:[st]})]);
      const r=await compare(pa,pb,region,'all');
      await Promise.all([sa.send('CSS.forcePseudoState',{nodeId:ids.a.get(i),forcedPseudoClasses:[]}),sb.send('CSS.forcePseudoState',{nodeId:ids.b.get(i),forcedPseudoClasses:[]})]);
      if(r.n){n+=r.n;for(const [k,v] of Object.entries(r.byProp))byProp[k]=(byProp[k]||0)+v;if(diffs.length<30)diffs.push([':'+st+' on '+(await pa.evaluate(i=>__desc(i),i)),r.diffs.slice(0,6)])}
     }
     await pa.evaluate(()=>document.querySelectorAll('[data-hz]').forEach(e=>e.removeAttribute('data-hz')));await pb.evaluate(()=>document.querySelectorAll('[data-hz]').forEach(e=>e.removeAttribute('data-hz')));
     emit({fx:name,cfg,targets:T.length,n,diffs,byProp});
    } else {
     const anim=cfg.startsWith('an');await setKill(pa,!anim);await setKill(pb,!anim);
     const r=await compare(pa,pb,all,anim?'anim':'all');
     let n=r.n,diffs=r.diffs,byProp=r.byProp;
     if(cfg.startsWith('rm')){await setKill(pa,false);await setKill(pb,false);const r2=await compare(pa,pb,all,'anim');n+=r2.n;diffs=diffs.concat(r2.diffs);for(const [k,v] of Object.entries(r2.byProp))byProp[k]=(byProp[k]||0)+v}
     emit({fx:name,cfg,els:N,n,diffs,byProp});
    }
   }
   }catch(e){emit({fx:name,cfg:dev,err:String(e.message||e).slice(0,200)})}
   if(ctx)await ctx.close().catch(()=>{});
  }
  process.stdout.write(`[w${process.env.WORKER}] ${name}\n`);
 }
 res.end();await b.close();
})();
