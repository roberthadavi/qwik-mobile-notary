#!/usr/bin/env python3
"""Trace the QWIK logo's Q and write public/favicon.svg + scripts/favicon/icon-square.svg.
Then run `node scripts/favicon/render-icons.cjs` and `python3 scripts/favicon/make-favicon.py --ico`."""
import re, sys, subprocess, pathlib
import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
NAVY, BLUE, WHITE = '#18304e', '#2474f5', '#ffffff'

def trace(mask, name):
    pbm = HERE / f'{name}.pbm'
    Image.fromarray(np.where(mask, 0, 255).astype('uint8')).save(pbm)
    svg = HERE / f'{name}.svg'
    subprocess.run(['potrace', '-s', '-o', str(svg), '-t', '10', '-a', '1.0', '-O', '0.2', str(pbm)], check=True)
    ds = re.findall(r'<path d="([^"]+)"', svg.read_text(), re.S)
    pbm.unlink(); svg.unlink()
    return ' '.join(' '.join(d.split()) for d in ds)

def build_svgs():
    lg = Image.open(ROOT / 'design-assets/MNE-Logo.png').convert('RGBA')
    q = lg.crop((0, 1, 125, 152))                      # the Q glyph (bowl 125x122 + tail to y=151)
    S = 8
    big = q.resize((q.width * S, q.height * S), Image.LANCZOS)
    mask = np.array(big)[:, :, 3] > 128
    cut = 122 * S
    bowl, tail = mask.copy(), mask.copy()
    bowl[cut:, :] = False
    tail[:cut, :] = False
    pb, pt = trace(bowl, 'bowl'), trace(tail, 'tail')
    box, gh = 64, 54.0
    s = gh / 1208.0; gw = 1000 * s; tx = (box - gw) / 2; ty = (box - gh) / 2
    def icon(rx):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {box} {box}" width="{box}" height="{box}">'
                f'<rect width="{box}" height="{box}" rx="{rx}" fill="{NAVY}"/>'
                f'<g transform="translate({tx:.3f},{ty:.3f}) scale({s:.6f}) translate(0,1208) scale(0.1,-0.1)">'
                f'<path fill="{WHITE}" d="{pb}"/><path fill="{BLUE}" d="{pt}"/></g></svg>\n')
    (ROOT / 'public/favicon.svg').write_text(icon(12))
    (HERE / 'icon-square.svg').write_text(icon(0))
    print('wrote public/favicon.svg and scripts/favicon/icon-square.svg')

def build_ico():
    f48, f32, f16 = [Image.open(HERE / f'ico/favicon-{s}.png').convert('RGBA') for s in (48, 32, 16)]
    f48.save(ROOT / 'public/favicon.ico', format='ICO', sizes=[(48, 48), (32, 32), (16, 16)], append_images=[f32, f16])
    print('wrote public/favicon.ico (16/32/48)')

if __name__ == '__main__':
    build_ico() if '--ico' in sys.argv else build_svgs()
