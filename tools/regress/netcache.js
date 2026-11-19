const fs=require('fs'),path=require('path'),crypto=require('crypto');
const DIR=process.env.NETCACHE||require('os').tmpdir()+'/shiki_netcache';fs.mkdirSync(DIR,{recursive:true});
module.exports=async function(page,{block=[]}={}){
 await page.route('**/*',async route=>{
  const req=route.request();const url=req.url();const t=req.resourceType();
  if(t==='document'||url.startsWith('data:'))return route.continue();
  if(t==='script'||block.includes(t))return route.abort();
  const k=crypto.createHash('sha1').update(url).digest('hex');const f=path.join(DIR,k);
  if(fs.existsSync(f+'.json')){const m=JSON.parse(fs.readFileSync(f+'.json'));if(m.fail)return route.abort();return route.fulfill({status:m.status,headers:m.headers,body:fs.readFileSync(f)});}
  try{const r=await route.fetch({timeout:20000});const body=await r.body();const h=r.headers();delete h['content-encoding'];delete h['content-length'];
   fs.writeFileSync(f,body);fs.writeFileSync(f+'.json',JSON.stringify({url,status:r.status(),headers:h}));return route.fulfill({status:r.status(),headers:h,body});}
  catch(e){fs.writeFileSync(f+'.json',JSON.stringify({url,fail:1}));return route.abort();}
 });
};
