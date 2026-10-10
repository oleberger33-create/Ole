// Rendert Bilder aus stage.html mit Chromium und schreibt sie als Video.
// node render.js <timeline.json> <fontdir> <out.mp4> [start] [end] [jpg-ordner-für-standbilder]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs'), path = require('path');
(async () => {
  const [tlPath, fontDir, outFile, a, b, stills] = process.argv.slice(2);
  const tl = JSON.parse(fs.readFileSync(tlPath, 'utf8'));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
  await page.goto('file://' + path.join(__dirname, 'stage.html'));
  const ff = (fam, file, w) => `@font-face{font-family:'${fam}';font-weight:${w};src:url(file://${fontDir}/${file})}`;
  await page.addStyleTag({ content: ff('Bagel Fat One', 'BagelFatOne-400.ttf', 400) + ff('Rethink Sans', 'RethinkSans-800.ttf', 800) + ff('Rethink Sans', 'RethinkSans-600.ttf', 600) + ff('DM Mono', 'DMMono-500.ttf', 500) + ff('DM Mono', 'DMMono-400.ttf', 400) });
  await page.evaluate(async () => { await document.fonts.load("40px 'Bagel Fat One'"); await document.fonts.load("800 40px 'Rethink Sans'"); await document.fonts.load("500 40px 'DM Mono'"); });
  const n = await page.evaluate(t => window.init(t), tl);
  if (errors.length) { console.error(errors); process.exit(1); }
  if (stills) {   // einzelne Standbilder: start/end sind Sekunden, kommagetrennt in a
    fs.mkdirSync(stills, { recursive: true });
    for (const s of a.split(',')) {
      const fr = Math.round(parseFloat(s) * tl.fps);
      await page.evaluate(i => window.render(i), fr);
      await page.screenshot({ path: path.join(stills, `t${String(s).padStart(6, '0')}.jpg`), type: 'jpeg', quality: 80 });
    }
    if (errors.length) console.error(errors);
    await browser.close();
    return;
  }
  const f0 = a ? parseInt(a) : 0, f1 = b ? Math.min(parseInt(b), n) : n;
  const fps = String(tl.fps);   // echte Bildrate aus timeline.json, keine Umrechnung
  const ff2 = spawn('ffmpeg', ['-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', fps, '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-tune', 'animation', '-pix_fmt', 'yuv420p',
    '-r', fps, '-g', String(2 * tl.fps), outFile]);
  ff2.stderr.on('data', d => process.stderr.write(d));
  const t0 = Date.now();
  for (let i = f0; i < f1; i++) {
    await page.evaluate(k => window.render(k), i);
    const buf = await page.screenshot({ type: 'jpeg', quality: 93 });
    if (!ff2.stdin.write(buf)) await new Promise(r => ff2.stdin.once('drain', r));
    if ((i - f0) % 600 === 0) console.log(`${outFile}: ${i - f0}/${f1 - f0}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
    if (errors.length) { console.error(errors); process.exit(1); }
  }
  ff2.stdin.end();
  await new Promise(r => ff2.on('close', r));
  await browser.close();
  console.log('fertig', outFile, ((Date.now() - t0) / 1000).toFixed(0) + 's');
})();
