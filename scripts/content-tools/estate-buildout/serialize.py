"""House-format JSON writer for src/content/parts/<hub>/<service>.json.

Mirrors the formatting of the hand-written part files (2-space indent, compact
one-line {en, es} objects inside `documents`, `bring` and `process[].title`,
compact `related`, raw UTF-8) so diffs stay readable.
"""
import json
import re


def enc(s: str) -> str:
    # the hand-written part files use straight apostrophes
    return json.dumps(s.replace('’', "'"), ensure_ascii=False)


def L(o, ind: str) -> str:
    return '{\n' + ind + '  "en": ' + enc(o['en']) + ',\n' + ind + '  "es": ' + enc(o['es']) + '\n' + ind + '}'


def Lc(o) -> str:
    return '{ "en": ' + enc(o['en']) + ', "es": ' + enc(o['es']) + ' }'


def service_json(d: dict) -> str:
    out = ['{']
    for k in ('title', 'metaDescription', 'eyebrow', 'h1', 'summary', 'feeModel', 'timeline'):
        out.append(f'  "{k}": ' + L(d[k], '  ') + ',')
    out.append('  "intro": [')
    out.append(',\n'.join('    ' + L(p, '    ') for p in d['intro']))
    out.append('  ],')
    out.append('  "sections": [')
    secs = []
    for s in d['sections']:
        body = ',\n'.join('        ' + L(p, '        ') for p in s['body'])
        secs.append('    {\n      "heading": ' + L(s['heading'], '      ') + ',\n      "body": [\n' + body + '\n      ]\n    }')
    out.append(',\n'.join(secs))
    out.append('  ],')
    out.append('  "documents": [')
    out.append(',\n'.join('    ' + Lc(x) for x in d['documents']))
    out.append('  ],')
    out.append('  "bring": [')
    out.append(',\n'.join('    ' + Lc(x) for x in d['bring']))
    out.append('  ],')
    out.append('  "process": [')
    steps = []
    for st in d['process']:
        steps.append('    {\n      "title": ' + Lc(st['title']) + ',\n      "body": ' + L(st['body'], '      ') + '\n    }')
    out.append(',\n'.join(steps))
    out.append('  ],')
    out.append('  "faqs": [')
    faqs = []
    for f in d['faqs']:
        faqs.append('    {\n      "q": ' + L(f['q'], '      ') + ',\n      "a": ' + L(f['a'], '      ') + '\n    }')
    out.append(',\n'.join(faqs))
    out.append('  ],')
    out.append('  "keywords": [')
    out.append(',\n'.join('    ' + enc(k) for k in d['keywords']))
    out.append('  ],')
    out.append('  "related": [' + ', '.join(enc(r) for r in d['related']) + '],')
    out.append('  "outbound": [')
    obs = []
    for o in d['outbound']:
        obs.append('    {\n      "label": ' + L(o['label'], '      ') + ',\n      "url": ' + enc(o['url']) + '\n    }')
    out.append(',\n'.join(obs))
    out.append('  ]')
    out.append('}')
    return '\n'.join(out) + '\n'


def words(s: str) -> int:
    return len(re.findall(r"\S+", s))


def report(d: dict, name: str) -> list[str]:
    """Spec checks the validator does not do (word counts) plus the length caps."""
    msgs = []
    caps = {'title': 60, 'metaDescription': 155, 'h1': 90}
    for k, cap in caps.items():
        en, es = len(d[k]['en']), len(d[k]['es'])
        flag = '' if en <= cap and es <= cap + 10 else '  <-- OVER'
        msgs.append(f'{name}.{k}: en {en}/{cap} es {es}/{cap + 10}{flag}')
    for i, p in enumerate(d['intro']):
        for lang in ('en', 'es'):
            w = words(p[lang])
            flag = '' if 70 <= w <= 120 else '  <-- intro words out of 70-120'
            msgs.append(f'{name}.intro[{i}].{lang}: {w} words{flag}')
    for i, s in enumerate(d['sections']):
        for j, p in enumerate(s['body']):
            w = words(p['en'])
            flag = '' if 55 <= w <= 110 else '  <-- section words out of ~60-100'
            msgs.append(f'{name}.sections[{i}].body[{j}].en: {w} words{flag}')
    for i, st in enumerate(d['process']):
        w = words(st['body']['en'])
        flag = '' if 22 <= w <= 50 else '  <-- step words out of 25-45'
        msgs.append(f'{name}.process[{i}].en: {w} words{flag}')
    for i, f in enumerate(d['faqs']):
        w = words(f['a']['en'])
        flag = '' if 38 <= w <= 85 else '  <-- faq words out of 40-80'
        msgs.append(f'{name}.faqs[{i}].en: {w} words{flag}')
    blob = json.dumps(d, ensure_ascii=False)
    msgs.append(f'{name}: "El Paso" x{blob.count("El Paso")}; "$" x{blob.count("$")}; notario? {bool(re.search(r"notarios?|notar[ií]as?\\b", blob, re.I))}; brackets? {"[" in blob}')
    return msgs
