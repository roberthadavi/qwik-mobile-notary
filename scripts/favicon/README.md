# Favicon / app icons

Brand mark = the "Q" of the QWIK logo (design-assets/MNE-Logo.png), traced to vector with potrace:
bowl in white + tail in brand blue (#2474f5) on brand navy (#18304e), rounded tile (rx 12/64).

Files served from public/: favicon.svg (any size), favicon.ico (16/32/48 — Google Search + old browsers),
apple-touch-icon.png (180, square — iOS rounds it), icons/icon-192.png, icons/icon-512.png,
icons/icon-512-maskable.png (full-bleed, glyph inside the 80% safe zone), site.webmanifest.

Rebuild: `python3 scripts/favicon/make-favicon.py` (needs potrace, Pillow, numpy) then
`node scripts/favicon/render-icons.cjs` (Playwright Chromium) — it writes straight into public/.
