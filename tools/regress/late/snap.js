// node snap.js urls.txt outdir   — рендерит страницу с JS сайта, сохраняет DOM как фикстуру (<!--THEME-->, без скриптов)
// строки urls.txt: name<TAB>url
const fs=require('fs'),path=require('path');const pw=require('/workspace/pw/node_modules/playwright-core');
const [list,out]=process.argv.slice(2);fs.mkdirSync(out,{recursive:true});
const items=fs.readFileSync(list,'utf8').split('\n').map(l=>l.trim()).filter(l=>l&&!l.startsWith('#')).map(l=>l.split(/\t+/));
const log=fs.createWriteStream(path.join(out,'_log.tsv'),{flags:'a'});
(async()=>{const b=await pw.chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
const ctx=await b.newContext({viewport:{width:1366,height:900},locale:'ru-RU',userAgent:'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'});
for(const [name,url] of items){const f=path.join(out,name+'.html');if(fs.existsSync(f))continue;
 const p=await ctx.newPage();let st=0,fin=url;
 try{const r=await p.goto(url,{waitUntil:'load',timeout:45000});st=r?r.status():0;fin=p.url();
  await p.waitForTimeout(2500);
  await p.evaluate(async()=>{for(let y=0;y<document.body.scrollHeight&&y<20000;y+=800){window.scrollTo(0,y);await new Promise(r=>setTimeout(r,120))}window.scrollTo(0,0)});
  await p.waitForTimeout(1500);
  let h=await p.evaluate(()=>{document.querySelectorAll('script,noscript,#custom_css,style#custom_css').forEach(e=>e.remove());return '<!DOCTYPE html>\n'+document.documentElement.outerHTML});
  const origin=new URL(fin).origin+'/';
  h=h.replace(/<head([^>]*)>/i,`<head$1><base href="${origin}">`).replace(/<\/head>/i,'<!--THEME--></head>');
  const body=(h.match(/<body[^>]*class="([^"]*)"/)||[])[1]||'';
  fs.writeFileSync(f,h);log.write([name,st,fin,body,h.length].join('\t')+'\n');console.log(st,name,fin,body.slice(0,60));
 }catch(e){log.write([name,'ERR',url,e.message.slice(0,80)].join('\t')+'\n');console.log('ERR',name,e.message.slice(0,80))}
 await p.close();await new Promise(r=>setTimeout(r,800));}
await b.close()})();
