// Content lint — Tex. Gov't Code §406.017: a notary may not use "notario" / "notario publico" in advertising.
// Scans source copy (and dist/ when present) and fails the build if the word appears anywhere.
import fs from 'node:fs';
import path from 'node:path';

const roots = ['src', 'public'];
if (process.argv.includes('--dist')) roots.push('dist');
const exts = new Set(['.json', '.ts', '.astro', '.md', '.html', '.txt', '.xml', '.mjs', '.css']);
const hits = [];
function walk(d) {
  if (!fs.existsSync(d)) return;
  for (const f of fs.readdirSync(d)) {
    const p = path.join(d, f);
    if (fs.statSync(p).isDirectory()) { if (f !== 'node_modules') walk(p); continue; }
    if (!exts.has(path.extname(f))) continue;
    const txt = fs.readFileSync(p, 'utf8');
    txt.split('\n').forEach((line, i) => {
      if (/notarios?|notar[ií]as?\b/i.test(line) && !/lint-content|§406\.017|prohibited word|FORBIDDEN/.test(line)) hits.push(`${p}:${i + 1}: ${line.trim().slice(0, 120)}`);
    });
  }
}
for (const r of roots) walk(path.resolve(r));
if (hits.length) { console.error('Prohibited term found (Tex. Gov\'t Code §406.017):\n' + hits.join('\n')); process.exit(1); }
console.log(`lint OK — no prohibited terms in ${roots.join(', ')}`);
