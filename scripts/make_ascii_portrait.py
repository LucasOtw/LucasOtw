#!/usr/bin/env python3
"""Photo -> portrait.svg: monochrome ASCII portrait in a terminal window that
prints itself row by row. Uses portrait.jpg/png at the repo root if present,
otherwise downloads your public GitHub avatar."""
import io, os, sys
import requests
from PIL import Image, ImageOps, ImageFilter
from common import ROOT, INK, esc, load, window

cfg = load("profile.json")
W, H, PAD, TOP = 560, 600, 20, 44
COLS = int(os.environ.get("COLS", 92))
ART_W, ART_H = W - 2 * PAD, H - TOP - 30
CW = ART_W / COLS
CH = CW * 1.85                      # monospace cell aspect
ROWS = int(ART_H // CH)
RAMP = " .,:;-~=+*cxo#%@"           # dark -> bright (light ink on dark bg)


def source():
    for name in ("portrait.png", "portrait.jpg", "portrait.jpeg"):
        p = os.path.join(ROOT, name)
        if os.path.exists(p):
            return Image.open(p)
    r = requests.get(f"https://github.com/{cfg['username']}.png?size=600", timeout=30)
    r.raise_for_status()
    return Image.open(io.BytesIO(r.content))


img = ImageOps.exif_transpose(source()).convert("L")
img = ImageOps.fit(img, (COLS * 10, int(ROWS * CH / CW * 10)), centering=(0.5, 0.35))
img = ImageOps.autocontrast(img, cutoff=2).filter(ImageFilter.UnsharpMask(2, 80, 2))
img = img.resize((COLS, ROWS), Image.LANCZOS)
px = img.load()
gamma = float(os.environ.get("GAMMA", 1.1))
rows = []
for y in range(ROWS):
    line = ""
    for x in range(COLS):
        v = (px[x, y] / 255) ** gamma
        line += RAMP[min(int(v * len(RAMP)), len(RAMP) - 1)]
    rows.append(line.rstrip())

out, total = [], 5.5
for i, line in enumerate(rows):
    if not line.strip():
        continue
    yy = TOP + (i + 1) * CH - CH * 0.22
    delay = i * total / ROWS
    out.append(f'<text class="r" x="{PAD}" y="{yy:.1f}" textLength="{len(line)*CW:.1f}" lengthAdjust="spacingAndGlyphs" '
               f'style="animation-delay:{delay:.2f}s" xml:space="preserve">{esc(line)}</text>')

css = f"""
  .r {{ fill:{INK}; font-size:{CH*0.95:.1f}px; clip-path:inset(0 100% 0 0); animation:type {total/ROWS*3:.2f}s steps(12) forwards; }}
  @keyframes type {{ to {{ clip-path:inset(0 0 0 0); }} }}
"""
cap = f'<text x="{PAD}" y="{H-12}" class="m" font-size="12">{cfg["prompt_user"]}@github ~ $ cat portrait.txt</text>'
svg = window(W, H, f"{cfg['prompt_user']}@github: ~ — portrait", "\n".join(out) + cap, css)
open(os.path.join(ROOT, "portrait.svg"), "w").write(svg)
print(f"portrait.svg: {COLS}x{ROWS}")
