// Usage: node stills.js out_dir t1 t2 ...
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const [out, ...ts] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  p.on('pageerror', e => console.error('PAGEERR', e.message));
  await p.goto('file://' + path.resolve(__dirname, 'index.html') + '?render');
  await p.evaluate(() => document.fonts.ready);
  for (const t of ts) {
    await p.evaluate(t => window.seek(+t), t);
    await p.screenshot({ path: `${out}/t${String(t).padStart(5, '0')}.png` });
  }
  await b.close();
})();
