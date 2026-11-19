// node shots.js style.css outdir engine dev pages...
const fs=require('fs'),path=require('path');const pw=(()=>{try{return require('playwright-core')}catch(e){return require('/workspace/pw/node_modules/playwright-core')}})();const nc=require('./netcache');
const [css,out,engine,dev,...pages]=process.argv.slice(2);fs.mkdirSync(out,{recursive:true});
const theme=fs.readFileSync(css,'utf8');const MAXH=+(process.env.MAXH||5000);
(async()=>{
 const bt=engine==='webkit'?pw.webkit:pw.chromium;
 const b=await bt.launch(engine==='webkit'?{}:{executablePath:'/usr/bin/google-chrome',args:['--no-sandbox','--hide-scrollbars']});
 const ctx=await b.newContext(dev==='phone'?{viewport:{width:390,height:844},deviceScaleFactor:2,isMobile:engine!=='webkit'?true:undefined,hasTouch:true,userAgent:'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1'}:{viewport:{width:1366,height:900},deviceScaleFactor:1});
 for(const pg of pages){
  const p=await ctx.newPage();await nc(p,{block:['media']});
  const h=fs.readFileSync(pg,'utf8').replace('<!--THEME-->','<style id="custom_css">'+theme.replace(/<\/style/gi,'')+'</style><style>*,*::before,*::after{caret-color:transparent!important}</style>');
  await p.setContent(h,{waitUntil:'load',timeout:90000}).catch(()=>{});
  await p.evaluate(()=>document.fonts&&document.fonts.ready).catch(()=>{});
  await p.waitForTimeout(700);
  const H=await p.evaluate(()=>document.documentElement.scrollHeight);
  const name=path.basename(pg,'.html');
  await p.screenshot({path:path.join(out,`${name}.png`),clip:{x:0,y:0,width:dev==='phone'?390:1366,height:Math.min(H,MAXH)},fullPage:true,animations:'disabled'}).catch(e=>console.error(name,e.message.slice(0,100)));
  await p.close();
 }
 await b.close();
})();
