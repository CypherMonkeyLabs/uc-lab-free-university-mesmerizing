#!/usr/bin/env python3
"""Build the UC round-2 university pages, diagrams, and text exports.

Run from the repo root: python3 scripts/build_uc_round2.py
Raster PNG files are a second step: python3 scripts/render_uc_png.py
"""
from __future__ import annotations

import html
import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTACT = "https://cyphermonkeylabs.com/#contact"
WEB = "https://cyphermonkeylabs.com"
ORG = "https://github.com/CypherMonkeyLabs"
TREE = "https://linktr.ee/cypherMonkey"

RFC3261 = ("RFC 3261, SIP", "https://www.rfc-editor.org/rfc/rfc3261")
RFC3264 = ("RFC 3264, offer/answer", "https://www.rfc-editor.org/rfc/rfc3264")
RFC3262 = ("RFC 3262, PRACK", "https://www.rfc-editor.org/rfc/rfc3262")
RFC3550 = ("RFC 3550, RTP", "https://www.rfc-editor.org/rfc/rfc3550")
RFC3711 = ("RFC 3711, SRTP", "https://www.rfc-editor.org/rfc/rfc3711")
RFC4594 = ("RFC 4594, DiffServ service classes", "https://www.rfc-editor.org/rfc/rfc4594")
RFC3246 = ("RFC 3246, Expedited Forwarding", "https://www.rfc-editor.org/rfc/rfc3246")
RFC3515 = ("RFC 3515, REFER", "https://www.rfc-editor.org/rfc/rfc3515")
RFC4028 = ("RFC 4028, session timers", "https://www.rfc-editor.org/rfc/rfc4028")
CUCM = ("Cisco Unified Communications Manager product support", "https://www.cisco.com/c/en/us/support/unified-communications/unified-communications-manager-callmanager/series.html")
CUBE = ("Cisco Unified Border Element product support", "https://www.cisco.com/c/en/us/support/unified-communications/unified-border-element/series.html")
SRST = ("Cisco Unified SRST product support", "https://www.cisco.com/c/en/us/support/unified-communications/unified-survivable-remote-site-telephony/series.html")
EXP = ("Cisco Expressway Series product support", "https://www.cisco.com/c/en/us/support/unified-communications/expressway-series/series.html")
UCCE = ("Cisco Unified Contact Center Enterprise product support", "https://www.cisco.com/c/en/us/support/customer-collaboration/unified-contact-center-enterprise/series.html")
WEBEX = ("Webex Help", "https://help.webex.com/")
ITU = ("ITU-T G.114, one-way transmission time", "https://www.itu.int/rec/T-REC-G.114")
CERTS = ("Cisco training and certifications", "https://www.cisco.com/c/en/us/training-events/training-certifications.html")

TRACKS = [
    ("T1", "SIP", "Messages, dialogs, and media", "#99f6e4"),
    ("T2", "CUCM dial plan", "Partitions, patterns, and trunks", "#bfdbfe"),
    ("T3", "CUBE and SRST", "Two legs, and the phone when CUCM is gone", "#fde68a"),
    ("T4", "Expressway", "The pair that lets a remote phone register", "#fecdd3"),
    ("T5", "Voice QoS", "Marks, queues, and the delay budget", "#ddd6fe"),
    ("T6", "UCCE bridges", "From the carrier to the agent desktop", "#d9f99d"),
    ("T7", "Webex Calling migration", "Move a number and keep a rollback", "#fed7aa"),
    ("T8", "Troubleshooting", "One hypothesis, then one change", "#f5d0fe"),
]

SECTIONS = [
    ("home", "Home", "index.html", "Eight tracks. Start here if you are new."),
    ("learn", "Learn", "start.html", "Ten minutes, or the full course."),
    ("diagrams", "Diagrams", "diagrams.html", "Still drawings you can export."),
    ("flows", "Flows", "flows.html", "Ladders with a moving packet."),
    ("play", "Play", "play.html", "A short code drill in this browser."),
    ("listen", "Listen", "listen.html", "Recorded notes, then read-along."),
    ("downloads", "Downloads", "downloads.html", "Sheets, cards, templates, and one zip."),
    ("ecosystem", "Ecosystem", "ecosystem.html", "Glossary, bridges, and the systems beside CUCM."),
    ("help", "Help", "help.html", "How the menu, course, bot, and downloads work."),
]


def esc(value: str) -> str:
    return html.escape(str(value), quote=True)


def track_name(tid: str) -> str:
    for row in TRACKS:
        if row[0] == tid:
            return row[1]
    return tid


SHIELD = (
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.5 4.5 5.5v5.8c0 4.6 3.1 8.6 7.5 10.2 4.4-1.6 7.5-5.6 7.5-10.2V5.5z" '
    'fill="currentColor" opacity=".18" stroke="currentColor" stroke-width="1.6"/>'
    '<path d="M8.2 12.2 11 15l4.8-5.2" fill="none" stroke="#0f766e" stroke-width="1.8" stroke-linecap="round"/></svg>'
)
MONKEY = '''<svg viewBox="0 0 64 64" class="monkey-icon" aria-hidden="true"><defs>
<radialGradient id="mh" cx="38%" cy="30%" r="80%"><stop offset="0" stop-color="#ffd9a0"/><stop offset=".5" stop-color="#e8903a"/><stop offset="1" stop-color="#8a3f10"/></radialGradient></defs>
<circle cx="14" cy="34" r="7" fill="url(#mh)"/><circle cx="50" cy="34" r="7" fill="url(#mh)"/>
<circle cx="32" cy="32" r="18" fill="url(#mh)"/>
<ellipse cx="32" cy="38" rx="10" ry="8" fill="#fde68a"/>
<circle cx="26" cy="31" r="2" fill="#2a1406"/><circle cx="38" cy="31" r="2" fill="#2a1406"/>
<circle cx="26" cy="31" r="6" fill="#e0f2fe" opacity=".45" stroke="#fde047" stroke-width="1.6"/>
<circle cx="38" cy="31" r="6" fill="#e0f2fe" opacity=".45" stroke="#fde047" stroke-width="1.6"/>
<path d="M27 42 q5 4 10 0" fill="none" stroke="#7c2d12" stroke-width="1.6" stroke-linecap="round"/></svg>'''
GITHUB = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 .5A11.5 11.5 0 0 0 .5 12.3c0 5.22 3.38 9.65 8.07 11.22.59.12.8-.26.8-.57v-2.02c-3.28.73-3.97-1.42-3.97-1.42-.53-1.38-1.3-1.75-1.3-1.75-1.07-.75.08-.73.08-.73 1.18.08 1.8 1.24 1.8 1.24 1.05 1.84 2.76 1.31 3.43.99.1-.78.41-1.31.75-1.61-2.62-.31-5.37-1.34-5.37-5.98 0-1.32.46-2.4 1.22-3.25-.12-.3-.53-1.53.12-3.18 0 0 1-.33 3.3 1.25a11.3 11.3 0 0 1 6 0c2.3-1.58 3.3-1.25 3.3-1.25.65 1.65.24 2.88.12 3.18.76.85 1.22 1.93 1.22 3.25 0 4.65-2.76 5.66-5.39 5.96.42.38.8 1.12.8 2.26v3.35c0 .31.21.7.81.57A11.52 11.52 0 0 0 23.5 12.3 11.5 11.5 0 0 0 12 .5z"/></svg>'
LINKTREE = """<svg viewBox="0 0 64 64" aria-hidden="true"><defs><filter id="uc-tree-glow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="2.2"/></filter></defs>
<g filter="url(#uc-tree-glow)" fill="#bbf7d0"><circle cx="32" cy="10" r="7"/><rect x="29" y="14" width="6" height="12" rx="3"/><circle cx="14" cy="30" r="6.5"/><circle cx="50" cy="30" r="6.5"/><rect x="16" y="27" width="32" height="6" rx="3"/><rect x="29" y="30" width="6" height="12" rx="3"/><circle cx="12" cy="46" r="6.5"/><circle cx="52" cy="46" r="6.5"/><rect x="14" y="43" width="36" height="6" rx="3"/><rect x="27" y="46" width="10" height="14" rx="5"/></g>
<g fill="#f7fee7" stroke="#052e16" stroke-width="1.6" stroke-linejoin="round"><circle cx="32" cy="10" r="7"/><rect x="29" y="14" width="6" height="12" rx="3"/><circle cx="14" cy="30" r="6.5"/><circle cx="50" cy="30" r="6.5"/><rect x="16" y="27" width="32" height="6" rx="3"/><rect x="29" y="30" width="6" height="12" rx="3"/><circle cx="12" cy="46" r="6.5"/><circle cx="52" cy="46" r="6.5"/><rect x="14" y="43" width="36" height="6" rx="3"/><rect x="27" y="46" width="10" height="14" rx="5"/></g></svg>"""


