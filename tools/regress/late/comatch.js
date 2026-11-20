// node comatch.js pairs.json out.json  — для каждой пары селекторов: сколько элементов матчат оба (по всему корпусу)
const {chromium}=require('/workspace/pw/node_modules/playwright');const fs=require('fs');const path=require('path');
const pairs=JSON.parse(fs.readFileSync(process.argv[2]));const out=process.argv[3];
const files=[...fs.readdirSync('pages').filter(f=>f.endsWith('.html')).map(f=>'pages/'+f),...fs.readdirSync('corpus').filter(f=>f.endsWith('.html')).map(f=>'corpus/'+f)];
function san(s){return s.replace(/::?(before|after|placeholder|marker|selection|first-line|first-letter|backdrop|-webkit-[\w-]+|-moz-[\w-]+)(\([^)]*\))?/g,'').replace(/:(hover|focus|focus-visible|focus-within|active|visited|target|checked|indeterminate|placeholder-shown|autofill|-webkit-autofill)\b(?!-)/g,'').trim()||'*'}
(async()=>{
 const sels=[...new Set(pairs.flat())];const S=sels.map(san);
 const res=pairs.map(()=>({co:0,a:0,b:0,pages:[]}));const cnt=new Map();
 const b=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});const ctx=await b.newContext({javaScriptEnabled:false});const p=await ctx.newPage();
 for(const f of files){
  let h=fs.readFileSync(f,'utf8').replace(/<script[\s\S]*?<\/script>/gi,'').replace(/<link[^>]*>/gi,'').replace(/<img/gi,'<x-img').replace(/<iframe[\s\S]*?<\/iframe>/gi,'');
  // img->x-img ломает теги img в селекторах; вернём: используем атрибут src отключение
  h=h.replace(/<x-img/gi,'<img data-x').replace(/\ssrc=/gi,' data-src=').replace(/\ssrcset=/gi,' data-srcset=');
  await p.setContent(h,{waitUntil:'domcontentloaded'});
  const r=await p.evaluate(([S,pairs,sels])=>{
    const all=[...document.querySelectorAll('*')];const id=new Map(all.map((e,i)=>[e,i]));
    const m={};S.forEach((s,i)=>{try{m[sels[i]]=new Set([...document.querySelectorAll(s)].map(e=>id.get(e)))}catch(e){m[sels[i]]=null}});
    return pairs.map(([a,b])=>{const A=m[a],B=m[b];if(!A||!B)return [-1,0,0];let c=0;for(const x of A)if(B.has(x))c++;return [c,A.size,B.size]});
  },[S,pairs,sels]);
  r.forEach((x,i)=>{const o=res[i];if(x[0]<0){o.err=1;return}o.co+=x[0];o.a+=x[1];o.b+=x[2];if(x[0]&&o.pages.length<3)o.pages.push(path.basename(f))});
  process.stdout.write('.');
 }
 fs.writeFileSync(out,JSON.stringify(pairs.map((pr,i)=>[pr[0],pr[1],res[i]])));await b.close();console.log('\ndone',files.length);
})();
