// Cloudflare Worker for QWIK Mobile Notary Public (mobilepublicnotaryelpaso.com)
// - Serves the static Astro build (assets binding, run_worker_first only for /api/*)
// - POST /api/contact → emails the lead via Resend

export interface Env {
  ASSETS: { fetch: (req: Request) => Promise<Response> };
  RESEND_API_KEY?: string;
  LEAD_TO_EMAIL?: string;   // override recipient (default qwikmobilenotary@gmail.com)
  LEAD_FROM_EMAIL?: string; // must be on a Resend-verified domain
}

const DEFAULT_TO = 'qwikmobilenotary@gmail.com';
const DEFAULT_FROM = 'QWIK Mobile Notary Website <noreply@mobilepublicnotaryelpaso.com>';

const esc = (s: string) => s.replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]!));

async function handleContact(req: Request, env: Env): Promise<Response> {
  if (req.method !== 'POST') return new Response('Method Not Allowed', { status: 405 });
  let data: FormData;
  try { data = await req.formData(); } catch { return json({ ok: false, error: 'bad_form' }, 400); }
  const get = (k: string) => String(data.get(k) ?? '').trim().slice(0, 2000);

  if (get('website')) return json({ ok: true }); // honeypot — pretend success
  const name = get('name'), phone = get('phone'), email = get('email'), matter = get('matter'), message = get('message');
  const lang = get('lang') || 'en', page = get('page');
  if (!name || !phone || !message) return json({ ok: false, error: 'missing_fields' }, 400);
  if (!env.RESEND_API_KEY) return json({ ok: false, error: 'not_configured' }, 500);

  const to = env.LEAD_TO_EMAIL || DEFAULT_TO;
  const from = env.LEAD_FROM_EMAIL || DEFAULT_FROM;
  const ip = req.headers.get('cf-connecting-ip') ?? '';
  const subject = `Notary request: ${matter || 'General'} — ${name}`;
  const rows: [string, string][] = [['Name', name], ['Phone', phone], ['Email', email || '—'], ['Document / service', matter || '—'], ['Language', lang], ['Page', page], ['IP', ip], ['Received', new Date().toISOString()]];
  const html = `<div style="font-family:Inter,Arial,sans-serif;font-size:15px;color:#111"><h2 style="margin:0 0 12px">New appointment request — QWIK Mobile Notary</h2><table cellpadding="6" style="border-collapse:collapse">${rows.map(([k, v]) => `<tr><td style="color:#666;padding-right:14px"><b>${k}</b></td><td>${esc(v)}</td></tr>`).join('')}</table><h3 style="margin:18px 0 6px">Message</h3><p style="white-space:pre-wrap;background:#f6f6f6;padding:12px;border-radius:6px">${esc(message)}</p></div>`;
  const text = rows.map(([k, v]) => `${k}: ${v}`).join('\n') + `\n\nMessage:\n${message}`;

  const r = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { Authorization: `Bearer ${env.RESEND_API_KEY}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ from, to: [to], reply_to: email || undefined, subject, html, text }),
  });
  if (!r.ok) {
    const body = await r.text();
    console.error('Resend error', r.status, body);
    return json({ ok: false, error: 'send_failed' }, 502);
  }
  return json({ ok: true });
}

function json(obj: unknown, status = 200) {
  return new Response(JSON.stringify(obj), { status, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' } });
}

export default {
  async fetch(req: Request, env: Env): Promise<Response> {
    const url = new URL(req.url);
    if (url.pathname === '/api/contact') return handleContact(req, env);
    if (url.pathname.startsWith('/api/')) return new Response('Not found', { status: 404 });
    return env.ASSETS.fetch(req);
  },
};
