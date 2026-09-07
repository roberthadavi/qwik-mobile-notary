// Usage: node scripts/merge-content.mjs <hub-id>
// Assembles src/content/<hub-id>.json from src/content/parts/<hub-id>/hub.json + <service-id>.json files.
import fs from 'node:fs';
import path from 'node:path';

const hubId = process.argv[2];
if (!hubId) { console.error('hub id required'); process.exit(1); }
const dir = path.resolve(`src/content/parts/${hubId}`);
if (!fs.existsSync(dir)) { console.error(`missing ${dir}`); process.exit(1); }
const out = { hub: null, services: {} };
for (const f of fs.readdirSync(dir).filter((f) => f.endsWith('.json')).sort()) {
  const data = JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8'));
  if (f === 'hub.json') out.hub = data;
  else out.services[f.replace(/\.json$/, '')] = data;
}
if (!out.hub) { console.error('hub.json missing'); process.exit(1); }
fs.mkdirSync(path.resolve('src/content'), { recursive: true });
fs.writeFileSync(path.resolve(`src/content/${hubId}.json`), JSON.stringify(out, null, 2));
console.log(`wrote src/content/${hubId}.json with ${Object.keys(out.services).length} services`);
