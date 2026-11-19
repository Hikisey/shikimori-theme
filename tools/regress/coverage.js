// node coverage.js style.css out.json pages/*.html
// Какие селекторы темы не совпали ни на одной из сохранённых страниц (:hover, ::before и т. п. отбрасываются).
// Несовпадение ещё не значит «мёртвое»: классы от скриптов и страницы под логином надо проверять отдельно.
const fs=require('fs');const pw=(()=>{try{return require('playwright-core')}catch(e){return require('/workspace/pw/node_modules/playwright-core')}})();
const [css,out,...files]=process.argv.slice(2);
const DYN=/::?(before|after|placeholder|selection|marker|backdrop|first-letter|first-line|file-selector-button|-webkit-[\w-]+|-moz-[\w-]+|-ms-[\w-]+|scroll-button\([^)]*\)|picker\([^)]*\)|picker-icon|checkmark)/g;
const DYNC=/:(hover|focus-visible|focus-within|focus|active|visited|open|target|placeholder-shown|autofill|popover-open|user-invalid)(?![\w-])/g;
(async()=>{
 const b=await pw.chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
 const p=await b.newPage();
 await p.setContent('<style id=t></style>');
 const sels=await p.evaluate(c=>{document.getElementById('t').textContent=c;const o=[];const walk=l=>{for(const r of l){if(r.selectorText)for(const s of r.selectorText.split(/,(?![^()]*\))/))o.push(s.trim());if(r.cssRules)walk(r.cssRules)}};walk(document.getElementById('t').sheet.cssRules);return [...new Set(o)]},fs.readFileSync(css,'utf8'));
 const hit=new Array(sels.length).fill(0);
 for(const f of files){
  const h=fs.readFileSync(f,'utf8').replace(/<script\b[^>]*>[\s\S]*?<\/script>/g,'').replace(/<link[^>]*>/g,'').replace(/<img\b/g,'<imgx');
  await p.setContent(h,{waitUntil:'domcontentloaded'}).catch(()=>{});
  const r=await p.evaluate(([S,a,c])=>{const A=new RegExp(a,'g'),C=new RegExp(c,'g');return S.map(s=>{const n=s.replace(A,'').replace(C,'').replace(/:not\(\s*\)|:is\(\s*\)/g,'').trim()||'*';try{return document.querySelector(n)?1:0}catch(e){return 0}})},[sels,DYN.source,DYNC.source]);
  r.forEach((v,i)=>{if(v)hit[i]=1});
 }
 const miss=sels.filter((s,i)=>!hit[i]);
 fs.writeFileSync(out,JSON.stringify({pages:files.length,selectors:sels.length,unmatched:miss},null,1));
 console.log(`страниц ${files.length}, селекторов ${sels.length}, не совпало ${miss.length}`);
 await b.close();
})();