def footer() -> str:
    icons = (
        f'<a class="brand-icon brand-web" href="{WEB}" aria-label="CypherMonkey Labs website">{MONKEY}</a>'
        f'<a class="brand-icon brand-gh" href="{ORG}" aria-label="CypherMonkey Labs on GitHub">{GITHUB}</a>'
        f'<a class="brand-icon brand-tree" href="{TREE}" aria-label="CypherMonkey on Linktree">{LINKTREE}</a>'
    )
    return (
        '<footer class="site-footer lab-footer wrap" data-canon-footer>'
        f'<aside class="disclaimer-panel" aria-labelledby="disc-title"><span class="disclaimer-ico">{SHIELD}</span><div>'
        '<h2 id="disc-title">A note from the student behind this lab</h2>'
        '<p>This is an <strong>independent, free, learning-only student project</strong>. It respects every company and vendor, and every trademark belongs to its owner. It is <strong>not affiliated with or endorsed by</strong> any of them.</p>'
        f'<p>If anyone has a concern, the content will be removed or corrected promptly via the contact form at <a href="{CONTACT}">{CONTACT}</a>. Nothing here is sold. I am happy to volunteer for any organization.</p>'
        "</div></aside>"
        '<p class="footer-brand">CypherMonkey Labs</p>'
        f'<nav class="brand-row brand-icons" aria-label="CypherMonkey Labs">{icons}</nav>'
        "<p class=\"site-copy\">© 2026 CypherMonkeyLabs 🐒</p>"
        "</footer>"
    )


def icon(path: str) -> str:
    return (
        '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" '
        f'stroke-linecap="round" stroke-linejoin="round">{path}</svg>'
    )


ICONS = {
    "home": icon('<path d="M4 10.5 12 4l8 6.5V20a1 1 0 0 1-1 1h-5v-6H10v6H5a1 1 0 0 1-1-1z"/>'),
    "learn": icon('<path d="M4 6h16v12H4z"/><path d="M8 10h8M8 14h5"/>'),
    "diagrams": icon('<rect x="4" y="5" width="16" height="14" rx="2"/><path d="m7 15 3-3 2 2 3-4"/>'),
    "flows": icon('<path d="M4 7h16M4 12h16M4 17h10"/>'),
    "play": icon('<path d="M8 5v14l11-7z"/>'),
    "listen": icon('<path d="M4 13a8 8 0 0 1 16 0"/><rect x="3" y="13" width="4" height="6" rx="1"/><rect x="17" y="13" width="4" height="6" rx="1"/>'),
    "downloads": icon('<path d="M12 4v10M8 10l4 4 4-4M5 19h14"/>'),
    "ecosystem": icon('<circle cx="12" cy="12" r="8"/><path d="M4 12h16M12 4c2 2.4 3 5 3 8s-1 5.6-3 8c-2-2.4-3-5-3-8s1-5.6 3-8z"/>'),
    "help": icon('<circle cx="12" cy="12" r="8"/><path d="M9.5 9a2.5 2.5 0 1 1 3.5 2.3c-.8.4-1 .9-1 1.7V14"/><path d="M12 17h.01"/>'),
    "menu": icon('<path d="M4 7h16M4 12h16M4 17h16"/>'),
}


def href(pre: str, path: str) -> str:
    return pre + path


