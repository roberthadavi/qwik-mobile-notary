// Usage: node scripts/validate-content.mjs <hub-id> [...]
// Validates src/content/<hub-id>.json against the catalog and the content spec (CONTENT_SPEC.md).
import fs from 'node:fs';
import path from 'node:path';

const catalogSrc = fs.readFileSync(new URL('../src/data/catalog.ts', import.meta.url), 'utf8');
// crude parse: hubs are multi-line objects (`{\n    id:`), services are single-line (`{ id:`)
const hubs = [];
for (const m of catalogSrc.matchAll(/\{(\s*)id: '([a-z0-9-]+)',\s*slug: \{ en: '[^']+', es: '[^']+' \},\s*name:/g)) {
  if (m[1].includes('\n')) hubs.push({ id: m[2], services: [], isCategory: false });
  else hubs[hubs.length - 1].services.push(m[2]);
}
for (const h of hubs) {
  const block = catalogSrc.slice(catalogSrc.indexOf(`id: '${h.id}'`));
  const end = block.indexOf('services:');
  h.isCategory = /isCategory: true/.test(block.slice(0, end));
}
const allServiceIds = new Set(hubs.flatMap((h) => h.services));

const FORBIDDEN = /notarios?|notar[ií]as?\b/i; // Tex. Gov't Code §406.017 — never in any advertising copy
const isL = (v) => v && typeof v === 'object' && typeof v.en === 'string' && typeof v.es === 'string' && v.en.trim() && v.es.trim();
const errs = [];
const chk = (cond, msg) => { if (!cond) errs.push(msg); };

function checkL(v, name, max) {
  chk(isL(v), `${name}: must be {en,es} non-empty`);
  if (!isL(v)) return;
  if (max) { chk(v.en.length <= max, `${name}.en > ${max} chars (${v.en.length})`); chk(v.es.length <= max + 10, `${name}.es > ${max + 10} chars (${v.es.length})`); }
  for (const l of ['en', 'es']) {
    chk(!/\[|lorem ipsum|\bTODO\b|\[insert/.test(v[l]) || /\[Notice|\[HIPAA/.test(v[l]), `${name}.${l}: placeholder text`);
    chk(!FORBIDDEN.test(v[l]), `${name}.${l}: contains the prohibited word "notario"`);
    chk(!/[*_#`]{2}|<\/?[a-z]+>/.test(v[l]), `${name}.${l}: markdown/HTML not allowed`);
  }
}
function checkLArr(v, name, min, max) {
  chk(Array.isArray(v) && v.length >= min && v.length <= max, `${name}: need ${min}-${max} items`);
  if (Array.isArray(v)) v.forEach((x, i) => checkL(x, `${name}[${i}]`));
}
function checkFaqs(v, name, min, max) {
  chk(Array.isArray(v) && v.length >= min && v.length <= max, `${name}: need ${min}-${max} faqs`);
  if (Array.isArray(v)) v.forEach((f, i) => { checkL(f.q, `${name}[${i}].q`); checkL(f.a, `${name}[${i}].a`); });
}
function checkSections(v, name, min, max) {
  chk(Array.isArray(v) && v.length >= min && v.length <= max, `${name}: need ${min}-${max} sections`);
  if (Array.isArray(v)) v.forEach((sec, i) => { checkL(sec.heading, `${name}[${i}].heading`); checkLArr(sec.body, `${name}[${i}].body`, 1, 2); });
}
function checkProcess(v, name) {
  chk(Array.isArray(v) && v.length === 3, `${name}: need 3 steps`);
  if (Array.isArray(v)) v.forEach((st, i) => { checkL(st.title, `${name}[${i}].title`); checkL(st.body, `${name}[${i}].body`); });
}
function checkOutbound(v, name, min, max) {
  chk(Array.isArray(v) && v.length >= min && v.length <= max, `${name}: need ${min}-${max} outbound links`);
  if (Array.isArray(v)) v.forEach((o, i) => { checkL(o.label, `${name}[${i}].label`); chk(/^https:\/\//.test(o.url || ''), `${name}[${i}].url must be https`); });
}
function checkRelated(v, name) {
  chk(Array.isArray(v) && v.length >= 2 && v.length <= 4, `${name}: need 2-4 related ids`);
  if (Array.isArray(v)) v.forEach((r) => chk(allServiceIds.has(r), `${name}: unknown service id "${r}"`));
}

for (const hubId of process.argv.slice(2)) {
  const hub = hubs.find((h) => h.id === hubId);
  if (!hub) { errs.push(`unknown hub ${hubId}`); continue; }
  const file = path.resolve(`src/content/${hubId}.json`);
  let data;
  try { data = JSON.parse(fs.readFileSync(file, 'utf8')); } catch (e) { errs.push(`${hubId}: invalid JSON — ${e.message}`); continue; }
  const H = data.hub || {};
  const p = `${hubId}.hub`;
  checkL(H.title, `${p}.title`, 60); checkL(H.metaDescription, `${p}.metaDescription`, 155); checkL(H.eyebrow, `${p}.eyebrow`); checkL(H.h1, `${p}.h1`, 90); checkL(H.summary, `${p}.summary`);
  if (hub.isCategory) {
    // rich hub page (apostille, wedding officiant): full service-style content
    checkLArr(H.intro, `${p}.intro`, 3, 3); checkFaqs(H.faqs, `${p}.faqs`, 5, 6);
    checkL(H.feeModel, `${p}.feeModel`); checkL(H.timeline, `${p}.timeline`);
    checkSections(H.sections, `${p}.sections`, 2, 3); checkLArr(H.documents, `${p}.documents`, 5, 12); checkLArr(H.bring, `${p}.bring`, 3, 6);
    checkProcess(H.process, `${p}.process`); checkOutbound(H.outbound, `${p}.outbound`, 1, 3);
    chk(Array.isArray(H.keywords) && H.keywords.length >= 4, `${p}.keywords: need >=4`);
    if (H.related !== undefined) checkRelated(H.related, `${p}.related`);
  } else {
    checkLArr(H.intro, `${p}.intro`, 2, 2); checkFaqs(H.faqs, `${p}.faqs`, 3, 3);
  }
  chk((JSON.stringify(H).match(/El Paso/g) || []).length >= 3, `${p}: mention "El Paso" >= 3 times`);

  const S = data.services || {};
  for (const sid of hub.services) {
    const s = S[sid]; const q = `${hubId}.services.${sid}`;
    if (!s) { errs.push(`${q}: missing`); continue; }
    checkL(s.title, `${q}.title`, 60); checkL(s.metaDescription, `${q}.metaDescription`, 155); checkL(s.eyebrow, `${q}.eyebrow`); checkL(s.h1, `${q}.h1`, 90); checkL(s.summary, `${q}.summary`);
    checkL(s.feeModel, `${q}.feeModel`); checkL(s.timeline, `${q}.timeline`);
    checkLArr(s.intro, `${q}.intro`, 3, 3);
    checkSections(s.sections, `${q}.sections`, 2, 2);
    checkLArr(s.documents, `${q}.documents`, 5, 14);
    checkLArr(s.bring, `${q}.bring`, 3, 6);
    checkProcess(s.process, `${q}.process`);
    checkFaqs(s.faqs, `${q}.faqs`, 5, 5);
    chk(Array.isArray(s.keywords) && s.keywords.length >= 4, `${q}.keywords: need >=4`);
    checkRelated(s.related, `${q}.related`);
    if (Array.isArray(s.related)) chk(!s.related.includes(sid), `${q}.related: must not include itself`);
    checkOutbound(s.outbound, `${q}.outbound`, 1, 3);
    const blob = JSON.stringify(s);
    chk((blob.match(/El Paso/g) || []).length >= 3, `${q}: mention "El Paso" >= 3 times`);
  }
  for (const k of Object.keys(S)) chk(hub.services.includes(k), `${hubId}: unexpected service key "${k}"`);
  chk(!FORBIDDEN.test(JSON.stringify(data)), `${hubId}: the word "notario" appears somewhere in the file`);
}
if (errs.length) { console.error(errs.join('\n')); console.error(`\n${errs.length} error(s)`); process.exit(1); }
console.log('OK');
