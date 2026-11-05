// Deterministic frame exporter: node render.js <outDir> <fps> <worker> <workers>
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const [out, fps = 60, wi = 0, wn = 1] = process.argv.slice(2);
  const F = 30 * +fps;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  p.on('pageerror', e => console.error('PAGEERR', e.message));
  await p.goto('file://' + path.resolve(__dirname, 'index.html') + '?render');
  await p.evaluate(() => document.fonts.ready);
  const t0 = Date.now();
  for (let f = +wi; f < F; f += +wn) {
    await p.evaluate(t => window.seek(t), f / fps);
    await p.screenshot({ path: `${out}/f${String(f).padStart(5, '0')}.png` });
    if (f % 200 < +wn) console.log(`w${wi} frame ${f}/${F} ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
  await b.close();
})();
