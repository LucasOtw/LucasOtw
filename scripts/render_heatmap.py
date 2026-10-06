#!/usr/bin/env python3
"""data/contributions.json -> contrib-heatmap.svg: the year grid pops in
column by column, then the total types out. Pure CSS animation (runs in <img>)."""
import datetime as dt, os
from common import ROOT, GREENS, INK, MUTED, MONO, load

d = load("data/contributions.json")
days = d["days"]
CELL, GAP, LEFT, TOP = 13, 3, 36, 26
STEP = CELL + GAP
weeks = (len(days) + 6) // 7
W = LEFT + weeks * STEP + 8
H = TOP + 7 * STEP + 34
REVEAL, POP = 3.2, 0.5
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()

first = dt.date.fromisoformat(days[0]["date"])
offset = (first.weekday() + 1) % 7          # GitHub rows start on Sunday
parts, last_month = [], None
for wk in range(weeks):
    m = (first + dt.timedelta(days=wk * 7 - offset + 6)).month
    if m != last_month and wk < weeks - 1:
        last_month = m
        parts.append(f'<text class="lbl" x="{LEFT + wk*STEP}" y="{TOP-9}">{MONTHS[m-1]}</text>')
for name, row in (("Mon", 1), ("Wed", 3), ("Fri", 5)):
    parts.append(f'<text class="lbl" x="0" y="{TOP + row*STEP + CELL - 2}">{name}</text>')

for i, day in enumerate(days):
    idx = i + offset
    wk, row = divmod(idx, 7)
    delay = round((wk + row * 0.5) / (weeks + 3) * REVEAL, 3)
    cls = "c hot" if day["level"] else "c"
    parts.append(f'<rect class="{cls}" x="{LEFT+wk*STEP}" y="{TOP+row*STEP}" width="{CELL}" height="{CELL}" '
                 f'rx="2.5" fill="{GREENS[day["level"]]}" style="animation-delay:{delay}s"><title>{day["date"]}: {day["count"]}</title></rect>')

caption = f'{d["total"]:,} contributions in the last year'
parts.append(f'<text class="cap" x="{LEFT}" y="{H-8}" textLength="{len(caption)*8.4:.0f}">{caption}</text>')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{MONO}">
<style>
  .lbl {{ fill:{MUTED}; font-size:12px; }}
  .cap {{ fill:{INK}; font-size:14px; font-weight:700; clip-path:inset(0 100% 0 0); animation:type 1.2s steps({len(caption)}) {REVEAL+POP}s forwards; }}
  .c {{ transform-box:fill-box; transform-origin:center; opacity:0; animation:pop {POP}s ease-out forwards; }}
  .hot {{ animation:pop {POP}s ease-out forwards, glow {POP+.3}s ease-out; }}
  @keyframes pop {{ 0% {{ opacity:0; transform:scale(.2); }} 60% {{ opacity:1; transform:scale(1.15); }} 100% {{ opacity:1; transform:scale(1); }} }}
  @keyframes glow {{ 0%,50% {{ filter:brightness(2.2); }} 100% {{ filter:brightness(1); }} }}
  @keyframes type {{ to {{ clip-path:inset(0 0 0 0); }} }}
  @media (prefers-reduced-motion: reduce) {{ .c,.cap {{ animation:none; opacity:1; clip-path:none; }} }}
</style>
{"".join(parts)}
</svg>'''
open(os.path.join(ROOT, "contrib-heatmap.svg"), "w").write(svg)
print(f"contrib-heatmap.svg: {weeks} weeks, {d['total']} contributions")
