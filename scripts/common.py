"""Shared palette / helpers for the profile SVGs."""
import html, json, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
BG, BG2, FRAME = "#0d1117", "#161b22", "#30363d"
INK, MUTED, ACCENT = "#c9d1d9", "#7d8590", "#39d353"
GREENS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"


def esc(s):
    return html.escape(str(s), quote=True)


def load(name):
    return json.load(open(os.path.join(ROOT, name)))


def window(w, h, title, body, extra_css=""):
    """Wrap content in a dark terminal window (title bar + traffic lights)."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{MONO}">
<style>
  .t {{ fill:{INK}; font-size:15px; }}
  .m {{ fill:{MUTED}; }}
  .a {{ fill:{ACCENT}; font-weight:700; }}
  .ln {{ opacity:0; animation:show .01s linear forwards; }}
  @keyframes show {{ to {{ opacity:1; }} }}
  {extra_css}
  @media (prefers-reduced-motion: reduce) {{ * {{ animation:none !important; opacity:1 !important; clip-path:none !important; }} .cov {{ display:none; }} }}
</style>
<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="10" fill="{BG}" stroke="{FRAME}"/>
<path d="M.5 10.5a10 10 0 0 1 10-10h{w-21}a10 10 0 0 1 10 10V32H.5z" fill="{BG2}"/>
<line x1="0" y1="32" x2="{w}" y2="32" stroke="{FRAME}"/>
<circle cx="20" cy="16" r="6" fill="#ff5f57"/><circle cx="40" cy="16" r="6" fill="#febc2e"/><circle cx="60" cy="16" r="6" fill="#28c840"/>
<text x="{w/2}" y="21" text-anchor="middle" class="m" font-size="13">{esc(title)}</text>
{body}
</svg>'''
