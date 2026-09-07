# El Paso Law Center — elpasolawyers.org

Bilingual (EN/ES) static site for the Law Office of Robert Navar, built with Astro and served by a Cloudflare Worker (static assets + `/api/contact` lead endpoint via Resend).

## Develop
```
npm install
npm run dev          # http://localhost:4321
npm run build        # dist/
npm run content:validate
node scripts/check-site.mjs   # QA over dist/ (links, titles, hreflang, sitemap)
```

## Content
- `src/data/catalog.ts` — hubs, services, EN/ES slugs, court-appearance flag.
- `src/content/parts/<hub>/*.json` — source copy per service (EN+ES). `npm run content:merge` assembles `src/content/<hub>.json`, which the templates read.
- `src/data/pages.ts` — home/about/contact/privacy copy. `src/data/site.ts` — contact details + UI strings.

## Deploy
Push to `main` → Cloudflare Workers Builds runs `npm run build` and `npx wrangler deploy`.
Worker secret: `RESEND_API_KEY`. Var `LEAD_TO_EMAIL` (wrangler.jsonc) overrides the lead recipient; remove it at launch so leads go to help@elpasolawyers.org.