def chrome(pre: str, title: str, desc: str, current: str, body: str, track: str = "") -> str:
    chips = []
    for key, label, path, blurb in SECTIONS:
        tour = f' data-tour="{key}"' if key in {"home", "learn", "diagrams", "play", "listen", "downloads"} else ""
        current_attr = ' aria-current="page"' if key == current else ""
        chips.append(
            f'<a class="section-chip" href="{href(pre, path)}"{tour}{current_attr} title="{esc(blurb)}">'
            f'<span class="chip-ico">{ICONS[key]}</span><span>{esc(label)}</span></a>'
        )
    rows = []
    for key, label, path, blurb in SECTIONS:
        rows.append(
            "<li><a data-menu-text=\"" + esc((label + " " + blurb).lower()) + f'" href="{href(pre, path)}">'
            f'<span class="ico">{ICONS[key]}</span><span><strong>{esc(label)}</strong>'
            f'<span class="desc">{esc(blurb)}</span></span></a></li>'
        )
    for tid, name, blurb, _color in TRACKS:
        rows.append(
            "<li><a data-menu-text=\"" + esc((name + " " + blurb).lower()) + f'" href="{href(pre, "tracks/" + tid + ".html")}">'
            f'<span class="ico">{ICONS["learn"]}</span><span><strong>{esc(name)}</strong>'
            f'<span class="desc">{esc(blurb)}</span></span></a></li>'
        )
    phone = (
        '<nav class="phone-bar" aria-label="Phone">'
        f'<button type="button" data-menu-open data-tour="menu"><span class="is-menu">{ICONS["menu"]}</span>Menu</button>'
        f'<a href="{href(pre, "start.html")}" data-tour="learn">{ICONS["learn"]}Learn</a>'
        f'<a href="{href(pre, "diagrams.html")}" data-tour="diagrams">{ICONS["diagrams"]}Diagrams</a>'
        f'<a href="{href(pre, "play.html")}" data-tour="play">{ICONS["play"]}Play</a>'
        f'<button type="button" data-listen data-tour="listen">{ICONS["listen"]}Listen</button>'
        f'<button type="button" data-open-guide>{ICONS["help"]}Guide</button>'
        "</nav>"
    )
    theme = (
        '<script>try{var t=localStorage.getItem("canon-theme");if(t!=="aurora")t="bloom";'
        'document.documentElement.dataset.theme=t;var f=localStorage.getItem("canon-font");'
        'if(f==="sm"||f==="lg")document.documentElement.dataset.font=f;'
        'var ink=localStorage.getItem("canon-ink");if(ink&&/^#[0-9a-f]{6}$/i.test(ink))'
        'document.documentElement.style.setProperty("--ink",ink);}catch(e){'
        'document.documentElement.dataset.theme="bloom";}</script>'
    )
    head_links = "".join(
        f'<link rel="stylesheet" href="{pre}assets/css/{name}">'
        for name in ("canon.css", "shell.css", "wow.css", "frame.css", "polish.css", "footer.css", "university.css", "uc.css")
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · UC Lab Free University</title>
<meta name="description" content="{esc(desc)}">
<link rel="icon" href="{pre}favicon.svg" type="image/svg+xml">
<link rel="manifest" href="{pre}manifest.webmanifest">
{theme}
{head_links}
<link rel="stylesheet" href="{pre}guide/guide.css">
</head>
<body class="uc-lab" data-uc-page="{esc(current)}" data-track="{esc(track)}">
<a class="skip" href="#main">Skip to content</a>
<header class="uc-top">
<div class="bar-inner">
<button type="button" class="menu-btn" data-menu-open data-tour="menu" aria-expanded="false" aria-controls="site-drawer">{ICONS["menu"]} Menu</button>
<a class="brand" href="{href(pre, "index.html")}" data-tour="home"><span>UC Lab<small>Free University</small></span></a>
<form class="nav-search" role="search"><input class="nav-q" data-nav-search type="search" placeholder="Search rooms" aria-label="Search rooms" autocomplete="off"><div class="search-pop" hidden></div></form>
<div class="display-control"><button type="button" class="display-btn" aria-expanded="false" aria-controls="display-panel">Display</button>
<div id="display-panel" class="display-panel" hidden>
<label>Font size</label>
<div class="a11y-font" role="group" aria-label="Font size">
<button type="button" data-font-set="sm" aria-pressed="false">A−</button>
<button type="button" data-font-set="md" aria-pressed="true">A</button>
<button type="button" data-font-set="lg" aria-pressed="false">A+</button>
</div>
<label for="ink">Font colour</label>
<input id="ink" class="ink-input" data-ink type="color" value="#16182b" aria-label="Font colour">
<label>Theme</label>
<div class="theme-row" role="group" aria-label="Theme">
<button type="button" data-set-theme="bloom" aria-pressed="true">Bright</button>
<button type="button" data-set-theme="aurora" aria-pressed="false">Dark</button>
</div>
</div></div>
</div>
</header>
<div class="canon-banner">
<button type="button" class="rail-arrow" data-rail="prev" aria-label="Scroll sections backward">‹</button>
<nav class="section-rail" aria-label="Sections">{''.join(chips)}</nav>
<button type="button" class="rail-arrow" data-rail="next" aria-label="Scroll sections forward">›</button>
</div>
<div class="drawer-backdrop"></div>
<nav id="site-drawer" class="site-drawer" aria-hidden="true" aria-label="Menu">
<div class="drawer-bar"><strong>Menu</strong><button type="button" data-menu-open>Close</button></div>
<input class="drawer-search" data-drawer-filter type="search" placeholder="Filter" aria-label="Filter the menu">
<ul class="drawer-list">{''.join(rows)}</ul>
</nav>
<main id="main">{body}</main>
{footer()}
{phone}
<script src="{pre}assets/js/frame.js"></script>
<script src="{pre}assets/js/university.js"></script>
<script src="{pre}guide/guide.js"></script>
</body>
</html>
"""


def write_page(rel: str, title: str, desc: str, current: str, body: str, track: str = "") -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    depth = len(Path(rel).parts) - 1
    pre = "../" * depth
    path.write_text(chrome(pre, title, desc, current, body, track), encoding="utf-8")


def dl_buttons(pre: str, slug: str, sheet: str) -> str:
    return (
        '<div class="room-downloads" data-dl>'
        '<span>Export</span>'
        f'<a class="dl-btn" href="{pre}assets/diagrams/university/{slug}.svg" download>SVG</a>'
        f'<a class="dl-btn" href="{pre}downloads/diagrams/{slug}.png" download>PNG</a>'
        f'<a class="dl-btn" href="{pre}downloads/diagrams/{slug}.html" download>HTML</a>'
        f'<a class="dl-btn" href="{pre}downloads/sheets/{sheet}.html" download>Sheet</a>'
        "</div>"
    )


def flow_svg(item: dict) -> str:
    actors = item["actors"]
    steps = item["steps"]
    n = len(actors)
    w = 980
    row_h = 48
    top = 96
    h = top + 24 + len(steps) * row_h
    span = (w - 180) / max(1, n - 1)
    xs = [90 + i * span for i in range(n)]
    colors = ["#22d3ee", "#a5b4fc", "#fbbf24", "#fb7185", "#86efac", "#f9a8d4"]
    slug = item["slug"]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(item["title"])}">',
        f'<defs><marker id="arrow-{slug}" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0 0 L8 3 L0 6 Z" fill="#fff"/></marker></defs>',
        f'<rect width="{w}" height="{h}" rx="18" fill="#0b1020"/>',
        f'<text x="24" y="32" fill="#a5b4fc" font-family="system-ui,sans-serif" font-size="18">{esc(item["title"])}</text>',
    ]
    commands = []
    for i, name in enumerate(actors):
        x = xs[i]
        parts.append(f'<rect x="{x - 64}" y="44" width="128" height="36" rx="12" fill="{colors[i % 6]}"/>')
        parts.append(
            f'<text x="{x}" y="67" text-anchor="middle" font-size="13" font-family="system-ui,sans-serif" fill="#0b1020">{esc(name)}</text>'
        )
        parts.append(f'<line x1="{x}" y1="80" x2="{x}" y2="{h - 18}" stroke="{colors[i % 6]}" stroke-dasharray="6 6"/>')
    for index, (a, b, label) in enumerate(steps):
        y = top + index * row_h
        x1, x2 = xs[a], xs[b]
        parts.append(
            f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="#fff" stroke-width="3" marker-end="url(#arrow-{slug})"/>'
        )
        parts.append(
            f'<text x="{(x1 + x2) / 2}" y="{y - 8}" text-anchor="middle" fill="#e0e7ff" font-size="12" font-family="system-ui,sans-serif">{esc(label)}</text>'
        )
        if not commands:
            commands.append(f"M{x1} {y}")
        commands.append(f"L{x2} {y}")
    parts.append(
        f'<circle r="6" fill="#fde047"><animateMotion dur="7s" repeatCount="indefinite" path="{" ".join(commands)}"/></circle>'
    )
    parts.append("</svg>")
    return "\n".join(parts)


def arch_svg(item: dict) -> str:
    boxes = item["boxes"]
    lines = item.get("lines") or []
    w, h = 980, 320
    gap = (w - 80) / max(1, len(boxes))
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(item["title"])}">',
        f'<rect width="{w}" height="{h}" rx="18" fill="#0b1020"/>',
        f'<text x="24" y="36" fill="#fde68a" font-family="system-ui,sans-serif" font-size="18">{esc(item["title"])}</text>',
    ]
    colors = ["#22d3ee", "#a5b4fc", "#fbbf24", "#fb7185", "#86efac", "#f9a8d4"]
    for i, label in enumerate(boxes):
        x = 40 + i * gap
        parts.append(f'<rect x="{x}" y="70" width="{gap - 24}" height="64" rx="14" fill="{colors[i % 6]}"/>')
        parts.append(
            f'<text x="{x + (gap - 24) / 2}" y="108" text-anchor="middle" font-size="14" font-family="system-ui,sans-serif" fill="#0b1020">{esc(label)}</text>'
        )
        if i:
            parts.append(f'<path d="M{x - 16} 102 H{x}" stroke="#fff" stroke-width="3"/>')
    for i, line in enumerate(lines):
        parts.append(
            f'<text x="32" y="{168 + i * 26}" fill="#e0e7ff" font-size="15" font-family="system-ui,sans-serif">{esc(line)}</text>'
        )
    parts.append("</svg>")
    return "\n".join(parts)


def build_diagrams() -> list[dict]:
    flows = [
        ("sip-register", "SIP registration", ["Phone", "CUCM"], [(0, 1, "REGISTER"), (1, 0, "401"), (0, 1, "REGISTER"), (1, 0, "200")]),
        ("sip-basic-call", "Basic INVITE", ["Alice", "CUCM", "Bob"], [(0, 1, "INVITE"), (1, 2, "INVITE"), (2, 1, "180"), (2, 1, "200"), (1, 0, "200"), (0, 1, "ACK")]),
        ("sip-early-offer", "Early offer", ["Phone", "CUBE"], [(0, 1, "INVITE + SDP"), (1, 0, "100"), (1, 0, "200 + SDP"), (0, 1, "ACK")]),
        ("sip-delayed-offer", "Delayed offer", ["Phone", "PSTN"], [(0, 1, "INVITE"), (1, 0, "200 + offer"), (0, 1, "ACK + answer")]),
        ("sip-prack", "Early media and PRACK", ["Phone", "CUBE", "PSTN"], [(0, 1, "INVITE"), (2, 1, "183"), (1, 0, "183"), (0, 1, "PRACK"), (1, 0, "200")]),
        ("sip-hold", "Hold", ["Phone", "CUCM"], [(0, 1, "re-INVITE sendonly"), (1, 0, "200 recvonly"), (0, 1, "ACK")]),
        ("sip-refer-blind", "Blind transfer", ["Transferor", "Transferee"], [(0, 1, "REFER"), (1, 0, "202"), (1, 0, "NOTIFY")]),
        ("sip-refer-attended", "Attended transfer", ["Transferor", "Transferee"], [(0, 1, "REFER + Replaces"), (1, 0, "202"), (1, 0, "NOTIFY 200")]),
        ("sip-session-timer", "Session refresh", ["Phone", "CUBE"], [(0, 1, "UPDATE"), (1, 0, "200")]),
        ("sip-options", "OPTIONS keepalive", ["CUCM", "CUBE"], [(0, 1, "OPTIONS"), (1, 0, "200")]),
        ("cube-two-legs", "CUBE two legs", ["CUCM", "CUBE", "PSTN"], [(0, 1, "INVITE leg A"), (1, 2, "INVITE leg B"), (2, 1, "200"), (1, 0, "200")]),
        ("dial-peer-hunt", "Dial-peer hunt", ["CUBE", "Carrier A", "Carrier B"], [(0, 1, "INVITE"), (1, 0, "503"), (0, 2, "INVITE"), (2, 0, "200")]),
        ("srst-register", "SRST fallback", ["Phone", "SRST"], [(0, 1, "REGISTER"), (1, 0, "200")]),
        ("css-search", "CSS search order", ["Phone", "CSS", "Partition"], [(0, 1, "dialed digits"), (1, 2, "first match"), (2, 1, "route or block")]),
        ("route-list", "Route list", ["Pattern", "Route list", "Gateway"], [(0, 1, "match"), (1, 2, "route group"), (2, 1, "call sent")]),
        ("translation", "Called-party transform", ["Phone", "Pattern", "Trunk"], [(0, 1, "9 plus national"), (1, 2, "strip access and add prefix")]),
        ("trunk-options", "SIP trunk OPTIONS", ["CUCM", "Trunk", "CUBE"], [(0, 1, "OPTIONS"), (1, 2, "OPTIONS"), (2, 0, "200")]),
        ("exp-traversal", "Traversal zone", ["Expressway-C", "Expressway-E"], [(0, 1, "traversal client"), (1, 0, "keepalive")]),
        ("mra-register", "MRA registration", ["Remote phone", "Exp-E", "Exp-C", "CUCM"], [(0, 1, "TLS"), (1, 2, "traversal"), (2, 3, "REGISTER"), (3, 0, "200")]),
        ("qos-trust", "QoS trust", ["Phone", "Access", "WAN"], [(0, 1, "EF mark"), (1, 2, "trust or remark"), (2, 1, "LLQ")]),
        ("one-way-rtp", "One-way audio", ["Phone A", "CUBE", "Phone B"], [(0, 1, "RTP"), (1, 2, "dropped"), (2, 1, "RTP returns")]),
        ("srtp-sdes", "SRTP with SDES", ["Phone", "CUBE"], [(0, 1, "INVITE crypto"), (1, 0, "200 crypto"), (0, 1, "SRTP")]),
        ("t38", "Fax re-INVITE", ["ATA", "CUBE", "PSTN"], [(0, 2, "voice"), (0, 1, "re-INVITE T.38"), (1, 2, "re-INVITE"), (2, 0, "200")]),
        ("conference", "Ad-hoc conference", ["Phone", "CUCM"], [(0, 1, "hold"), (0, 1, "INVITE third"), (1, 0, "join")]),
        ("park", "Call park", ["Phone A", "CUCM", "Phone B"], [(0, 1, "park"), (2, 1, "retrieve"), (1, 2, "200")]),
        ("snr", "Single number reach", ["Desk", "CUCM", "Mobile"], [(1, 0, "INVITE"), (1, 2, "INVITE"), (0, 1, "200")]),
        ("voicemail", "No answer to voicemail", ["Phone", "CUCM", "Unity"], [(0, 1, "180"), (1, 2, "forward"), (2, 1, "200")]),
        ("e911", "Emergency callback identity", ["Phone", "CUCM", "Gateway"], [(0, 1, "911"), (1, 2, "INVITE + ELIN"), (2, 1, "200")]),
        ("ucce-path", "UCCE comprehensive path", ["PSTN", "CVP", "ICM", "Agent"], [(0, 1, "call"), (1, 2, "route request"), (2, 1, "label"), (1, 3, "deliver")]),
        ("ucce-queue", "Queue until an agent", ["Script", "Queue", "Finesse"], [(0, 1, "queue"), (2, 1, "ready"), (1, 2, "deliver")]),
        ("cucm-ucce", "CUCM and UCCE", ["CUCM", "PG", "ICM"], [(0, 1, "CTI"), (1, 2, "peripheral"), (2, 0, "label")]),
        ("lgw-call", "Local gateway call", ["Webex Calling", "CUBE", "PSTN"], [(0, 1, "SIP TLS"), (1, 2, "INVITE"), (2, 1, "200"), (1, 0, "200")]),
        ("migration-dual", "Dual-run one number", ["Carrier", "CUCM", "Webex"], [(0, 1, "still live"), (0, 2, "test path"), (1, 0, "rollback")]),
        ("survivability", "Survivability gateway", ["Phone", "Local GW", "PSTN"], [(0, 1, "local dial"), (1, 2, "INVITE"), (2, 1, "200")]),
        ("shared-line", "Shared line", ["Phone A", "CUCM", "Phone B"], [(1, 0, "INVITE"), (1, 2, "INVITE"), (0, 1, "200"), (1, 2, "CANCEL")]),
        ("hunt-pilot", "Hunt pilot", ["Caller", "Hunt pilot", "Line group"], [(0, 1, "digits"), (1, 2, "next member"), (2, 1, "200")]),
    ]
    arches = [
        ("uc-stack", "A teaching UC stack", ["Phone", "CUCM", "CUBE", "PSTN"], ["Signaling and media are different paths.", "Confirm every box against the design you actually run."]),
        ("sip-trapezoid", "SIP trapezoid", ["UA", "Proxy", "Proxy", "UA"], ["The dialog is end to end. A proxy is not a party on the RTP path unless it is a B2BUA."]),
        ("dialog-tags", "Dialog identifiers", ["Call-ID", "From tag", "To tag"], ["RFC 3261 section 12. A To tag arrives on a response, not on the first INVITE."]),
        ("codec-bandwidth", "G.711 at 20 ms", ["80 bytes", "+ 40", "80 kbit/s"], ["Layer 3 is about 80 kbit/s. Add the layer-2 header before you size a WAN queue."]),
        ("css-order", "Calling search space order", ["Partition A", "Partition B", "Partition C"], ["CUCM searches the partitions in the order listed on the CSS. First match wins."]),
        ("partition-map", "Who can call whom", ["Lobby", "Internal", "PSTN"], ["A phone with only the lobby partition cannot see the PSTN patterns."]),
        ("route-group", "Route group members", ["RG1 GW-A", "RG1 GW-B"], ["Distribution is top-down or circular. Confirm the setting on the route group."]),
        ("transform-pipe", "Digit transform pipeline", ["Called", "Calling", "Redirect"], ["Name which mask ran. A successful call can still show the wrong caller identity."]),
        ("sip-trunk-profile", "SIP trunk pieces", ["Trunk", "SIP profile", "Security profile"], ["The trunk, the profile, and the security profile are three objects."]),
        ("cube-b2bua", "CUBE is a B2BUA", ["Dialog A", "CUBE", "Dialog B"], ["Read the CUCM leg and the carrier leg as two calls that CUBE relates."]),
        ("dial-peer-match", "Inbound SIP match order", ["URI", "Called", "Calling"], ["Cisco documents URI header matching before called-number on inbound SIP. Confirm the IOS guide for your release."]),
        ("srst-topology", "SRST when CUCM is unreachable", ["Phones", "Local router", "PSTN"], ["Fallback registration is not the same as a normal CUCM registration."]),
        ("exp-pair", "Expressway pair", ["Exp-C", "Firewall", "Exp-E"], ["C sits inside. E sits in the DMZ or outside. The traversal zone joins them."]),
        ("mra-dns", "MRA names", ["SRV", "Exp-E", "CUCM"], ["The phone discovers the edge from DNS. Confirm the SRV names in the current MRA guide."]),
        ("firewall-zones", "Zones, not one ACL", ["Inside", "Traversal", "Outside"], ["Open the ports the deployment guide lists for your version. Do not copy a blog matrix."]),
        ("dscp-map", "Voice marks", ["EF 46", "CS3 signal", "CS5 RFC"], ["RFC 4594 maps telephony to EF. Cisco designs often mark signaling CS3. RFC 4594 points signaling at CS5. Say which standard you are using."]),
        ("llq", "Low-latency queue", ["EF", "Priority", "Rest"], ["Priority bandwidth is a cap, not a guarantee that the link is big enough."]),
        ("delay-budget", "One-way delay budget", ["Packetize", "Queue", "Playout"], ["ITU-T G.114 is the usual source for a 150 ms one-way planning figure. Confirm the current recommendation."]),
        ("locations-cac", "CUCM locations", ["Location A", "Location B", "Bandwidth"], ["CUCM locations limit calls. They do not mark DSCP."]),
        ("ucce-boxes", "UCCE pieces", ["Gateway", "CVP", "ICM", "Finesse"], ["A script chooses a label. The desktop shows the agent state. They are not the same log."]),
        ("cvp-legs", "CVP and the agent", ["Ingress", "VXML", "Agent"], ["Treatment and queue audio are not the agent conversation."]),
        ("finesse", "Agent desktop", ["State", "Call", "Gadgets"], ["Ready is a state. A ringing call is an event. Confirm gadget behavior in the Finesse guide."]),
        ("pstn-choices", "Webex Calling PSTN shapes", ["Calling Plan", "Local GW", "Cloud Connected"], ["These are different operational models. Confirm the names in Webex Help for your tenant."]),
        ("local-gateway", "Local gateway", ["Calling", "CUBE", "PBX or PSTN"], ["The gateway registers or presents a certificate. Confirm which model the control hub location uses."]),
        ("di-versus-calling", "Two different offers", ["Webex Calling", "Dedicated Instance"], ["Dedicated Instance is not a skin on multi-tenant Calling. Confirm the offer before you design dial plan."]),
        ("migration-waves", "Migration waves", ["Pilot", "Site", "Rollback"], ["Move a number you can give back. Keep the old path until evidence says the new path works."]),
        ("evidence-pack", "Evidence before the change", ["Hypothesis", "Capture", "Result"], ["One change. Save the ladder, the counter, and the time."]),
        ("trouble-tree", "Where to look first", ["Signaling", "Media", "Identity"], ["A 200 OK does not prove two-way audio."]),
        ("integration-map", "CUCM, UCCE, and Calling", ["CUCM", "UCCE", "Webex Calling"], ["Bridges are explicit trunks or gateways. A shared brand name is not a shared dial plan."]),
        ("cert-map", "Study toward collaboration exams", ["Associate", "Professional", "Specialist"], ["Exam names change. Confirm the current title on Cisco's certification page before you pay."]),
        ("glossary-map", "Words that travel together", ["Dialog", "CSS", "B2BUA", "EF"], ["Learn the word next to the object it names."]),
        ("timeline", "A honest study order", ["SIP", "Dial plan", "Edge", "Contact center"], ["SRST and Expressway come after you can read a ladder."]),
        ("future-hooks", "What this lab does not decide", ["Your release", "Your carrier", "Your region"], ["Port lists, license counts, and emergency law are local. Confirm them."]),
    ]
    out = []
    for slug, title, actors, steps in flows:
        out.append({"slug": slug, "title": title, "kind": "flow", "actors": actors, "steps": steps})
    for slug, title, boxes, lines in arches:
        out.append({"slug": slug, "title": title, "kind": "arch", "boxes": boxes, "lines": lines})
    return out


def rooms() -> list[dict]:
    common_eco = "Sister pieces sit on the ecosystem page: glossary, the mind map, and the CUCM to Webex Calling bridge."
    rows = [
        dict(id="T1-R01", track="T1", slug="sip-transactions", title="SIP transactions and dialogs", diagram="sip-basic-call", sheet="sip",
             five=["A transaction pairs a request with its responses.", "INVITE, its final response, and the ACK for a 2xx are how a call is accepted.", "A dialog needs a Call-ID and both tags. A 100 Trying has no To tag.", "BYE ends that dialog.", "RTP does not have to follow the proxy that forwarded the INVITE."],
             core="RFC 3261 separates transactions from dialogs. People debug the wrong object when a retransmitted 200 is treated as a second call, or when a To tag on a 180 is treated as an answer. The 180 means alerting. The 200 means the far end accepted the session. ACK completes that handshake for a 2xx. Media can start once offer and answer are known, which is often the 200, and the packets may go directly between the endpoints.",
             example="A phone sends INVITE through CUCM. CUCM is a back-to-back user agent in this path, so you may see two Call-IDs. On each leg, find the branch, the CSeq, and the tags before you decide the call failed.",
             quiz=[("A 180 Ringing means the call was answered.", "False. It means alerting. The 200 accepts the session.", ["True", "False"], "False"),
                   ("ACK for a 2xx is optional.", "False. Without ACK the far end retransmits the 200 and can drop the call.", ["True", "False"], "False")],
             sources=[RFC3261], glossary=[("Transaction", "A request and its matching responses."), ("Dialog", "A peer relationship identified by Call-ID and tags.")],
             config="On a ladder, write the method, status, CSeq, and tags for one leg only.",
             trouble="If the 200 repeats, look for a missing ACK before you look at QoS.",
             bridge="CUCM, CUBE, and a carrier SBC can each be a B2BUA. Count the dialogs.",
             confirm=""),
        dict(id="T1-R02", track="T1", slug="offer-answer", title="Offer and answer", diagram="sip-early-offer", sheet="sip",
             five=["SDP is the offer or the answer, not a second signaling protocol you ignore.", "Early offer puts the offer in the INVITE.", "The answer lists what was accepted, not a new unrelated codec list.", "A re-INVITE can change hold, codec, or fax.", "RFC 3264 is the rule for which lines may be answered."],
             core="Early offer is common on CUCM SIP trunks. Delayed offer puts the offer in the 200 and the answer in the ACK. Mixing them on a CUBE without a plan produces a call that signals and then has no media, or a codec neither side wanted. Read m= lines and the direction attributes before you blame the WAN.",
             example="An INVITE carries G.711 and G.729. The 200 answers with G.711 only. The call is G.711. If the 200 has no audio m-line you accepted, you do not have a voice call yet.",
             quiz=[("The answer may add a codec the offer did not list.", "False. The answer narrows the offer.", ["True", "False"], "False")],
             sources=[RFC3264, RFC3261], glossary=[("Early offer", "SDP in the INVITE."), ("Delayed offer", "SDP offered in the reliable response or the 200.")],
             config="Check the SIP trunk's early offer setting before you compare two traces.",
             trouble="One-way audio sometimes starts as an unanswered direction attribute, sendonly against sendonly.",
             bridge="Webex Calling local gateway guides expect early offer and SRTP. Confirm the current guide.",
             confirm="Confirm the early-offer checkbox name in the CUCM version you run."),
        dict(id="T1-R03", track="T1", slug="sip-registration", title="Registration", diagram="sip-register", sheet="sip",
             five=["REGISTER publishes a Contact. It does not place a call.", "The Request-URI is the registrar domain, not the user's address-of-record.", "401 challenges the user. A second REGISTER must use a new CSeq.", "The binding expires.", "A registered phone can still be unreachable for media."],
             core="RFC 3261 section 10 is the whole idea. CUCM is the registrar for the phones that point at it. A successful 200 means CUCM stored a binding until it expires or the phone removes it. It does not mean the WAN will carry RTP.",
             example="First REGISTER, 401, second REGISTER with Authorization and CSeq plus one, then 200. If the second CSeq matches the first, the registrar treats it as a replay.",
             quiz=[("REGISTER creates a voice session.", "False. It stores a Contact binding.", ["True", "False"], "False")],
             sources=[RFC3261, CUCM], glossary=[("AOR", "The address-of-record being registered."), ("Contact", "The device URI to try later.")],
             config="Compare the phone's CUCM address, the digest user, and the registration timer.",
             trouble="A phone that flips between registered and rejected is often a credential, a trust list, or a clock, not a dial plan.",
             bridge="MRA still ends in a CUCM registration. The Expressway pair is the path, not a second registrar you invent.",
             confirm=""),
        dict(id="T1-R04", track="T1", slug="prack-early-media", title="Early media and PRACK", diagram="sip-prack", sheet="sip",
             five=["183 Session Progress can carry SDP before answer.", "A reliable provisional response wants PRACK.", "PRACK is its own transaction.", "Early media is not the same as answer.", "RFC 3262 is the specification."],
             core="Carriers often send ringback or an announcement as early media. If the caller hears silence until the 200, the 183 may have been unreliable and ignored, or the early RTP never arrived. Do not mark the call answered because you heard a tone.",
             example="INVITE, 183 with Require 100rel and SDP, PRACK, 200 OK of the PRACK, later 200 OK of the INVITE, ACK. The tone is the 183. The answer is the later 200.",
             quiz=[("Hearing ringback proves the called party answered.", "False. Ringback can be early media.", ["True", "False"], "False")],
             sources=[RFC3262, RFC3261], glossary=[("PRACK", "Acknowledgement of a reliable provisional response."), ("100rel", "The extension that makes selected 1xx responses reliable.")],
             config="If one side requires 100rel and the other cannot send PRACK, the call fails before answer.",
             trouble="Save the 183 and say whether RTP to that address was visible.",
             bridge="CUBE can interwork early media between a CUCM trunk and a carrier. Read both legs.",
             confirm=""),
        dict(id="T2-R01", track="T2", slug="partitions-css", title="Partitions and calling search spaces", diagram="css-order", sheet="dial-plan",
             five=["A partition is a bucket of patterns.", "A calling search space is an ordered list of partitions.", "The phone, the line, and the trunk can each have a CSS.", "First match in that order wins.", "A pattern you cannot see is not a failed route. It is invisible."],
             core="This is the CUCM dial plan's access control. Lobby phones should not see the PSTN partition. Emergency patterns are usually placed so that every CSS used by a phone can find them. Confirm the emergency design for your region rather than copying a lab CSS.",
             example="A phone CSS lists Internal then PSTN. The user dials a ten-digit number that also exists as a shorter internal pattern. If the shorter pattern is in an earlier partition, it matches first.",
             quiz=[("CUCM searches every partition and picks the longest match across all of them.", "False. It walks the CSS in order.", ["True", "False"], "False")],
             sources=[CUCM], glossary=[("Partition", "A group of patterns with the same reachability."), ("CSS", "An ordered list of partitions.")],
             config="Read the CSS on the device and on the line. Both can apply.",
             trouble="DNA, or the Dialed Number Analyzer when your version has it, shows the path. Confirm the tool name in your release.",
             bridge="Webex Calling locations and routing are a different model. Do not paste CSS words onto a Calling location.",
             confirm="Confirm the analyzer name and menu for your CUCM version."),
        dict(id="T2-R02", track="T2", slug="route-patterns", title="Route patterns, lists, and groups", diagram="route-list", sheet="dial-plan",
             five=["A route pattern matches digits.", "A route list holds route groups in order.", "A route group holds gateways or trunks.", "Distribution inside the group is its own setting.", "A pattern pointed at a gateway skips the list."],
             core="When the PSTN call fails over, you are usually looking at the route list order and whether the first member sent a release cause that CUCM is willing to hunt on. Not every failure hunts.",
             example="Pattern 9.! sends national calls to a route list. Group 1 is the primary SIP trunk. Group 2 is the backup. A 503 from the first trunk can hunt. A fast busy from a downstream reason may not. Read the cause.",
             quiz=[("A route group is a list of partitions.", "False. It is a list of gateways or trunks.", ["True", "False"], "False")],
             sources=[CUCM], glossary=[("Route pattern", "Digits in a partition that point at a gateway or route list."), ("Route list", "An ordered set of route groups.")],
             config="Name the pattern, the list, the group, and the member before you change hunting.",
             trouble="If only some calls fail, compare the digit string with the pattern, not the trunk status alone.",
             bridge="A Webex Calling route group is a different object. Say which product you mean.",
             confirm=""),
        dict(id="T2-R03", track="T2", slug="transformations", title="Transformations", diagram="transform-pipe", sheet="dial-plan",
             five=["Called, calling, and redirecting numbers are different fields.", "A mask can fix or break caller ID.", "Translation patterns change digits and can change the CSS.", "External phone number masks are a presentation tool.", "Write the digits before and after each step."],
             core="Most 'wrong caller ID' tickets are a mask on the route pattern, the route list, or the trunk, applied in an order the engineer did not draw. Capture the outgoing INVITE and compare it with the directory number.",
             example="Users dial 9 and a national number. The pattern strips the 9 and prefixes the carrier's expected digits. The calling number is masked to the site's main number. If the mask is the directory number instead, the carrier may reject the call.",
             quiz=[("The calling number and the called number are the same field.", "False.", ["True", "False"], "False")],
             sources=[CUCM], glossary=[("Translation pattern", "A pattern that transforms digits and can continue routing."), ("Mask", "A digit rewrite applied to a number field.")],
             config="On the ladder, copy the From and the Request-URI after the trunk.",
             trouble="If inbound calls show the wrong name, look at inbound transformations and the directory lookup, not only outbound masks.",
             bridge="Local gateway digit manipulation on IOS and CUCM masks can both run. Decide which box owns the plan.",
             confirm=""),
        dict(id="T2-R04", track="T2", slug="sip-trunks", title="SIP trunks on CUCM", diagram="sip-trunk-profile", sheet="dial-plan",
             five=["The trunk, the SIP profile, and the security profile are three objects.", "OPTIONS can mark a trunk out of service.", "Early offer is a setting, not a guess.", "Run on all nodes is a choice with consequences.", "A trunk in service can still route nowhere if the CSS is empty."],
             core="CUCM sends OPTIONS when the profile says so. A trunk that looks down may be a failed OPTIONS to an address that does not answer, while calls would have worked, or the reverse. Read the destination address and the profile together.",
             example="A new CUBE peer answers calls but CUCM marks the trunk down. The OPTIONS ping target is a different IP than the INVITE target. Fix the target you actually configured, then retest.",
             quiz=[("A SIP trunk in service proves the route pattern points at it.", "False. Routing and status are separate.", ["True", "False"], "False")],
             sources=[CUCM, RFC3261], glossary=[("SIP trunk", "CUCM's signaling peer toward a gateway or another call agent."), ("SIP profile", "Timers, OPTIONS, and offer behavior for that trunk.")],
             config="Record profile name, security profile, destination, and CSS.",
             trouble="Compare a failed call's SIP cause with the trunk status at that minute.",
             bridge="The local gateway trunk toward Webex Calling is still a SIP trunk with its own profile. Confirm the Webex guide.",
             confirm="Confirm OPTIONS defaults in your CUCM version."),
        dict(id="T3-R01", track="T3", slug="dial-peers", title="Dial peers", diagram="dial-peer-match", sheet="cube",
             five=["A dial peer matches an incoming or outgoing call.", "Inbound SIP matching checks URI headers before called number on current Cisco IOS guidance.", "Outbound hunt prefers the longest match, then preference.", "Preference is not the same as a CUCM route list.", "A peer with no session target does not send a call."],
             core="Engineers memorize one match order and apply it to every release. Cisco's SIP matching article is the source for the release you run. The teaching order used here is URI, then called number, then calling number for inbound SIP, and longest match then preference for outbound. Confirm that article before you change a production peer.",
             example="Two outbound peers match the same number. Preference 1 points at a dead carrier. The call waits on that peer until the timeout, then tries preference 2. Users call it slow dial tone to the PSTN.",
             quiz=[("Outbound dial-peer preference is consulted before match length.", "False. Longest match comes first when hunt is the default.", ["True", "False"], "False")],
             sources=[CUBE], glossary=[("Dial peer", "An IOS rule that matches a call and names a target."), ("Preference", "A tie-break after match length.")],
             config="debug voip dialpeer inout is noisy. Use it on one call, then turn it off.",
             trouble="If the wrong carrier gets the call, print the matched peer number from the debug, not from memory.",
             bridge="CUCM route patterns and IOS dial peers are two plans. Draw both.",
             confirm="Confirm inbound match order in the IOS dial-peer guide for your release."),
        dict(id="T3-R02", track="T3", slug="cube-b2bua", title="CUBE as a B2BUA", diagram="cube-two-legs", sheet="cube",
             five=["CUBE terminates one dialog and starts another.", "Codec, DTMF, and header policies are per leg unless you bind them.", "Media can anchor on CUBE or flow around it, depending on the design.", "A 200 on the CUCM leg does not prove the carrier leg is up.", "Read IP addresses on each SDP."],
             core="Unified Border Element is Cisco's SBC on IOS. Treat it as two calls. Mid-call services such as transfer and hold are re-INVITEs CUBE must map. If you only capture the CUCM side, you will miss a carrier rejection.",
             example="CUCM sends G.711. The carrier peer allows G.729 only. CUBE can transcode if a DSP is configured and licensed for that feature. If not, the carrier leg fails and CUCM may see a different cause than 'no DSP'.",
             quiz=[("CUBE forwards one SIP dialog unchanged, like a proxy.", "False. It is a B2BUA.", ["True", "False"], "False")],
             sources=[CUBE, RFC3261], glossary=[("B2BUA", "A user agent that sits between two dialogs."), ("Media anchor", "RTP terminates on the SBC.")],
             config="Show the inbound peer, the outbound peer, and whether a transcoder profile is bound.",
             trouble="Capture both legs. One ladder is not the call.",
             bridge="The same CUBE can be a Webex Calling local gateway and a CUCM PSTN gateway. Those are different dial peers.",
             confirm="DSP and license names vary by platform. Confirm before you order hardware."),
        dict(id="T3-R03", track="T3", slug="srst", title="SRST", diagram="srst-topology", sheet="cube",
             five=["SRST is the fallback when phones cannot reach CUCM.", "The router becomes a small call agent for the phones that fail over.", "Dial plan on SRST is a subset you configured, not the full CUCM CSS.", "Fallback is a registration event.", "When CUCM returns, phones re-home. Confirm the timers."],
             core="Survivable Remote Site Telephony keeps a branch placing and receiving a planned set of calls during a WAN failure. It is not an automatic copy of every CUCM feature. Hunt pilots, pickup, and presence may not exist in fallback. Test the fallback dial plan on purpose.",
             example="WAN down. Phones show a fallback mode and register to the branch router. 911 and local PSTN still match the SRST dial peers. An internal abbreviation that lived only in CUCM fails. That failure is expected if you never built it on SRST.",
             quiz=[("SRST automatically clones every CUCM hunt pilot.", "False.", ["True", "False"], "False")],
             sources=[SRST, CUCM], glossary=[("SRST", "Fallback call processing on the branch router."), ("Re-home", "Phones returning to CUCM after the WAN recovers.")],
             config="List the numbers that must work in fallback, including emergency, and test them.",
             trouble="A phone that never falls back may still be reaching CUCM over a path you thought was down.",
             bridge="Webex Calling survivability gateway is a different feature. Do not use the SRST command set as if it were that feature.",
             confirm="Confirm whether the site uses SRST, E-SRST, or Unified SRST for the platform you run."),
        dict(id="T3-R04", track="T3", slug="local-gateway", title="Local gateway toward Webex Calling", diagram="local-gateway", sheet="cube",
             five=["The local gateway is how premises PSTN or a PBX meets Webex Calling.", "Signaling to Calling is SIP over TLS. Media is SRTP.", "Registration-based and certificate-based trunks are different models.", "Dial peers still decide the premises leg.", "Confirm call caps and ciphers in the current guide."],
             core="Cisco's Webex Calling local gateway documentation describes CUBE as the supported trunk on the premises side for this design. A registration trunk and a certificate trunk do not have the same limits. People quote a 250-call registration cap from older guides. Treat that number as something to confirm in the guide for your tenant before you design to it.",
             example="A location uses a local gateway. Inbound DID hits a Webex dial peer, and outbound PSTN hits a carrier peer. If you only debug one peer, you will explain the wrong leg.",
             quiz=[("A local gateway registration is the same object as a CUCM phone registration.", "False. It is the trunk from CUBE toward Calling.", ["True", "False"], "False")],
             sources=[WEBEX, CUBE], glossary=[("Local gateway", "The premises SBC that connects Webex Calling to PSTN or a PBX."), ("Certificate trunk", "A trunk that authenticates with a certificate instead of a registration.")],
             config="Keep the Webex peer and the carrier peer in the drawing.",
             trouble="If Calling shows the gateway offline, check registration or certificate status before the carrier.",
             bridge="This is the usual bridge during a CUCM to Calling migration when the PSTN stays on premises.",
             confirm="Confirm the current registration call cap, cipher suite, and supported platforms in Webex Help."),
        dict(id="T4-R01", track="T4", slug="expressway-pair", title="Expressway-C and Expressway-E", diagram="exp-pair", sheet="expressway",
             five=["Expressway-C lives on the inside, next to CUCM.", "Expressway-E lives at the edge.", "A traversal zone connects them.", "They are not a SIP proxy you insert in every PSTN call.", "Clustering and certificates are part of the design, not an afterthought."],
             core="The pair exists so devices on the internet can reach CUCM services without exposing CUCM. Traversal keeps the connection initiated from the inside. If you treat C and E as two unrelated servers, MRA will not come up.",
             example="Phones on the LAN register straight to CUCM. Phones off the LAN use the Expressway pair. A PSTN call from a LAN phone does not need to hairpin through Expressway unless you designed it that way.",
             quiz=[("Every CUCM call must pass through Expressway.", "False.", ["True", "False"], "False")],
             sources=[EXP, CUCM], glossary=[("Traversal zone", "The zone that joins Expressway-C and Expressway-E."), ("Expressway-E", "The edge server.")],
             config="Name the zone, the peer addresses, and which side is the client.",
             trouble="Certificate names that do not match the traversal peer fail quietly until you read the zone status.",
             bridge="Expressway is also used in some hybrid calling designs. Confirm whether your tenant still uses that hybrid path.",
             confirm="Hybrid Calling architectures have changed. Confirm the current Webex hybrid document before you build one."),
        dict(id="T4-R02", track="T4", slug="mra", title="Mobile and Remote Access", diagram="mra-register", sheet="expressway",
             five=["MRA lets a remote Cisco phone or Jabber register to CUCM through the Expressway pair.", "DNS SRV records point the client at Expressway-E.", "The registration still belongs to CUCM.", "Media traversal is a separate problem from the REGISTER.", "A VPN is a different design. Do not mix the words."],
             core="Users say the phone is 'on the VPN' when it is on MRA, or the reverse. The logs are different. MRA failures are often DNS, certificates, or the CUCM registration that never completes after the edge accepted the TLS session.",
             example="A remote phone resolves the edge, completes TLS to Expressway-E, and never appears on CUCM. The traversal zone is up, but the CUCM domain or the registration allow list on Expressway does not include that device. Look at the Expressway registration status and then CUCM.",
             quiz=[("MRA replaces CUCM as the registrar.", "False. CUCM remains the registrar.", ["True", "False"], "False")],
             sources=[EXP, CUCM], glossary=[("MRA", "Mobile and Remote Access through Expressway."), ("SRV", "A DNS record the client uses to find the edge.")],
             config="Record the SRV names you published and the certificate SAN.",
             trouble="If LAN phones work and remote phones fail, compare DNS and certificates before the dial plan.",
             bridge="Webex app registration to the cloud is not MRA. Say which client you mean.",
             confirm="Confirm the current SRV names and port list in the MRA deployment guide."),
        dict(id="T4-R03", track="T4", slug="firewall-traversal", title="Firewall and traversal", diagram="firewall-zones", sheet="expressway",
             five=["Open the ports your version's guide lists.", "Signaling ports and media ranges are different lines.", "Traversal media is not the same range as a phone's RTP range on the LAN.", "One ACL copied from a blog is how outages start.", "Write the source, destination, and direction."],
             core="Cisco publishes a port reference with the Expressway and MRA guides. It changes. This lab does not reprint a port matrix as if it were current. The skill is to read the matrix for your version and test one flow: registration, then a call, then hold.",
             example="Registration works and the call has no audio. Signaling ports were opened. The media range for traversal was not. The ladder shows 200 OK. RTP counters on one side stay at zero.",
             quiz=[("A completed INVITE proves the firewall allows RTP.", "False.", ["True", "False"], "False")],
             sources=[EXP, RFC3550], glossary=[("Traversal media", "The UDP range Expressway uses for remote media."), ("Signaling", "SIP or the HTTPS path used to register.")],
             config="Quote the guide's table row, the version, and the date you read it.",
             trouble="Capture on both sides of the firewall before you widen every range.",
             bridge="CUBE PSTN media ranges and Expressway traversal ranges are different tables.",
             confirm="Confirm every port in the deployment guide for the Expressway version you run."),
        dict(id="T5-R01", track="T5", slug="dscp-trust", title="DSCP and the trust boundary", diagram="dscp-map", sheet="qos",
             five=["Voice RTP is commonly marked EF, DSCP 46.", "RFC 3246 defines Expedited Forwarding.", "RFC 4594 maps telephony to EF and points signaling at CS5.", "Cisco campus designs often mark call signaling CS3.", "Say which document you are following."],
             core="Phones can mark packets. Switches can trust that mark or rewrite it. If the access port does not trust the phone, the WAN queue never sees EF, and the priority class stays empty while voice is delayed in the default class.",
             example="A capture at the phone shows DSCP 46. A capture after the access switch shows DSCP 0. The trust boundary is the switchport. Fix the policy there before you resize the WAN queue.",
             quiz=[("EF and CS3 are the same mark.", "False. EF is DSCP 46. CS3 is a different codepoint.", ["True", "False"], "False")],
             sources=[RFC3246, RFC4594], glossary=[("EF", "Expedited Forwarding, DSCP 46."), ("Trust boundary", "The place you decide to keep or rewrite a mark.")],
             config="Record the policy-map and the interface direction.",
             trouble="Look at the mark on the wire, not the mark configured on the phone alone.",
             bridge="Webex Calling media on the internet is not your EF queue unless you have a path that still honors DSCP. Often it does not.",
             confirm=""),
        dict(id="T5-R02", track="T5", slug="llq-delay", title="LLQ and the delay budget", diagram="delay-budget", sheet="qos",
             five=["Priority queue bandwidth is a limiter for the EF class.", "Serialization, queuing, propagation, packetization, and jitter buffer all add delay.", "ITU-T G.114 is the usual citation for a 150 ms one-way planning target.", "A queue cannot create bandwidth the circuit does not have.", "Confirm the current ITU text before you treat 150 ms as a contract."],
             core="G.711 at 20 ms is about 80 kbit/s at layer 3 and about 87.2 kbit/s with an 18-byte Ethernet header. The formula is (payload + 40 + layer-2) times 8 times packets per second, then divide by 1000 for kbit/s. Size the priority class from calls you allow, not from a feeling.",
             example="Twenty G.711 calls want about 1.6 Mbit/s at layer 3 before overhead. A priority statement of 512 kbit/s will drop or delay the rest. Users hear it as clipping, not as a SIP error.",
             quiz=[("LLQ adds bandwidth to a circuit.", "False. It schedules the bandwidth you already have.", ["True", "False"], "False")],
             sources=[ITU, RFC4594], glossary=[("LLQ", "A queue that serves a priority class up to a configured rate."), ("Packetization", "The time to fill one RTP payload.")],
             config="Write the class rate next to the number of calls.",
             trouble="If signaling succeeds and MOS collapses only at busy hour, look at drops in the priority class.",
             bridge="CAC in CUCM can limit calls so the queue is not overrun. QoS and CAC are partners.",
             confirm="Confirm the current G.114 text. The 150 ms figure is the classic planning number, not a promise about your carrier."),
        dict(id="T5-R03", track="T5", slug="locations-cac", title="Locations and call admission control", diagram="locations-cac", sheet="qos",
             five=["A CUCM location names a bandwidth budget between sites.", "CAC refuses a call. QoS schedules a call that was allowed.", "Audio and video budgets are separate in current CUCM designs.", "Refused calls show a cause, not silence.", "Locations do not mark DSCP."],
             core="If you set the location bandwidth below the real queue, CUCM blocks calls the WAN could have carried. If you set it far above the queue, CUCM admits calls the queue will damage. The two numbers should be designed together.",
             example="Site A to site B is 1 Mbit/s for voice in CUCM and 512 kbit/s in the priority queue. The sixth G.711 call is admitted and then sounds broken. Align the location with the queue, or the reverse, on purpose.",
             quiz=[("CUCM locations mark RTP as EF.", "False.", ["True", "False"], "False")],
             sources=[CUCM], glossary=[("Location", "A CUCM bandwidth domain for admission control."), ("CAC", "Call admission control, the decision to allow a call.")],
             config="Record location bandwidth and the WAN policy in the same note.",
             trouble="A reorder from CUCM with no SIP error on the carrier is often CAC or a CSS, not the PSTN.",
             bridge="Webex Calling does not use CUCM locations for cloud media. Keep the words apart.",
             confirm="Confirm video bandwidth defaults in your CUCM version."),
        dict(id="T6-R01", track="T6", slug="ucce-path", title="UCCE from carrier to agent", diagram="ucce-path", sheet="ucce",
             five=["Ingress, routing, queue treatment, and the agent are different stages.", "CVP can front the call and ask ICM for a label.", "The routing script returns a destination. It is not the audio file.", "Finesse shows agent state.", "CUIC reports what was logged, which can lag the call."],
             core="Unified Contact Center Enterprise is a system of pieces: gateway, CVP, the ICM router and logger, peripheral gateways, and the desktop. A teaching path is PSTN to the gateway, control to CVP and ICM, then delivery to an agent on CUCM. Your deployment can be a different model. Name the model before you debug.",
             example="The caller hears queue music, so CVP treatment works. No agent is offered the call. Look at skill group staffing and the script's queue node before you restart the gateway.",
             quiz=[("Queue music means an agent phone is ringing.", "False. Treatment happens before delivery.", ["True", "False"], "False")],
             sources=[UCCE], glossary=[("CVP", "Customer Voice Portal, the voice browser and call-control front in many designs."), ("ICM", "The routing brain in UCCE.")],
             config="Save the script name, the label returned, and the agent device target.",
             trouble="Separate 'no route' from 'no agent available'.",
             bridge="CUCM still places the agent call. A CUCM partition mistake looks like an ICM failure.",
             confirm="Confirm component names against the design guide for your UCCE release."),
        dict(id="T6-R02", track="T6", slug="cucm-ucce-bridge", title="The CUCM bridge into UCCE", diagram="cucm-ucce", sheet="ucce",
             five=["Agents are CUCM endpoints.", "The peripheral gateway watches those endpoints.", "A label must be a number CUCM can route.", "CTI controls the desktop. The SIP call is still a call.", "Device targets and extensions drift apart when people rename lines."],
             core="The bridge fails in ordinary ways: the script returns a label that is not a directory number, the phone is in a partition the CTI route point cannot reach, or the agent is not associated with the application user. None of those are a mystery queue.",
             example="ICM returns label 4501. CUCM has 4501 in a partition the trunk CSS cannot see. The call dies after a successful script. Fix the CSS or the label, and say which one you changed.",
             quiz=[("A successful ICM script guarantees CUCM can ring the phone.", "False.", ["True", "False"], "False")],
             sources=[UCCE, CUCM], glossary=[("Label", "The destination the script returns."), ("Peripheral gateway", "The process that represents CUCM devices to ICM.")],
             config="Match the label to a route pattern or directory number and name the CSS.",
             trouble="Look at the CUCM dial plan trace for that label, not only the script monitor.",
             bridge="This is the on-premises bridge. A Webex Contact Center flow is a different product.",
             confirm=""),
        dict(id="T6-R03", track="T6", slug="wxcc-and-ucce", title="Webex Contact Center beside UCCE", diagram="integration-map", sheet="ucce",
             five=["Webex Contact Center and UCCE are different products.", "A flow in one is not an ICM script in the other.", "Some customers bridge them during a migration. That bridge is a designed trunk or call route, not a brand promise.", "Reporting names differ.", "Do not claim a feature exists on both without the current data sheet."],
             core="This lab will not invent a feature matrix. If you are moving a call type, write the entry point, the queue, the agent desktop, and the report you will use as proof. Confirm each one in the product help for the tenant you have.",
             example="A number still enters UCCE while a pilot number enters Webex Contact Center. They do not share a queue just because both are Cisco. Test the pilot with one call and one report before you move the main number.",
             quiz=[("An ICM script runs unchanged inside Webex Contact Center.", "False.", ["True", "False"], "False")],
             sources=[UCCE, WEBEX], glossary=[("Flow", "The routing document in Webex Contact Center."), ("Script", "The routing document in ICM.")],
             config="Name the product on every diagram box.",
             trouble="If the wrong desktop rings, you moved the number into the wrong product.",
             bridge="Keep UCCE on its own sheet until the cutover evidence says otherwise.",
             confirm="Confirm connectors and coexistence in the current Webex Contact Center documentation."),
        dict(id="T7-R01", track="T7", slug="calling-versus-di", title="Webex Calling and Dedicated Instance", diagram="di-versus-calling", sheet="migration",
             five=["Multi-tenant Webex Calling and Dedicated Instance are different offers.", "Calling locations, numbers, and features are managed in Control Hub.", "Dedicated Instance is CUCM hosted for you, with its own dial plan.", "A local gateway is a PSTN choice for Calling, not the definition of Calling.", "Confirm the offer on the subscription before you design."],
             core="People say 'we moved to Webex' and mean four different architectures. Ask whether the phone registers to Calling, to a Dedicated Instance CUCM, or still to the old CUCM through a trunk. The ladder answers it.",
             example="A site keeps CUCM and sends only a pilot range to Webex Calling through a local gateway. That is coexistence, not a finished migration. Draw the numbers that still live on CUCM.",
             quiz=[("Dedicated Instance uses the same dial-plan objects as multi-tenant Calling.", "False.", ["True", "False"], "False")],
             sources=[WEBEX, CUCM], glossary=[("Dedicated Instance", "A hosted CUCM offer inside the Webex cloud contract."), ("Control Hub", "The admin place for Webex Calling locations and numbers.")],
             config="Write the registration target of one test phone.",
             trouble="If the phone still registers to the old CUCM, you have not moved that user.",
             bridge="The local gateway is the usual SIP bridge during coexistence.",
             confirm="Confirm offer names and feature gaps in the current Webex Calling data sheet."),
        dict(id="T7-R02", track="T7", slug="dual-run", title="Dual-run and rollback", diagram="migration-dual", sheet="migration",
             five=["Move one number you can give back.", "Keep the old route until the new path passes a scripted test.", "Rollback is a planned route, not a hope.", "Porting a carrier number is slower than changing a lab route.", "Evidence is a call, a ladder, and a user check."],
             core="Dual-run means the same business number can still be delivered the old way while you prove the new way, or that you can return it quickly. Carrier ports do not always allow an instant return. Say which kind of move you are doing before the night of the change.",
             example="A DID is translated to Webex Calling for a day, with the CUCM translation pattern saved. The test call fails caller ID. You put the old translation back and attach both INVITEs to the ticket. That is a rollback, not a defeat.",
             quiz=[("A carrier port can always be undone in five minutes.", "False. Confirm the porting rules.", ["True", "False"], "False")],
             sources=[WEBEX, CUCM], glossary=[("Dual-run", "Old and new paths both available for a number during a test."), ("Rollback", "Returning the number to the path you saved.")],
             config="Save the route pattern or translation before you edit it.",
             trouble="If you cannot name the old route, you cannot roll back.",
             bridge="CUBE dial peers and CUCM patterns both need a saved copy.",
             confirm="Confirm porting lead times with the carrier. This lab does not know your contract."),
        dict(id="T7-R03", track="T7", slug="cutover-survivability", title="Survivability during cutover", diagram="survivability", sheet="migration",
             five=["Cloud calling needs a plan for when the cloud path is down.", "A survivability gateway is a Webex Calling feature. Confirm it is on your subscription.", "SRST is the CUCM-era feature. It does not automatically cover Webex apps.", "Emergency calling must be tested on the fallback path.", "Write who can call whom when the WAN is down."],
             core="Cutover weekend is the worst time to discover that branch phones have no local PSTN. If the design uses a survivability gateway, test it before you move the numbers. If the design is CUCM with SRST, test SRST. Do not assume one covers the other.",
             example="After the site moves to Calling, you pull the WAN. The survivability gateway registers the phones it is responsible for and places a local emergency call. If that call fails, the site is not ready, even if the happy-path cloud call worked.",
             quiz=[("SRST protects Webex Calling apps with no extra design.", "False.", ["True", "False"], "False")],
             sources=[WEBEX, SRST], glossary=[("Survivability gateway", "A local gateway mode that keeps selected Calling users up during a cloud outage."), ("Fallback test", "A planned failure of the primary path.")],
             config="Name the gateway, the users in scope, and the emergency number you will dial in a test window.",
             trouble="A test that only pings the gateway does not prove a call.",
             bridge="Keep the CUCM SRST test in the old design until that site has actually moved.",
             confirm="Confirm survivability gateway support and limits in the current Webex Calling guide."),
        dict(id="T8-R01", track="T8", slug="one-change", title="One hypothesis, one change", diagram="evidence-pack", sheet="trouble",
             five=["Say what you think is broken, in one sentence.", "Change one thing.", "Capture before and after.", "If the symptom does not move, revert.", "A bundle of changes is not a lesson."],
             core="Voice tickets get worse when five settings change before the first ladder is saved. The evidence pack is the hypothesis, the time, the calling and called numbers, the SIP ladder or the CUCM trace, and the result. Store it next to the change.",
             example="Hypothesis: the trunk CSS cannot see the PSTN partition. Change: add that partition. Result: the same call now leaves CUCM and fails further downstream. You learned something. You did not also restart the cluster.",
             quiz=[("Changing the CSS, the codec, and the gateway in one window is a clean test.", "False.", ["True", "False"], "False")],
             sources=[CUCM], glossary=[("Hypothesis", "The single fault you are testing."), ("Evidence pack", "The traces and notes that show the test.")],
             config="Paste the relevant lines, not a 40-page trace, into the note.",
             trouble="If you cannot revert, you did not have a change. You had an accident.",
             bridge="The same habit works on CUBE dial peers and on Calling locations.",
             confirm=""),
        dict(id="T8-R02", track="T8", slug="read-a-ladder", title="Reading a ladder", diagram="sip-basic-call", sheet="trouble",
             five=["One leg at a time.", "Method, status, CSeq, Call-ID, tags.", "SDP addresses are where media was supposed to go.", "A cause code is a clue, not a root cause by itself.", "Compare a good call of the same type."],
             core="Start at the first request that belongs to the failure. Note who sent it and who answered. If there are two Call-IDs, you have a B2BUA. Follow the leg that actually failed, then step back one box.",
             example="CUCM sends INVITE to CUBE. CUBE answers 503. The carrier leg has no INVITE. The failure is on CUBE before the carrier, often dial-peer or a down interface. Do not open a carrier ticket yet.",
             quiz=[("Two Call-IDs mean the trace is corrupt.", "False. A B2BUA creates two dialogs.", ["True", "False"], "False")],
             sources=[RFC3261, CUBE], glossary=[("Ladder", "A drawing of messages between named boxes."), ("Cause", "The reason phrase or Q.850 cause on a failure.")],
             config="Filter the capture by Call-ID after you have identified it.",
             trouble="Wireshark's flow graph is a view. You still have to name the boxes.",
             bridge="A Calling call may show TLS you cannot decrypt. Say that, and use the product's own call log as the other view.",
             confirm=""),
        dict(id="T8-R03", track="T8", slug="one-way-audio", title="One-way audio", diagram="one-way-rtp", sheet="trouble",
             five=["Signaling can be perfect while RTP fails in one direction.", "Compare SDP connection addresses with the addresses that really send packets.", "NAT and a firewall are the common reasons.", "Codec mismatch usually fails the call, it does not half-succeed.", "Hold and resume is a second offer. Check it too."],
             core="One-way audio means one side's packets arrive and the other's do not, or one side is playing silence because the direction attribute is inactive or sendonly. Look at RTP counters and the SDP, then the firewall, then QoS. QoS rarely drops only one direction unless the return path is a different route.",
             example="The agent hears the caller. The caller hears nothing. The caller's SDP says a private address the carrier cannot route. The fix is the media address CUBE advertises, not a new codec list.",
             quiz=[("A 200 OK with SDP proves two-way audio.", "False.", ["True", "False"], "False")],
             sources=[RFC3550, RFC3264, CUBE], glossary=[("SDP c= line", "The address where media should be sent."), ("One-way audio", "Media in a single direction.")],
             config="Note both c= addresses and whether the interface can reach them.",
             trouble="If both RTP streams are present and the user still hears silence, look at codec payload types and mute, not the firewall.",
             bridge="SRTP without matching keys sounds like silence or a dropped call. Check whether both legs intended SRTP.",
             confirm=""),
    ]
    for row in rows:
        row.setdefault("confirm", "")
        row["eco"] = common_eco
    return rows
