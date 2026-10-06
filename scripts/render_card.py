#!/usr/bin/env python3
"""profile.json + data/contributions.json -> card.svg: a neofetch-style
info card whose lines type themselves in, followed by live GitHub stats."""
import datetime as dt, os
from common import ROOT, BG, GREENS, esc, load, window

cfg, d = load("profile.json"), load("data/contributions.json")
card = cfg["card"]
best = d["best_day"]
best_date = dt.date.fromisoformat(best["date"]).strftime("%d %b %Y")
plural = lambda n, w: f"{n} {w}{'' if n == 1 else 's'}"

W, H, X, Y0, LH, CH = 560, 600, 28, 66, 28, 9.6   # CH = monospace char width at 16px
lines = [("title", card["title"], None), ("rule", "─" * len(card["title"]), None)]
lines += [("kv", k, v) for k, v in card["info"]]
lines += [("blank", "", None), ("head", "GitHub · last 12 months", None),
          ("kv", "Contributions", f"{d['total']:,}"),
          ("kv", "Active days", str(d["active_days"])),
          ("kv", "Streak", f"{plural(d['current_streak'], 'day')} (best {plural(d['longest_streak'], 'day')})"),
          ("kv", "Best day", f"{best['count']} on {best_date}"),
          ("blank", "", None), ("palette", "", None)]

KEYW = max(len(k) for t, k, _ in lines if t == "kv") + 2
out, t, y = [], 0.3, Y0
for kind, a, b in lines:
    if kind == "blank":
        y += LH // 2
        continue
    if kind == "palette":
        sw = "".join(f'<rect x="{X + i*34}" y="{y-16}" width="28" height="18" rx="3" fill="{c}"/>'
                     for i, c in enumerate(GREENS + ["#c9d1d9", "#7d8590"]))
        out.append(f'<g class="ln" style="animation-delay:{t:.2f}s">{sw}</g>')
        break
    if kind == "kv":
        text = f'<tspan class="a">{esc(a)}</tspan><tspan class="m">:</tspan><tspan x="{X + KEYW*CH}">{esc(b)}</tspan>'
        n = KEYW + len(b)
    elif kind == "title":
        text, n = f'<tspan class="a">{esc(a)}</tspan>', len(a)
    elif kind == "head":
        text, n = f'<tspan class="m">── {esc(a)} ──</tspan>', len(a) + 6
    else:
        text, n = f'<tspan class="m">{a}</tspan>', len(a)
    dur = min(0.05 + n * 0.008, 0.35)
    out.append(f'<text class="t ln" x="{X}" y="{y}" style="animation-delay:{t:.2f}s">{text}</text>'
               f'<rect class="cov" x="{X-2}" y="{y-18}" width="{W-X}" height="24" fill="{BG}" '
               f'style="animation-delay:{t:.2f}s;animation-duration:{dur:.2f}s"/>')
    t += dur + 0.05
    y += LH

cursor_y = y + 14
out.append(f'<rect class="cur" x="{X}" y="{cursor_y}" width="10" height="18" fill="#c9d1d9" style="animation-delay:{t:.2f}s"/>')
out.append(f'<text x="{W-24}" y="{H-16}" text-anchor="end" class="m" font-size="12">updated {d["updated"]}</text>')

css = """
  .t { font-size:16px; }
  .cov { transform-box:fill-box; transform-origin:right; animation-name:wipe; animation-timing-function:steps(20); animation-fill-mode:forwards; }
  @keyframes wipe { to { transform:scaleX(0); } }
  .cur { opacity:0; animation:blink 1s step-end infinite; }
  @keyframes blink { 0%,100% { opacity:1; } 50% { opacity:0; } }
"""
svg = window(W, H, f"{cfg['prompt_user']}@github: ~ — neofetch", "\n".join(out), css)
open(os.path.join(ROOT, "card.svg"), "w").write(svg)
print("card.svg written")
