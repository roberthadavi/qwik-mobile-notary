// Static QA over dist/: broken internal links, duplicate titles, missing meta, hreflang pairs, sitemap coverage
// Pages carrying <meta name="robots" content="noindex…"> (e.g. the unlisted /photos/ staff gallery) skip the canonical/hreflang/sitemap checks.
import fs from 'node:fs'; import path from 'node:path';
const dist = path.resolve('dist');
const pages = [];
(function walk(d) { for (const f of fs.readdirSync(d)) { const p = path.join(d, f); if (fs.statSync(p).isDirectory()) walk(p); else if (f.endsWith('.html')) pages.push(p); } })(dist);
const urlOf = (p) => '/' + path.relative(dist, p).replace(/index\.html$/, '').replace(/\\/g, '/');
const exists = (u) => { const clean = u.split('#')[0].split('?')[0]; if (!clean.startsWith('/')) return true; const f = path.join(dist, clean); return fs.existsSync(f) || fs.existsSync(path.join(f, 'index.html')) || fs.existsSync(f.replace(/\/$/, '') + '.html'); };
const errs = []; const titles = new Map(); const descs = new Map(); const noindex = new Set();
let links = 0;
for (const p of pages) {
  const html = fs.readFileSync(p, 'utf8'); const u = urlOf(p);
  const unlisted = /<meta name="robots" content="noindex/.test(html); if (unlisted) noindex.add(u);
  const title = (html.match(/<title>(.*?)<\/title>/) || [])[1] || '';
  const desc = (html.match(/<meta name="description" content="(.*?)"/) || [])[1] || '';
  if (!title) errs.push(`${u}: no title`); if (!desc) errs.push(`${u}: no description`);
  if (title.length > (u.startsWith('/es/') ? 70 : 65)) errs.push(`${u}: title ${title.length} chars`);
  if (desc.length > 165) errs.push(`${u}: description ${desc.length} chars`);
  if (titles.has(title)) errs.push(`${u}: duplicate title with ${titles.get(title)}`); else titles.set(title, u);
  if (!/<h1[\s>]/.test(html)) errs.push(`${u}: no h1`);
  if ((html.match(/<h1[\s>]/g) || []).length > 1) errs.push(`${u}: multiple h1`);
  if (!unlisted && !/rel="canonical"/.test(html)) errs.push(`${u}: no canonical`);
  if (!unlisted && (!/hreflang="es"/.test(html) || !/hreflang="en"/.test(html))) errs.push(`${u}: hreflang missing`);
  for (const m of html.matchAll(/<a [^>]*href="([^"]+)"/g)) { links++; const h = m[1]; if (h.startsWith('/') && !exists(h)) errs.push(`${u}: broken link ${h}`); }
  for (const m of html.matchAll(/<img [^>]*src="([^"]+)"[^>]*>/g)) { if (m[1].startsWith('/') && !exists(m[1])) errs.push(`${u}: missing image ${m[1]}`); if (!/alt=/.test(m[0])) errs.push(`${u}: img without alt ${m[1]}`); }
  // hreflang target must exist
  for (const m of html.matchAll(/hreflang="(en|es)" href="https:\/\/mobilepublicnotaryelpaso\.com([^"]+)"/g)) if (!exists(m[2])) errs.push(`${u}: hreflang target missing ${m[2]}`);
}
const sm = fs.existsSync(path.join(dist, 'sitemap-0.xml')) ? fs.readFileSync(path.join(dist, 'sitemap-0.xml'), 'utf8') : '';
const smUrls = [...sm.matchAll(/<loc>(.*?)<\/loc>/g)].map((m) => m[1]);
console.log(`${pages.length} pages (${noindex.size} noindex), ${links} links checked, ${smUrls.length} sitemap urls`);
for (const p of pages) { const u = urlOf(p); if (u === '/404' || u === '/404.html' || noindex.has(u)) continue; if (!smUrls.includes('https://mobilepublicnotaryelpaso.com' + u)) errs.push(`sitemap missing ${u}`); }
if (errs.length) { console.error(errs.join('\n')); console.error(`${errs.length} issue(s)`); process.exit(1); } else console.log('QA OK');
