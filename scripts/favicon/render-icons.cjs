const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const b = await chromium.launch();
  const page = await b.newPage({ viewport: { width: 600, height: 600 }, deviceScaleFactor: 1 });
  const path = require('path');
const ROOT = path.resolve(__dirname, '../..');
const P = (f) => path.join(ROOT, 'public', f);
const jobs = [
    [P('favicon.svg'), 16, 'ico/favicon-16.png'], [P('favicon.svg'), 32, 'ico/favicon-32.png'], [P('favicon.svg'), 48, 'ico/favicon-48.png'],
    [P('favicon.svg'), 192, P('icons/icon-192.png')], [P('favicon.svg'), 512, P('icons/icon-512.png')],
    [path.join(__dirname, 'icon-square.svg'), 180, P('apple-touch-icon.png')], [path.join(__dirname, 'icon-square.svg'), 512, P('icons/icon-512-maskable.png')],
  ];
  fs.mkdirSync(path.join(__dirname, 'ico'), { recursive: true });
  process.chdir(__dirname);
  for (const [src, size, out] of jobs) {
    const svg = fs.readFileSync(src, 'utf8');
    await page.setContent(`<html><body style="margin:0;background:transparent"><img id="i" src="data:image/svg+xml;utf8,${encodeURIComponent(svg)}" width="${size}" height="${size}" style="display:block"></body></html>`);
    await page.waitForTimeout(100);
    const el = await page.$('#i');
    await el.screenshot({ path: out, omitBackground: true });
  }
  await b.close();
  console.log('rendered', jobs.length);
})();
