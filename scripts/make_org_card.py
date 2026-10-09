#!/usr/bin/env python3
"""
Build org-card.svg -- the terminal-window "whoami" card for the organisation:
identity up top, then what lives inside the hub. Same visual language as the
rest of the org art (dark frame, monospace, short fade/slide reveal).

    python3 scripts/make_org_card.py [out.svg]

The public-repo count is read from data/repos.json when present, else from
the public GitHub API, else falls back to a static number (never breaks).
STATIC=1 emits the frozen end-state (for local previews).
"""
import html
import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") \
    else os.path.join(HERE, "..", "profile", "org-card.svg")
STATIC = bool(os.environ.get("STATIC"))

ORG = "ACADEMIC-AND-PERSONAL-PROJECTS"

W, H = 860, 336
PAD = 28
TITLEBAR_H = 30
KEY_X = PAD
VAL_X = PAD + 116
LINE_H = 20.5

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
MUTED = "#7d8590"
INK = "#c9d1d9"
KEY = "#ffa657"      # orange keys
SECTION = "#58a6ff"  # blue section headers
GREEN = "#3fb950"
ACCENT = "#22d3ee"


def repo_count():
    path = os.path.join(HERE, "..", "data", "repos.json")
    try:
        with open(path) as f:
            repos = json.load(f)
        n = len([r for r in repos if not r.get("fork") and r.get("name") != ".github"])
        if n:
            return n
    except Exception:
        pass
    try:
        req = urllib.request.Request(
            f"https://api.github.com/orgs/{ORG}",
            headers={"Accept": "application/vnd.github+json",
                     "User-Agent": "org-readme-bot/1.0"})
        token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        with urllib.request.urlopen(req, timeout=15) as resp:
            return int(json.load(resp)["public_repos"])
    except Exception:
        pass
    return 21  # offline fallback


N = repo_count()

# content model: ("host",) | ("kv", key, value) | ("sec", title) | ("bul", text) | ("gap",)
ROWS = [
    ("host",),
    ("kv", "Now", "Hub for academic & personal engineering projects"),
    ("kv", "Focus", "Data Engineering · Machine Learning · Full-Stack"),
    ("kv", "Owner", "Khadim Mbaye — AI & Big Data student"),
    ("kv", "Based", "Dakar, Senegal"),
    ("gap",),
    ("sec", "Inside"),
    ("kv", "Repos", f"{N} public projects — coursework, zoomcamps & builds"),
    ("kv", "Code", "Python · Java · Scala · SQL · JavaScript"),
    ("gap",),
    ("sec", "Highlights"),
    ("bul", "Learning in public — from classroom theory to real builds"),
    ("bul", "Coursework, zoomcamps & personal apps — one hub"),
]


def esc(s):
    return html.escape(s)


def rise(inner, i):
    """fade + slight upward slide, staggered by row index; freezes visible."""
    if STATIC:
        return f"<g>{inner}</g>"
    delay = 0.15 + i * 0.06
    return (f'<g opacity="0" transform="translate(0,5)">{inner}'
            f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.4s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="0 5" to="0 0" '
            f'begin="{delay:.2f}s" dur="0.4s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/></g>')


parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
    '<defs>'
    f'<linearGradient id="obg" x1="0" y1="0" x2="0" y2="1">'
    f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>',
    f'<rect width="{W}" height="{H}" rx="12" fill="url(#obg)"/>',
    f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}"/>',
    f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
]
for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{PAD + i*16 - 8}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')
parts.append(f'<text x="{W/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="12" '
             f'text-anchor="middle">org@github: ~$ whoami</text>')

y = TITLEBAR_H + 30
for i, row in enumerate(ROWS):
    kind = row[0]
    if kind == "gap":
        y += LINE_H * 0.5
        continue
    if kind == "host":
        label = "org@github"
        inner = (f'<text x="{KEY_X}" y="{y:.1f}" font-size="14" font-weight="700">'
                 f'<tspan fill="{GREEN}">org</tspan><tspan fill="{MUTED}">@</tspan>'
                 f'<tspan fill="{ACCENT}">github</tspan></text>'
                 f'<line x1="{KEY_X + len(label)*9.8 + 4:.0f}" y1="{y-4:.1f}" x2="{W-PAD}" y2="{y-4:.1f}" '
                 f'stroke="{FRAME}" stroke-opacity="0.8"/>')
    elif kind == "sec":
        title = esc(row[1])
        inner = (f'<text x="{KEY_X}" y="{y:.1f}" fill="{SECTION}" font-size="12.5" font-weight="700">'
                 f'&#8212; {title}</text>'
                 f'<line x1="{KEY_X + 12 + len(row[1])*8}" y1="{y-4:.1f}" x2="{W-PAD}" y2="{y-4:.1f}" '
                 f'stroke="{FRAME}" stroke-opacity="0.8"/>')
    elif kind == "kv":
        key, val = esc(row[1]), esc(row[2])
        inner = (f'<text x="{KEY_X}" y="{y:.1f}" fill="{KEY}" font-size="12.5" font-weight="700">{key}</text>'
                 f'<text x="{VAL_X}" y="{y:.1f}" fill="{INK}" font-size="12.5">{val}</text>')
    elif kind == "bul":
        txt = esc(row[1])
        inner = (f'<circle cx="{KEY_X+3}" cy="{y-4:.1f}" r="2.5" fill="{GREEN}"/>'
                 f'<text x="{KEY_X+14}" y="{y:.1f}" fill="{INK}" font-size="12.5">{txt}</text>')
    else:
        continue
    parts.append(rise(inner, i))
    y += LINE_H

parts.append("</svg>")
svg = "".join(parts)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as f:
    f.write(svg)
print("wrote", OUT, len(svg), "bytes;", W, "x", H, "|", N, "public repos")
