// node affected.js sels.json fx_all.txt > fx_list : страницы, где хоть один селектор (без состояний и псевдоэлементов) что-то находит
const pw=require('/workspace/pw/node_modules/playwright-core');const fs=require('fs');
const sels=JSON.parse(fs.readFileSync(process.argv[2]));const files=fs.readFileSync(process.argv[3],'utf8').split('\n').filter(Boolean);
function san(s){return s.replace(/::?(before|after|first-line|first-letter)(?![\w-])/g,'').replace(/::[\w-]+(\([^)]*\))?/g,'').replace(/:(hover|focus|focus-visible|focus-within|active|visited|target|checked|indeterminate|placeholder-shown|autofill|-webkit-autofill|open)(?![\w-])/g,'').replace(/:-moz-[\w-]+/g,'').trim()||'*'}
(async()=>{const b=await pw.chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});const ctx=await b.newContext({javaScriptEnabled:false});const p=await ctx.newPage();
 const S=sels.map(san);const bad=new Set();
 for(const f of files){let h=fs.readFileSync(f,'utf8').replace(/<script[\s\S]*?<\/script>/gi,'').replace(/<link[^>]*>/gi,'').replace(/\ssrc=/gi,' data-src=').replace(/\ssrcset=/gi,' data-srcset=');
  await p.setContent(h,{waitUntil:'domcontentloaded'});
  const r=await p.evaluate(S=>{const hit=[];const err=[];S.forEach((s,i)=>{try{if(document.querySelector(s))hit.push(i)}catch(e){err.push(i)}});return [hit,err]},S);
  r[1].forEach(i=>bad.add(sels[i]));
  if(r[0].length||r[1].length)console.log(f);}
 if(bad.size)console.error('INVALID',[...bad]);await b.close()})();
