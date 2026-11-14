// node tools/shot.js <saved.html> <style.css> <out.png> [pc|phone]
// Скриншот сохранённой страницы Шикимори с собранной темой. Скрипты страницы
// вырезаются, стили Шикимори и картинки грузятся с shikimori.io.
// playwright-core ищется обычным require (NODE_PATH) или в /tmp/csstree/node_modules.
const fs = require('fs');
let pw;
try { pw = require('playwright-core'); } catch (e) { pw = require('/tmp/csstree/node_modules/playwright-core'); }
const [page, style, out, dev = 'pc'] = process.argv.slice(2);
const chrome = ['/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser'].find(p => fs.existsSync(p));
(async () => {
  let html = fs.readFileSync(page, 'utf8')
    .replace(/<script\b[^>]*>[\s\S]*?<\/script>/g, '')
    .replace(/<style[^>]*id="custom_css"[^>]*>[\s\S]*?<\/style>/g, '');
  if (!/<base /.test(html)) html = html.replace('<head>', '<head><base href="https://shikimori.io/">');
  html = html.replace('</head>', '<style id="custom_css">' + fs.readFileSync(style, 'utf8') + '</style></head>');
  const b = await pw.chromium.launch({ executablePath: chrome, args: ['--no-sandbox'] });
  const ctx = dev === 'phone'
    ? { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true }
    : { viewport: { width: 1280, height: 900 } };
  const p = await (await b.newContext(ctx)).newPage();
  await p.setContent(html, { waitUntil: 'load', timeout: 60000 }).catch(() => {});
  await p.waitForTimeout(1500);
  await p.screenshot({ path: out, animations: 'disabled' });
  await b.close();
  console.log('скриншот:', out);
})();
