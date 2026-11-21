"""Write the five estate-planning build-out pages (2026-11-20) into src/content/parts/estate-planning/.

Run from the repo root:  python3 scripts/content-tools/estate-buildout/build.py
Then: npm run content:merge && npm run content:validate
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from serialize import service_json, report  # noqa: E402

import p_will_signing, p_living_trust, p_todd, p_guardian, p_signing_agent  # noqa: E402

PAGES = [p_will_signing, p_living_trust, p_todd, p_guardian, p_signing_agent]
OUT = os.path.join(HERE, '..', '..', '..', 'src', 'content', 'parts', 'estate-planning')

for m in PAGES:
    path = os.path.normpath(os.path.join(OUT, f'{m.ID}.json'))
    with open(path, 'w', encoding='utf-8') as f:
        f.write(service_json(m.DATA))
    print(f'wrote {os.path.relpath(path)}')
    for line in report(m.DATA, m.ID):
        if '<--' in line or line.startswith(m.ID + ':'):
            print('   ', line)
