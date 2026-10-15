#!/usr/bin/env python3
"""Build the flagship static studio from the richest readable sources.

Sources:
- Idea-pool study bank and diagrams on origin/merge/idea-pool-2026-10-14
- SIP, E911, dial-plan, QoS, CUBE, and migration study pages on
  origin/cursor/supercharge-2026-10-03
The deep campus in campus/ is left in place and linked.
"""

from __future__ import annotations

import html
import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "flagship"
POOL = "origin/merge/idea-pool-2026-10-14"
LEARN = "origin/cursor/supercharge-2026-10-03"
REPO = "https://github.com/cipher0x9/uc-lab-free-university-mesmerizing"
CONTACT = "https://cyphermonkeylabs.com/#contact"
PORT_DOC = "https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15/cucm_m_tcp-and-udp-port-usage-12-0.html"

NAV = [
    ("Home", "index.html"),
    ("Diagrams", "diagrams/index.html"),
    ("Flows", "flows/index.html"),
    ("Charts", "charts/index.html"),
    ("Cheat Codes", "cheats/index.html"),
    ("Play", "play/index.html"),
    ("Ecosystem", "ecosystem/index.html"),
    ("Downloads", "download.html"),
    ("Careers", "guide/interview.html"),
]

ORDER = [
    ("index.html", "Home"),
    ("diagrams/index.html", "Diagrams"),
    ("charts/index.html", "Charts"),
    ("tracks/index.html", "Tracks"),
    ("tracks/start.html", "Start here"),
    ("tracks/sip.html", "SIP and media"),
    ("tracks/cucm.html", "CUCM and CUBE"),
    ("tracks/cloud.html", "Webex and Teams"),
    ("tracks/ucce.html", "UCCE and PCCE"),
    ("tracks/ccaas.html", "CCaaS platforms"),
    ("tracks/e911.html", "Emergency calling"),
    ("tracks/qos.html", "Voice network and QoS"),
    ("tracks/migrate.html", "Migrations"),
    ("tracks/trouble.html", "Troubleshooting"),
    ("tracks/evidence.html", "Evidence habits"),
    ("tracks/design.html", "Design notes"),
    ("tracks/practice.html", "Practice"),
    ("tracks/reference.html", "Reference"),
    ("path.html", "Fundamentals to advanced"),
    ("flows/index.html", "Call-flow atlas"),
    ("flows/registration.html", "SIP registration"),
    ("flows/basic-call.html", "Basic call"),
    ("flows/sdp.html", "Offer and answer"),
    ("flows/hold.html", "Hold"),
    ("flows/transfer.html", "Transfer"),
    ("flows/early-media.html", "Early media"),
    ("flows/prack.html", "PRACK"),
    ("flows/session-refresh.html", "Session refresh"),
    ("flows/dial-plan.html", "CUCM dial plan"),
    ("flows/cube.html", "CUBE"),
    ("flows/pstn.html", "CUCM to PSTN"),
    ("flows/mra.html", "Mobile and Remote Access"),
    ("flows/srtp.html", "TLS and SRTP"),
    ("flows/options.html", "OPTIONS keepalive"),
    ("flows/one-way.html", "One-way audio"),
    ("flows/webex-lgw.html", "Webex local gateway"),
    ("flows/teams-dr.html", "Teams Direct Routing"),
    ("flows/migration.html", "CUCM to Webex Calling"),
    ("flows/e911.html", "Emergency call"),
    ("flows/qos.html", "QoS marks"),
    ("flows/ucce.html", "UCCE comprehensive"),
    ("flows/webex-cc.html", "Webex Contact Center"),
    ("flows/voicemail.html", "Unity Connection"),
    ("flows/hunt.html", "Hunt pilot"),
    ("flows/conference.html", "Conference"),
    ("flows/park.html", "Call park"),
    ("flows/shared-line.html", "Shared line"),
    ("flows/snr.html", "Single Number Reach"),
    ("flows/t38.html", "T.38 fax"),
    ("ports.html", "Ports and protocols"),
    ("ecosystem/index.html", "Ecosystem"),
    ("ecosystem/glossary.html", "Glossary"),
    ("ecosystem/mindmap.html", "Mind map"),
    ("ecosystem/wfm.html", "Workforce management"),
    ("ecosystem/recording.html", "Recording and QM"),
    ("ecosystem/emergency.html", "Emergency systems"),
    ("ecosystem/analytics.html", "Analytics"),
    ("ecosystem/crm.html", "CRM"),
    ("ecosystem/agents.html", "AI agents"),
    ("ecosystem/bridges.html", "Cross-platform bridges"),
    ("ecosystem/regions.html", "Regions"),
    ("licensing.html", "Licensing"),
    ("certifications.html", "Certifications"),
    ("roadmap.html", "Roadmap"),
    ("integrations.html", "Customer integrations"),
    ("quiz.html", "Quiz"),
    ("cards.html", "Flashcards"),
    ("cases.html", "Troubleshooting cases"),
    ("labs.html", "Interactive labs"),
    ("rooms.html", "Idea-pool diagrams"),
    ("guide/index.html", "Guide"),
    ("guide/architecture.html", "Architecture"),
    ("guide/deployment.html", "Deployment"),
    ("guide/configure.html", "Configuration"),
    ("guide/migration.html", "Migration checklist"),
    ("guide/playbooks.html", "Troubleshooting playbooks"),
    ("guide/firewall.html", "Firewall matrix"),
    ("guide/pstn.html", "PSTN and SIP trunking"),
    ("guide/security.html", "Security and compliance"),
    ("guide/interview.html", "Interview and career"),
    ("guide/whats-new.html", "What's new in 2026"),
    ("play/index.html", "Play"),
    ("play/ports-game.html", "Ports game"),
    ("play/map.html", "Flow map"),
    ("play/sandbox.html", "Call-flow sandbox"),
    ("play/daily.html", "Daily challenge"),
    ("play/badges.html", "Badges"),
    ("cheats/index.html", "Cheat codes"),
    ("cheats/ports.html", "Ports cheat sheet"),
    ("cheats/firewall.html", "Firewall cheat sheet"),
    ("cheats/call-flows.html", "Call-flow cheat sheet"),
    ("cheats/config.html", "Config checklist"),
    ("cheats/troubleshoot.html", "Troubleshooting cheat sheet"),
    ("cheats/glossary.html", "Glossary cheat sheet"),
    ("cheats/pstn.html", "PSTN cheat sheet"),
    ("cheats/e911.html", "Emergency cheat sheet"),
    ("cheats/qos.html", "QoS cheat sheet"),
    ("cheats/migration.html", "Cutover cheat sheet"),
    ("cheats/security.html", "Security cheat sheet"),
    ("cheats/wfm-recording.html", "WFM and recording cheat sheet"),
    ("cheats/flashcards.html", "Printable flashcards"),
    ("download.html", "Offline download"),
]


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def git_show(rev: str, path: str) -> str:
    return subprocess.check_output(["git", "show", f"{rev}:{path}"], text=True, errors="replace")


def git_bytes(rev: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{rev}:{path}"])


def extract_main(page: str) -> str:
    match = re.search(r"<main\b[^>]*>(.*)</main>", page, re.S | re.I)
    body = match.group(1) if match else ""
    body = body.replace("../svg/", "../assets/inherited/")
    body = body.replace('src="svg/', 'src="../assets/inherited/')
    repl = {
        "../dial-plan/cucm.html": "dial-plan.html",
        "../e911/design.html": "e911.html",
        "../migration/cucm-to-webex.html": "migration.html",
        "../qos/dscp.html": "qos.html",
        "../sbc/cube.html": "cube.html",
        "../sip/index.html": "index.html",
        "../flashcards.html": "../cards.html",
        "../pdf/index.html": "../download.html",
        "../index.html": "../index.html",
        "sdp-offer-answer.html": "sdp.html",
        "prack.html": "prack.html",
    }
    for old, new in repl.items():
        body = body.replace(f'href="{old}"', f'href="{new}"')
    return body


def crumbs_for(rel: str, title: str, root: str) -> str:
    parents = {
        "flows": ("Flows", "flows/index.html"),
        "diagrams": ("Diagrams", "diagrams/index.html"),
        "charts": ("Charts", "charts/index.html"),
        "cheats": ("Cheat Codes", "cheats/index.html"),
        "play": ("Play", "play/index.html"),
        "ecosystem": ("Ecosystem", "ecosystem/index.html"),
        "guide": ("Guide", "guide/index.html"),
        "tracks": ("Tracks", "tracks/index.html"),
    }
    items = [("Home", root + "index.html")]
    if rel != "index.html":
        folder = rel.split("/")[0] if "/" in rel else ""
        if folder in parents:
            label, href = parents[folder]
            if href != rel:
                items.append((label, root + href))
        items.append((title, ""))
    parts = []
    for index, (label, href) in enumerate(items):
        if href and index != len(items) - 1:
            parts.append(f'<li><a href="{esc(href)}">{esc(label)}</a></li>')
        else:
            parts.append(f'<li aria-current="page">{esc(label)}</li>')
    return f'<nav class="crumbs" aria-label="Breadcrumb"><ol>{"".join(parts)}</ol></nav>'


def chrome(rel: str, title: str, body: str, description: str) -> str:
    depth = rel.count("/")
    root = "../" * depth
    current = rel
    hub = [
        ("https://cyphermonkeylabs.com", "Studio"),
        ("https://linktr.ee/cyphermonkey", "Links"),
        (REPO, "GitHub · rate, comment, help"),
        ("https://dev.to/cyphermonkey", "DEV"),
        ("https://huggingface.co/Cypher0x9", "Hugging Face"),
        ("https://x.com/CypherMonkey", "X · @CypherMonkey"),
    ]
    hub_html = "".join(
        f'<a href="{esc(href)}">{esc(label)}</a>' for href, label in hub
    )
    i18n_nav = {
        "Home": "navHome",
        "Diagrams": "navDiagrams",
        "Flows": "navFlows",
        "Charts": "navCharts",
        "Cheat Codes": "navCheats",
        "Play": "navPlay",
        "Ecosystem": "navEco",
        "Downloads": "navDownloads",
        "Careers": "navCareers",
    }

    def marked(href: str) -> str:
        section = href.split("/")[0] if href.endswith("/index.html") else ""
        on_section = bool(section) and current.startswith(section + "/")
        if href == current or on_section:
            return ' aria-current="page"'
        return ""

    tabs = []
    sheet = []
    for label, href in NAV:
        abs_href = root + href
        here = marked(href)
        key = i18n_nav.get(label, "")
        link = f'<a href="{esc(abs_href)}"{here} data-i18n="{key}">{esc(label)}</a>'
        tabs.append(link)
        sheet.append(link)
    quick = [
        ("Learn", "path.html", "quickLearn"),
        ("Diagrams", "diagrams/index.html", "navDiagrams"),
        ("Play", "play/index.html", "navPlay"),
    ]
    quick_html = "".join(
        f'<a href="{esc(root + href)}"{marked(href)} data-i18n="{key}">{esc(label)}</a>'
        for label, href, key in quick
    )
    theme_html = """
        <div class="themes" role="radiogroup" aria-label="Theme">
          <button type="button" class="swatch-neon" data-theme-set="neon" aria-label="Neon" aria-checked="true"></button>
          <button type="button" class="swatch-holographic" data-theme-set="holographic" aria-label="Holographic" aria-checked="false"></button>
          <button type="button" class="swatch-cyberpunk" data-theme-set="cyberpunk" aria-label="Cyberpunk" aria-checked="false"></button>
          <button type="button" class="swatch-sunset" data-theme-set="sunset" aria-label="Sunset" aria-checked="false"></button>
          <button type="button" class="swatch-light" data-theme-set="light" aria-label="Light" aria-checked="false"></button>
        </div>"""
    lang_html = """
      <div class="lang-chips" role="radiogroup" aria-label="Language">
        <button type="button" data-lang="en" aria-pressed="true"><span aria-hidden="true">🇬🇧</span> EN</button>
        <button type="button" data-lang="es" aria-pressed="false"><span aria-hidden="true">🇪🇸</span> ES</button>
        <button type="button" data-lang="hi" aria-pressed="false"><span aria-hidden="true">🇮🇳</span> HI</button>
        <button type="button" data-lang="te" aria-pressed="false"><span aria-hidden="true">🇮🇳</span> TE</button>
        <button type="button" data-lang="fr" aria-pressed="false"><span aria-hidden="true">🇫🇷</span> FR</button>
        <button type="button" data-lang="de" aria-pressed="false"><span aria-hidden="true">🇩🇪</span> DE</button>
        <button type="button" data-lang="ja" aria-pressed="false"><span aria-hidden="true">🇯🇵</span> JA</button>
        <button type="button" data-lang="ar" aria-pressed="false"><span aria-hidden="true">🇸🇦</span> AR</button>
      </div>"""
    found = [i for i, (href, _) in enumerate(ORDER) if href == rel]
    if found:
        idx = found[0]
        prev_h, prev_l = ORDER[(idx - 1) % len(ORDER)]
        next_h, next_l = ORDER[(idx + 1) % len(ORDER)]
    else:
        prev_h, prev_l = ("cheats/index.html", "Cheat codes")
        next_h, next_l = ("download.html", "Offline download")

    def rel_to(target: str) -> str:
        if target.startswith("../"):
            return target
        return root + target

    sisters = [
        ("https://cipher0x9.github.io/ai-lab-free-university-mesmerizing/", "AI Lab"),
        ("https://cipher0x9.github.io/amazon-connect-lab-free-university-mesmerizing/", "Amazon Connect"),
        ("https://cipher0x9.github.io/microsoft-voice-cc-lab-free-university-mesmerizing/", "Microsoft Voice"),
        ("https://cipher0x9.github.io/five9-lab-free-university-mesmerizing/", "Five9"),
        ("https://cipher0x9.github.io/genesys-cloud-lab-free-university-mesmerizing/", "Genesys Cloud"),
        ("https://cipher0x9.github.io/nice-cxone-lab-free-university-mesmerizing/", "NICE CXone"),
        ("https://cipher0x9.github.io/sip-universe-lab-free-university-mesmerizing/", "SIP Universe"),
        (rel_to("path.html"), "Study path"),
    ]
    sister_html = "".join(f'<a class="card" href="{esc(href)}"><strong>{esc(label)}</strong></a>' for href, label in sisters)
    effects_html = ""
    if "data-effects" in body or rel in ("index.html", "diagrams/index.html", "charts/index.html"):
        effects_html = f'<script type="module" src="{root}assets/effects.js"></script>'
    confetti_html = ""
    if 'id="quiz"' in body:
        confetti_html = f'<script src="{root}assets/vendor/confetti.browser.js"></script>'
    crumb_html = crumbs_for(rel, title, root)
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="neon">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · UC Lab Free University</title>
<meta name="description" content="{esc(description)}">
<link rel="icon" href="{root}assets/icon.svg">
<link rel="manifest" href="{root}manifest.webmanifest">
<link rel="stylesheet" href="{root}assets/site.css">
<script>
try {{
  var params = new URLSearchParams(location.search);
  var t = params.get("theme") || localStorage.getItem("uc_flagship_theme");
  var ok = {{neon:1, holographic:1, cyberpunk:1, sunset:1, light:1}};
  if (ok[t]) document.documentElement.setAttribute("data-theme", t);
  var motion = localStorage.getItem("uc_flagship_motion");
  if (motion === "reduce" || motion === "allow") document.documentElement.setAttribute("data-motion", motion);
  var lang = localStorage.getItem("uc_flagship_lang");
  if (lang) document.documentElement.lang = lang;
  if (lang === "ar") document.documentElement.dir = "rtl";
}} catch (e) {{}}
</script>
</head>
<body data-root="{root}">
<a class="skip" href="#content" data-i18n="skip">Skip to content</a>
<header class="topbar">
  <div class="bar">
    <a class="brand" href="{root}index.html">
      <svg viewBox="0 0 36 36" aria-hidden="true"><rect width="36" height="36" rx="10" fill="#172033"/><path d="M6 22c4-8 8-8 12 0s8 8 12 0" fill="none" stroke="#7dcec4" stroke-width="2"/><circle cx="10" cy="14" r="2" fill="#f0b429"/><circle cx="18" cy="14" r="2" fill="#f4efe6"/><circle cx="26" cy="14" r="2" fill="#e07a5f"/></svg>
      <span><strong>UC Lab</strong><small data-i18n="brandSub">Free University</small></span>
    </a>
    <nav class="hub" aria-label="Studio">{hub_html}</nav>
    <div class="tools">
      {theme_html}
      <button type="button" class="btn mode-btn" data-i18n="mode">Light</button>
      <button type="button" class="btn motion-btn">Motion</button>
      <a class="btn dl" href="{root}download.html">Offline</a>
      <button type="button" class="btn settings-open" data-open="settings">Settings</button>
      <button type="button" class="btn menu-btn" data-open="menu" aria-expanded="false" aria-controls="siteMenu"><span class="burger" aria-hidden="true"></span><span data-i18n="menu">Menu</span></button>
    </div>
    <form class="site-search" role="search">
      <input id="siteSearch" type="search" placeholder="Search" aria-label="Search the lab" autocomplete="off" data-i18n-placeholder="searchPh">
      <div id="searchPop" class="search-pop" hidden></div>
    </form>
  </div>
  <nav class="tabs" aria-label="Lab">{''.join(tabs)}</nav>
  {lang_html}
  <p class="progress" id="visitProgress">Progress</p>
</header>
<main id="content" class="wrap">
{crumb_html}
{body}
</main>
<footer class="site-foot">
  <div class="wrap">
    <p class="kicker">Next</p>
    <p><a href="{esc(rel_to(prev_h))}">Previous · {esc(prev_l)}</a> · <a href="{esc(rel_to(next_h))}">Next · {esc(next_l)}</a> · <a href="{root}../campus/uc-lab-free-university.html">Deep campus · 580 sections</a></p>
    <div class="sister">{sister_html}</div>
    <p class="sig">CYPHER0X9</p>
    <p class="disc">Independent educational project, not affiliated with vendors. Trademarks belong to their owners. MIT code, CC BY-NC-SA content. Teaching models do not change a live system. Check the vendor's current document before you change production.</p>
    <p><a href="{REPO}">Rate, comment, or help</a> · <a href="{CONTACT}">Report a concern or takedown</a> · <a href="{CONTACT}">Work with us</a></p>
  </div>
</footer>
<div id="siteMenu" class="site-menu" hidden role="dialog" aria-modal="true" aria-labelledby="menuTitle">
  <div class="sheet-bar">
    <h2 id="menuTitle" data-i18n="menu">Menu</h2>
    <button type="button" class="btn sheet-close" data-close="menu" data-i18n="close">Close</button>
  </div>
  <div id="menuSearchSlot"></div>
  <nav class="sheet-nav" aria-label="Sections">{''.join(sheet)}</nav>
  <button type="button" class="btn settings-open sheet-settings" data-open="settings" data-i18n="settings">Settings</button>
</div>
<div id="settingsPanel" class="settings-sheet" hidden role="dialog" aria-modal="true" aria-labelledby="settingsTitle">
  <div class="sheet-card">
    <div class="sheet-bar">
      <h2 id="settingsTitle" data-i18n="settings">Settings</h2>
      <button type="button" class="btn sheet-close" data-close="settings" data-i18n="close">Close</button>
    </div>
    <p class="kicker">Theme</p>
    {theme_html}
    <p><button type="button" class="btn mode-btn" data-i18n="mode">Light</button></p>
    <p class="kicker">Language</p>
    {lang_html}
    <p class="kicker">Sound</p>
    <p><button type="button" class="btn sound-btn" aria-pressed="true">Sound on</button></p>
    <p class="kicker">Motion</p>
    <p><button type="button" class="btn motion-btn" aria-pressed="false">Motion on</button></p>
    <p class="kicker">Studio</p>
    <nav class="studio-links" aria-label="Studio">{hub_html}</nav>
  </div>
</div>
<div id="listenSheet" class="listen-sheet" hidden role="dialog" aria-modal="true" aria-labelledby="listenTitle">
  <div class="sheet-card">
    <div class="sheet-bar">
      <h2 id="listenTitle" data-i18n="quickListen">Listen</h2>
      <button type="button" class="btn sheet-close" data-close="listen" data-i18n="close">Close</button>
    </div>
    <p>Architect tour</p>
    <audio controls preload="none" src="{root}audio/architect-tour.mp3"></audio>
    <p>Architect practice</p>
    <audio controls preload="none" src="{root}audio/architect-practice.mp3"></audio>
  </div>
</div>
<nav class="quickbar" aria-label="Quick">
  {quick_html}
  <button type="button" class="quick-menu" data-open="menu" aria-expanded="false" aria-controls="siteMenu" data-i18n="menu">Menu</button>
  <button type="button" class="quick-listen" data-open="listen" aria-expanded="false" aria-controls="listenSheet" data-i18n="quickListen">Listen</button>
</nav>
<script src="{root}assets/search.js"></script>
<script src="{root}assets/bank.js"></script>
<script src="{root}assets/site.js"></script>
<script src="{root}assets/play.js"></script>
{effects_html}
{confetti_html}
</body>
</html>
"""


def write_page(rel: str, title: str, body: str, description: str) -> None:
    path = OUT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(chrome(rel, title, body, description), encoding="utf-8")


def sources(pairs: list[tuple[str, str]]) -> str:
    items = "".join(f'<li><a href="{esc(url)}">{esc(name)}</a></li>' for name, url in pairs)
    return f"<h2>Sources</h2><ul>{items}</ul>"


KIND = {
    "req": "#5eead4",
    "prov": "#fde047",
    "ok": "#86efac",
    "err": "#fb7185",
    "media": "#d8b4fe",
    "note": "#f0abfc",
}


_LADDER = 0


def ladder_block(title: str, actors: list[str], steps: list[tuple]) -> str:
    global _LADDER
    _LADDER += 1
    marker = f"arrow{_LADDER}"
    n = max(len(actors), 1)
    width = max(760, 200 * n)
    row = 46
    top = 70
    height = top + 20 + row * max(len(steps), 1)
    cols = [int((i + 0.5) * width / n) for i in range(n)]
    parts = [
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="{esc(title)}">',
        f"<defs><marker id='{marker}' markerWidth='8' markerHeight='8' refX='7' refY='3' orient='auto'><path d='M0,0 L8,3 L0,6 Z' fill='#5eead4'/></marker></defs>",
        f'<rect width="{width}" height="{height}" rx="16" fill="#0b0618"/>',
        f'<text x="20" y="24" font-family="Georgia, serif" font-size="16" fill="#f9a8d4">{esc(title)}</text>',
    ]
    for i, name in enumerate(actors):
        x = cols[i]
        parts.append(f'<text x="{x}" y="48" text-anchor="middle" font-family="Georgia, serif" font-size="15" fill="#f5f7ff">{esc(name)}</text>')
        parts.append(f'<line x1="{x}" y1="58" x2="{x}" y2="{height - 16}" stroke="#3b3260" stroke-width="2"/>')
    lis = []
    for i, step in enumerate(steps):
        src, dst, label, kind, cap = step
        y = top + i * row
        color = KIND.get(kind, "#0f6e62")
        x1, x2 = cols[src], cols[dst]
        dash = ' class="dash" stroke-dasharray="7 5"' if kind == "media" else ""
        parts.append(f'<g class="msg" data-cap="{esc(cap)}">')
        parts.append(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{color}" stroke-width="2.4" marker-end="url(#{marker})"{dash}/>')
        parts.append(f'<text x="{(x1 + x2) / 2:.1f}" y="{y - 8}" text-anchor="middle" font-size="13" font-family="Segoe UI, sans-serif" fill="{color}">{esc(label)}</text>')
        parts.append("</g>")
        lis.append(f"<li><strong>{esc(label)}</strong> — {esc(cap)}</li>")
    parts.append("</svg>")
    return (
        f'<figure class="ladder" data-ladder>{"".join(parts)}'
        '<div class="ladder-controls"><button type="button" class="btn" data-act="prev">Step back</button>'
        '<button type="button" class="btn" data-act="play">Play</button>'
        '<button type="button" class="btn" data-act="next">Step</button></div>'
        '<p class="ladder-cap muted"></p>'
        f"<ol>{''.join(lis)}</ol></figure>"
    )


def flow_shell(kicker: str, title: str, lede: str, level: str, diagrams: str, prose: str, cite: str, inherited_html: str) -> str:
    rail = (
        "<aside class='rail'><div class='paper'><p class='kicker'>Level</p>"
        f"<p class='num'>{esc(level)}</p><p class='muted'>Play the ladder, then read the inherited study card when this page has one.</p></div>"
        "<div class='paper'><p class='kicker'>Proof habit</p><p>Leg, identifier, counter, capture. A 200 OK is not two-way audio.</p></div></aside>"
    )
    inherited = ""
    if inherited_html.strip():
        inherited = "<h2>Study card carried forward</h2><div class='paper inherited'>" + inherited_html + "</div>"
    return (
        f"<p class='kicker'>{esc(kicker)}</p><h1>{esc(title)}</h1><p class='lede'>{esc(lede)}</p>"
        f"<div class='read'><div class='prose'>{diagrams}{prose}{cite}{inherited}</div>{rail}</div>"
    )


RFC3261 = ("RFC 3261", "https://www.rfc-editor.org/rfc/rfc3261")
RFC3264 = ("RFC 3264", "https://www.rfc-editor.org/rfc/rfc3264")


def flow_preview(flow: dict) -> str:
    ladder = flow["ladders"][0]
    actors = ladder["actors"][:4]
    steps = ladder["steps"][:6]
    n = max(len(actors), 1)
    width = 720
    row = 42
    height = 86 + row * max(len(steps), 1)
    cols = [int((i + 0.5) * width / n) for i in range(n)]
    parts = [
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="{esc(flow["title"])}">',
        "<style>.hop{stroke-dasharray:6 5;animation:dash 1.1s linear infinite}"
        ".pkt{animation:ride 2.8s linear infinite}"
        "@keyframes dash{to{stroke-dashoffset:-22}}"
        "@keyframes ride{to{offset-distance:100%}}</style>",
        f'<rect width="{width}" height="{height}" rx="18" fill="#0b0618"/>',
        f'<text x="18" y="28" fill="#f9a8d4" font-size="16" font-family="Georgia, serif">{esc(ladder["title"])}</text>',
    ]
    for i, name in enumerate(actors):
        x = cols[i]
        parts.append(f'<text x="{x}" y="54" text-anchor="middle" fill="#f5f7ff" font-size="14" font-family="Georgia, serif">{esc(name)}</text>')
        parts.append(f'<line x1="{x}" y1="64" x2="{x}" y2="{height - 14}" stroke="#3b3260" stroke-width="2"/>')
    for i, step in enumerate(steps):
        src, dst, label, kind, _cap = step
        y = 84 + i * row
        color = KIND.get(kind, "#5eead4")
        x1, x2 = cols[src], cols[dst]
        parts.append(f'<g class="msg" data-cap="{esc(label)}">')
        parts.append(f'<line class="hop" x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{color}" stroke-width="2.5"/>')
        parts.append(f'<text x="{(x1 + x2) / 2:.0f}" y="{y - 8}" text-anchor="middle" fill="{color}" font-size="13" font-family="Segoe UI, sans-serif">{esc(label)}</text>')
        parts.append(f'<circle class="pkt" r="5" fill="{color}" style="offset-path: path(\'M {x1} {y} H {x2}\'); offset-rotate: 0deg;"/>')
        parts.append("</g>")
    parts.append("</svg>")
    return "".join(parts)


def build_flows() -> None:
    flows = flow_defs()
    cards = []
    for flow in flows:
        inherited = ""
        if flow.get("pr2"):
            inherited = extract_main(git_show(LEARN, flow["pr2"]))
        diagrams = "".join(ladder_block(block["title"], block["actors"], block["steps"]) for block in flow["ladders"])
        body = flow_shell(flow["kicker"], flow["title"], flow["lede"], flow["level"], diagrams, flow["prose"], sources(flow["sources"]), inherited)
        write_page(f"flows/{flow['slug']}.html", flow["title"], body, flow["lede"])
        cards.append(flow)
    atlas = ["<p class='kicker'>Atlas</p><h1 data-i18n='pageFlows'>Call flows</h1>",
             f"<p class='lede'>{len(cards)} large ladders. Click a drawing to enlarge it, then play, pause, or step. The study card stays on the flow page.</p>",
             "<div class='flow-atlas'>"]
    for flow in cards:
        atlas.append(
            "<article class='tilt-card glass flow-card' data-tilt>"
            f"<button type='button' class='shot' data-why='{esc(flow['lede'])}'>{flow_preview(flow)}</button>"
            f"<h2><a href='{esc(flow['slug'])}.html'>{esc(flow['title'])}</a></h2>"
            f"<p class='muted'>{esc(flow['level'])} · {esc(flow['kicker'])}</p></article>"
        )
    atlas.append("</div>")
    write_page("flows/index.html", "Call flows", "".join(atlas), "Playable SIP, CUCM, cloud, and contact-center ladders.")


def flow_defs() -> list[dict]:
    s = sources
    return [
        dict(slug="registration", symbol="R", title="SIP registration", kicker="SIP · RFC 3261 §10", level="1 · Fundamentals",
             lede="REGISTER stores a binding. It does not create a call.",
             pr2="learn/sip/registration.html",
             sources=[RFC3261],
             ladders=[dict(title="Registrar challenge", actors=["Phone", "Registrar"], steps=[
                 (0, 1, "REGISTER", "req", "Request-URI is the registrar domain. Contact is the binding the phone wants stored."),
                 (1, 0, "401", "err", "WWW-Authenticate challenges the user. 401 is from the registrar, not a proxy."),
                 (0, 1, "REGISTER", "req", "The retry carries Authorization. The Call-ID stays with this registration dialog usage."),
                 (1, 0, "200 OK", "ok", "The binding is stored until the Contact expires. No media starts."),
             ])],
             prose="<p>A phone that cannot register never places a call. Read the realm, the nonce, and whether the second REGISTER was sent to the same registrar. A 407 would mean a proxy challenged the request, which is a different hop than 401.</p>"),
        dict(slug="basic-call", symbol="C", title="Basic call", kicker="SIP · RFC 3261", level="1 · Fundamentals",
             lede="The call is not up until ACK completes the 200 OK. Media often skips the proxy.",
             pr2="learn/sip/basic-call.html",
             sources=[RFC3261, RFC3264],
             ladders=[dict(title="Alice, proxy, Bob", actors=["Alice", "Proxy", "Bob"], steps=[
                 (0, 1, "INVITE", "req", "Early offer: SDP in the INVITE."),
                 (1, 2, "INVITE", "req", "The proxy forwards toward Bob. Record-Route keeps it on the path."),
                 (2, 1, "100", "prov", "100 Trying is hop-by-hop. Alice's 100 comes from the proxy, not from Bob."),
                 (1, 0, "100", "prov", "The proxy generates its own Trying."),
                 (2, 1, "180", "prov", "180 Ringing. A To tag starts an early dialog."),
                 (1, 0, "180", "prov", "Relayed toward Alice."),
                 (2, 1, "200", "ok", "SDP answer. The dialog is confirmed only after ACK."),
                 (1, 0, "200", "ok", "Follows the Via path back."),
                 (0, 1, "ACK", "req", "ACK for a 2xx is end-to-end, its own transaction."),
                 (1, 2, "ACK", "req", "Stays on the path when Record-Route is set."),
                 (0, 2, "RTP", "media", "Media can go direct. The proxy may never see it."),
                 (0, 1, "BYE", "req", "Either side ends the dialog."),
                 (2, 0, "200", "ok", "The BYE transaction completes."),
             ])],
             prose="<p>Separate signaling from media. A perfect ladder with a private address in SDP c= is still one-way audio. 100 is not ringing. 180 is not answer.</p>"),
        dict(slug="sdp", symbol="S", title="Offer and answer", kicker="SDP · RFC 3264", level="1 · Fundamentals",
             lede="One offer, one answer. A second offer before the answer is a protocol error.",
             pr2="learn/sip/sdp-offer-answer.html",
             sources=[RFC3264, ("RFC 4566", "https://www.rfc-editor.org/rfc/rfc4566")],
             ladders=[dict(title="Early offer", actors=["Offerer", "Answerer"], steps=[
                 (0, 1, "INVITE + SDP", "req", "The offer lists codecs the offerer can receive."),
                 (1, 0, "200 + SDP", "ok", "The answer picks a common codec. Port 0 rejects a stream."),
                 (0, 1, "ACK", "req", "The offer/answer completes with the 200, and ACK confirms the dialog."),
             ])],
             prose="<p>Delayed offer puts the first SDP in the 200, and the ACK carries the answer. Early offer puts SDP in the INVITE. CUCM trunks and CUBE dial-peers must agree which model the next hop requires. 488 means the SDP was rejected.</p>"),
        dict(slug="hold", symbol="H", title="Hold", kicker="SIP · RFC 3264", level="2 · Call control",
             lede="Hold is a new offer that changes direction, not a mute button on one phone.",
             pr2="learn/sip/hold.html",
             sources=[RFC3264, RFC3261],
             ladders=[dict(title="re-INVITE sendonly", actors=["Alice", "Bob"], steps=[
                 (0, 1, "re-INVITE", "req", "Same dialog. SDP a=sendonly, or inactive when neither side should send."),
                 (1, 0, "200", "ok", "Bob answers with recvonly, matching the direction."),
                 (0, 1, "ACK", "req", "The new offer is in force. Music, if any, is a local decision."),
                 (0, 1, "re-INVITE", "req", "Resume offers sendrecv again."),
                 (1, 0, "200", "ok", "Both directions restored."),
             ])],
             prose="<p>If the far side answers sendrecv to a sendonly offer, you still have a direction bug. Check both SDPs before you blame the network.</p>"),
        dict(slug="transfer", symbol="T", title="Transfer", kicker="REFER · RFC 3515 and 3891", level="2 · Call control",
             lede="Blind transfer refers the dialog. Attended transfer adds Replaces so the consult leg is taken over.",
             pr2="learn/sip/transfer.html",
             sources=[("RFC 3515", "https://www.rfc-editor.org/rfc/rfc3515"), ("RFC 3891", "https://www.rfc-editor.org/rfc/rfc3891")],
             ladders=[
                 dict(title="Blind transfer", actors=["Alice", "Bob", "Carol"], steps=[
                     (0, 1, "REFER", "req", "Refer-To is Carol. Alice asks Bob to call Carol."),
                     (1, 0, "202", "ok", "202 accepts the REFER. It does not mean Carol answered."),
                     (1, 2, "INVITE", "req", "Bob places the new call."),
                     (1, 0, "NOTIFY", "note", "The subscription tells Alice how the new call is going."),
                 ]),
                 dict(title="Attended transfer", actors=["Alice", "Bob", "Carol"], steps=[
                     (0, 2, "INVITE", "req", "Alice consults Carol on a second dialog."),
                     (2, 0, "200", "ok", "The consult is up."),
                     (0, 1, "REFER", "req", "Refer-To carries Replaces for the consult dialog."),
                     (1, 2, "INVITE", "req", "Bob invites Carol with Replaces. Carol drops Alice's consult."),
                 ]),
             ],
             prose="<p>202 is not a completed transfer. Read the NOTIFY body, or the new dialog, before you tell the user it worked.</p>"),
        dict(slug="early-media", symbol="E", title="Early media", kicker="RFC 3960 and 3261", level="2 · Call control",
             lede="183 with SDP is progress media. It is not answer, and it is not a confirmed dialog.",
             pr2="learn/sip/early-media.html",
             sources=[("RFC 3960", "https://www.rfc-editor.org/rfc/rfc3960"), RFC3261],
             ladders=[dict(title="183 Session Progress", actors=["Caller", "Callee"], steps=[
                 (0, 1, "INVITE", "req", "Early offer, so the callee can send media before answer."),
                 (1, 0, "183 + SDP", "prov", "Early media. Ringback or an announcement can be RTP, not a local tone."),
                 (1, 0, "RTP", "media", "One direction may start before 200."),
                 (1, 0, "200", "ok", "Answer. Cut-through must be checked again."),
             ])],
             prose="<p>If you treat 183 as answer, billing and recording start too early. If you ignore 183, the caller hears silence while the network is already playing an announcement.</p>"),
        dict(slug="prack", symbol="P", title="PRACK", kicker="RFC 3262", level="2 · Call control",
             lede="Reliable provisional responses need PRACK. A lost 183 otherwise never settles the early offer.",
             pr2="learn/sip/prack.html",
             sources=[("RFC 3262", "https://www.rfc-editor.org/rfc/rfc3262")],
             ladders=[dict(title="100rel", actors=["Caller", "Callee"], steps=[
                 (0, 1, "INVITE", "req", "Supported or Require includes 100rel."),
                 (1, 0, "183", "prov", "RSeq is set. The 183 is retransmitted until PRACK."),
                 (0, 1, "PRACK", "req", "RAck names the RSeq and the INVITE CSeq."),
                 (1, 0, "200", "ok", "That 200 is for the PRACK, not the call."),
             ])],
             prose="<p>Require: 100rel on a hop that cannot send PRACK fails the call. Match the requirement on both sides of a B2BUA before you change codecs.</p>"),
        dict(slug="session-refresh", symbol="⏱", title="Session refresh", kicker="RFC 4028", level="2 · Call control",
             lede="A session timer refreshes a dialog that would otherwise look up forever after a lost BYE.",
             pr2="learn/sip/session-refresh.html",
             sources=[("RFC 4028", "https://www.rfc-editor.org/rfc/rfc4028")],
             ladders=[dict(title="UPDATE refresh", actors=["Refresher", "Peer"], steps=[
                 (0, 1, "INVITE", "req", "Session-Expires and a refresher are negotiated."),
                 (1, 0, "200", "ok", "The peer agrees, or it rejects with 422 and a Min-SE."),
                 (0, 1, "UPDATE", "req", "At about half the interval the refresher sends UPDATE or re-INVITE."),
                 (1, 0, "200", "ok", "The session lives. If the refresh fails, the dialog is torn down."),
             ])],
             prose="<p>A 422 means your Session-Expires was below the peer's Min-SE. Raise it. Do not disable timers to hide a stuck call.</p>"),
        dict(slug="dial-plan", symbol="#", title="CUCM dial plan", kicker="Unified CM 15", level="2 · Call control",
             lede="A calling search space is an ordered list of partitions. The first partition that can match may hide a later, better pattern.",
             pr2="learn/dial-plan/cucm.html",
             sources=[("CUCM 15 system configuration", "https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15.html")],
             ladders=[dict(title="Analysis order", actors=["Phone", "Line CSS", "Partition", "Route"], steps=[
                 (0, 1, "Digits", "req", "The line CSS is searched before the device CSS."),
                 (1, 2, "Best match", "note", "Inside a partition, the closest match wins. Urgent priority can stop the wait for more digits."),
                 (2, 3, "Route", "ok", "A route pattern points at a route list, then a route group, then a trunk or gateway."),
                 (1, 0, "Reorder", "err", "No match in any partition of the CSS is a class-of-service miss, not a carrier failure."),
             ])],
             prose="<p>Standard Local Route Group picks the gateway from the calling device pool, so the same pattern can leave by a different gateway at each site. DNA is a model of analysis. A trunk trace is the call that actually happened.</p>"),
        dict(slug="cube", symbol="▣", title="CUBE", kicker="Cisco IOS XE border element", level="3 · Edge",
             lede="CUBE is a B2BUA. The inside dial-peer and the outside dial-peer are two legs, and each has its own offer.",
             pr2="learn/sbc/cube.html",
             sources=[("CUBE configuration guides", "https://www.cisco.com/c/en/us/support/unified-communications/unified-border-element/series.html")],
             ladders=[dict(title="Two dial-peers", actors=["CUCM", "CUBE", "ITSP"], steps=[
                 (0, 1, "INVITE", "req", "Incoming match: URI, then other inbound criteria. Dial-peer 0 means nothing you wrote matched."),
                 (1, 2, "INVITE", "req", "Outgoing match is destination-pattern, longest match, then lowest preference."),
                 (2, 1, "200 + SDP", "ok", "The carrier answer is not automatically the SDP CUCM sees."),
                 (1, 0, "200 + SDP", "ok", "Early-offer or delayed-offer is a property of this leg's dial-peer and SIP profile."),
             ])],
             prose="<p>OPTIONS keepalive can busy-out a server-group target. Cause 188 on a server-group usually means the target was busied out, not that the CSS missed.</p>"),
        dict(slug="pstn", symbol="↗", title="CUCM to the PSTN", kicker="Trunk · early offer", level="3 · Edge",
             lede="A national call is three signaling hops and two media negotiations.",
             pr2="",
             sources=[RFC3261, RFC3264, ("CUCM 15 port usage", PORT_DOC)],
             ladders=[dict(title="Phone, CUCM, CUBE, carrier", actors=["Phone", "CUCM", "CUBE", "ITSP"], steps=[
                 (0, 1, "INVITE", "req", "The phone's CSS finds the route pattern."),
                 (1, 2, "INVITE", "req", "CUCM may send a delayed offer toward CUBE."),
                 (2, 3, "INVITE", "req", "CUBE offers early toward the carrier when that dial-peer requires it."),
                 (3, 2, "180", "prov", "Alerting from the public network."),
                 (3, 2, "200", "ok", "Carrier SDP answer."),
                 (2, 1, "200", "ok", "If this 200 has no SDP, CUCM never receives the answer. That is a classic one-way call."),
                 (0, 3, "RTP", "media", "Media is between the negotiated addresses, not along the SIP hops."),
             ])],
             prose="<p>Trace both CUBE legs. Compare the SIP profile on the inside dial-peer before you open a carrier ticket. Signaling port 5060 or 5061 is not the RTP range.</p>"),
        dict(slug="mra", symbol="⌘", title="Mobile and Remote Access", kicker="Expressway", level="3 · Edge",
             lede="Outside clients discover the edge with _collab-edge._tls. Desk phones keep using _cisco-uds._tcp inside.",
             pr2="",
             sources=[("Expressway configuration examples", "https://www.cisco.com/c/en/us/support/unified-communications/expressway-series/products-configuration-examples-list.html")],
             ladders=[dict(title="Traversal registration", actors=["Jabber", "Exp-E", "Exp-C", "CUCM"], steps=[
                 (0, 1, "DNS SRV", "note", "_collab-edge._tls points at Expressway-E. A public _cisco-uds answer is the wrong record."),
                 (0, 1, "TLS", "req", "The edge certificate chain must be trusted by the client."),
                 (1, 2, "Traversal", "req", "Expressway-E is the traversal server. Expressway-C is the client."),
                 (2, 3, "REGISTER", "req", "CUCM still owns the registration. The edge does not replace the cluster."),
             ])],
             prose="<p>Office phones registering while laptops fail means the edge, DNS, or the certificate, not the line CSS. SIP on a new Expressway pair still has to be turned on for MRA.</p>"),
        dict(slug="srtp", symbol="🔒", title="TLS and SRTP", kicker="RFC 3711", level="3 · Edge",
             lede="TLS locks signaling. SRTP locks audio. One without the other is a half-locked call.",
             pr2="",
             sources=[("RFC 3711", "https://www.rfc-editor.org/rfc/rfc3711"), RFC3261],
             ladders=[dict(title="Secure hop", actors=["Phone", "CUCM", "CUBE"], steps=[
                 (0, 1, "SIP/TLS", "req", "5061. The certificate name must match the peer the phone dials."),
                 (1, 2, "SIP/TLS", "req", "The trunk security profile is a separate decision from the phone security profile."),
                 (0, 2, "SRTP", "media", "Crypto attributes in SDP. A successful TLS handshake does not encrypt RTP by itself."),
             ])],
             prose="<p>Mixed mode, CAPF, and the CTL are CUCM concerns. A 488 after you require SRTP usually means the far side offered RTP only.</p>"),
        dict(slug="options", symbol="?", title="OPTIONS keepalive", kicker="RFC 3261", level="3 · Edge",
             lede="OPTIONS asks a target if it is alive. It is not a call, and a timeout can take the target out of service.",
             pr2="",
             sources=[RFC3261],
             ladders=[dict(title="Keepalive", actors=["CUBE", "ITSP"], steps=[
                 (0, 1, "OPTIONS", "req", "Sent on an interval you configured, often per dial-peer or server-group."),
                 (1, 0, "200", "ok", "The target stays in service."),
                 (0, 1, "OPTIONS", "req", "The next probe, after the interval."),
                 (1, 0, "timeout", "err", "Repeated failure busies the target. New calls hunt to the next preference."),
             ])],
             prose="<p>If half your calls use the expensive carrier, check preference and whether keepalive has busied out the cheap one. Do not 'fix' it by adding a second identical destination-pattern at the same preference.</p>"),
        dict(slug="one-way", symbol="⇢", title="One-way audio", kicker="SDP c= and RTP", level="3 · Edge",
             lede="The ladder can be perfect while one RTP direction never arrives.",
             pr2="",
             sources=[RFC3264, ("RFC 3550", "https://www.rfc-editor.org/rfc/rfc3550")],
             ladders=[dict(title="Answer missing on one leg", actors=["CUCM", "CUBE", "ITSP"], steps=[
                 (0, 1, "INVITE", "req", "Delayed offer from CUCM."),
                 (1, 2, "INVITE + SDP", "req", "CUBE offers early to the provider."),
                 (2, 1, "200 + SDP", "ok", "The carrier's answer has a connection address."),
                 (1, 0, "200", "err", "The 200 toward CUCM has no SDP. CUCM has no address to send RTP to."),
             ])],
             prose="<p>Open both legs before you restart CallManager. A CSS miss does not connect a call and then drop one direction. QoS can still hurt a call that has two RTP streams. It does not explain a missing answer.</p>"),
        dict(slug="webex-lgw", symbol="W", title="Webex local gateway", kicker="Webex Calling", level="4 · Cloud",
             lede="A local gateway is a customer-managed border that connects a Webex Calling location to premises PSTN.",
             pr2="",
             sources=[("Webex Calling help", "https://help.webex.com/")],
             ladders=[dict(title="Location PSTN", actors=["Webex", "Local GW", "PSTN"], steps=[
                 (0, 1, "INVITE", "req", "The location's PSTN choice sends the call to the gateway registered for it."),
                 (1, 2, "INVITE", "req", "The gateway's dial-peer selects the carrier or the PBX."),
                 (2, 1, "200", "ok", "Answer and SDP."),
                 (0, 2, "RTP", "media", "Confirm the media addresses. Control Hub is not the RTP relay."),
             ])],
             prose="<p>Calling Plan has no local gateway. If the design says Calling Plan, do not troubleshoot a CUBE that is not on the path. A location pointed at the wrong gateway fails only that location.</p>"),
        dict(slug="teams-dr", symbol="T", title="Teams Direct Routing", kicker="Microsoft Teams Phone", level="4 · Cloud",
             lede="The certified SBC speaks SIP to Teams and to the carrier. OPTIONS health comes before the first INVITE.",
             pr2="",
             sources=[("Direct Routing plan", "https://learn.microsoft.com/en-us/microsoftteams/direct-routing-plan")],
             ladders=[dict(title="Direct Routing", actors=["Teams", "SBC", "Carrier"], steps=[
                 (1, 0, "OPTIONS", "req", "The SBC must answer Teams. A failed OPTIONS takes the trunk down before users dial."),
                 (0, 1, "INVITE", "req", "Teams sends the call for a number assigned to a Direct Routing voice route."),
                 (1, 2, "INVITE", "req", "The SBC's own dial plan picks the carrier."),
                 (2, 0, "RTP", "media", "Media bypass, when it is in the design, changes where RTP goes. It does not remove the SBC from signaling."),
             ])],
             prose="<p>Operator Connect and Calling Plan do not use your SBC. Read the user's PSTN connectivity type before you collect an SBC trace. The Florida Crystals story on the integrations page moved from Direct Routing to Operator Connect. Those are different paths.</p>"),
        dict(slug="migration", symbol="→", title="CUCM toward Webex Calling", kicker="Dual run", level="4 · Cloud",
             lede="Move a number only when identity, emergency location, and recording have a place to land.",
             pr2="learn/migration/cucm-to-webex.html",
             sources=[("Webex Calling help", "https://help.webex.com/"), RFC3261],
             ladders=[dict(title="Dual-run number", actors=["Old PBX", "Gateway", "Webex"], steps=[
                 (0, 1, "Still home", "note", "The number still registers on CUCM. Inbound stays there."),
                 (1, 2, "Canary", "req", "A pilot user moves. Outbound and inbound are tested, including emergency callback."),
                 (2, 1, "Rollback", "err", "The trigger to move the number back is written before the cut, not during it."),
             ])],
             prose="<p>A dial plan that globalizes to +E.164 on both sides is what makes the dual-run readable. Extension-only habits hide which system owns the call.</p>"),
        dict(slug="e911", symbol="!", title="Emergency call", kicker="Kari's Law · RAY BAUM", level="5 · Safety",
             lede="A connected 911 call with the wrong location is a failed emergency call.",
             pr2="learn/e911/design.html",
             sources=[("FCC MLTS 911 requirements", "https://www.fcc.gov/mlts-911-requirements"), ("Emergency Responder", "https://www.cisco.com/c/en/us/support/unified-communications/emergency-responder/series.html")],
             ladders=[dict(title="Dispatchable location", actors=["Phone", "CUCM", "CER", "PSAP"], steps=[
                 (0, 1, "911", "req", "Direct dial. Kari's Law does not allow a prefix to be required."),
                 (1, 2, "Route", "note", "CER, or the cloud location service, selects the ELIN or the dispatchable location."),
                 (2, 3, "INVITE", "req", "The calling number the PSAP sees must be the one that maps back to this site."),
                 (1, 0, "Notify", "ok", "On-site notification is a separate duty from completing the call."),
             ])],
             prose="<p>Callback that rings a headquarters receptionist failed the location, even though the first call connected. Test 933 where the carrier provides it, and keep 911 tests on the procedure your carrier allows.</p>"),
        dict(slug="qos", symbol="Q", title="QoS marks", kicker="RFC 4594 and enterprise practice", level="5 · Safety",
             lede="A DSCP mark does nothing until a queue treats it as priority. EF without a priority queue is a label.",
             pr2="learn/qos/dscp.html",
             sources=[("RFC 4594", "https://www.rfc-editor.org/rfc/rfc4594"), ("ITU-T G.114", "https://www.itu.int/rec/T-REC-G.114")],
             ladders=[dict(title="Mark, then queue", actors=["Phone", "Switch", "WAN"], steps=[
                 (0, 1, "RTP EF", "media", "Voice RTP is commonly marked EF, DSCP 46. Confirm the cluster service parameter."),
                 (0, 1, "SIP CS3", "req", "Many Cisco designs mark signaling CS3. RFC 4594 assigns signaling to CS5 and CS3 to broadcast video."),
                 (1, 2, "Queue", "note", "Trust the mark only from ports that should be trusted. Then give EF a priority queue."),
             ])],
             prose="<p>Do not copy RFC 4594 code points over a Cisco collaboration plan, or the reverse, without reading both. G.114's planning conversation is about one-way delay around 150 ms. It is not a license to add a deep jitter buffer.</p><p>G.711 at 20 ms is 80 kbit/s at layer 3: (160 bytes of payload + 40 bytes of IP, UDP, and RTP) × 8 × 50 packets. An 18-byte Ethernet header makes 87.2 kbit/s. The codec lab on the labs page uses that formula.</p>"),
        dict(slug="ucce", symbol="☎", title="UCCE comprehensive", kicker="Contact center", level="6 · Contact center",
             lede="The dialed number selects a call type. The call type is the report bucket and the script.",
             pr2="",
             sources=[("Unified Contact Center Enterprise", "https://www.cisco.com/c/en/us/support/customer-collaboration/unified-contact-center-enterprise/series.html")],
             ladders=[dict(title="Ingress to agent", actors=["Gateway", "CVP", "ICM", "Phone"], steps=[
                 (0, 1, "Inbound", "req", "The carrier call arrives at the ingress gateway and is handed to CVP."),
                 (1, 2, "Route request", "note", "ICM matches the dialed number to a call type, then a script."),
                 (2, 1, "Queue / IVR", "prov", "Treatment stays on CVP and VVB until the script selects an agent."),
                 (2, 3, "Reserve", "ok", "The agent desktop shows Reserved, then the phone must actually ring."),
             ])],
             prose="<p>Reserved with a silent phone is a device or CTI problem, not proof that the queue is empty. CUIC intervals follow the call type you scripted. A skill group is not a substitute bucket.</p>"),
        dict(slug="webex-cc", symbol="☁", title="Webex Contact Center", kicker="Cloud contact center", level="6 · Contact center",
             lede="The PSTN entry point, the flow, and the team are three different objects.",
             pr2="",
             sources=[("Webex help", "https://help.webex.com/")],
             ladders=[dict(title="Entry point to agent", actors=["PSTN", "Webex CC", "Flow", "Agent"], steps=[
                 (0, 1, "Call", "req", "The number is mapped to an entry point."),
                 (1, 2, "Flow", "note", "The flow gathers digits or intent, then queues."),
                 (2, 3, "Offer", "ok", "The agent desktop must be in an available state the flow is allowed to use."),
                 (3, 0, "Media", "media", "Browser agents bring WebRTC into the media path. That is why WebRTC stays in this lab."),
             ])],
             prose="<p>A flow that plays a prompt is not a queue. Confirm the task arrived in the team before you debug the agent's headset.</p>"),
        dict(slug="voicemail", symbol="✉", title="Unity Connection", kicker="Diversion", level="2 · Call control",
             lede="The forwarded call must tell Unity which mailbox to open. Otherwise every caller hears the opening greeting.",
             pr2="",
             sources=[("Unity Connection 15 administration", "https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/connection/15/administration/guide/b_15cucsag/b_15cucsag_chapter_0111.html")],
             ladders=[dict(title="Forward no answer", actors=["Caller", "CUCM", "Unity"], steps=[
                 (0, 1, "INVITE", "req", "The called phone rings."),
                 (1, 2, "INVITE", "req", "Forward on no answer. Diversion or history names the original called number."),
                 (2, 0, "Greeting", "ok", "Unity matches a mailbox. No match falls through to the opening greeting."),
             ])],
             prose="<p>A user who dials the pilot from their own phone and hears the opening greeting is a sign-in scope problem, not a missing codec. The call is a direct call, not a forwarded one.</p>"),
        dict(slug="hunt", symbol="⊛", title="Hunt pilot", kicker="Unified CM 15", level="2 · Call control",
             lede="The pilot, the line group, and the queue are three decisions. Logging out is not the same as being busy.",
             pr2="",
             sources=[("Hunt groups, CUCM 15", "https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/cucm_b_feature-configuration-guide-for-15/cucm_mp_a9c61bd0_00_accessing-hunt-groups-12-0.html"), ("Call queuing", "https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/cucm_b_feature-configuration-guide-for-15/cucm_m_configure-call-queuing.html")],
             ladders=[dict(title="Line group", actors=["Caller", "Pilot", "Member"], steps=[
                 (0, 1, "INVITE", "req", "The pilot pattern matches."),
                 (1, 2, "Offer", "req", "Distribution follows the line group's algorithm. HLog removes a member without deleting them."),
                 (2, 0, "180", "prov", "That member is ringing."),
                 (1, 0, "Queue", "note", "Queue when members are busy, if queuing is on. Logged-out behavior is a separate setting. Read the current chapter before you change it."),
             ])],
             prose="<p>The idea-pool hunt case on the cases page walks a logged-out queue. The chapter text and the lab model are both cited there. Do not treat this ladder as a substitute for the Release 15 page.</p>"),
        dict(slug="conference", symbol="+", title="Conference", kicker="Media resource", level="2 · Call control",
             lede="Ad-hoc conference hairpins media in a bridge. The bridge has a codec list and a capacity.",
             pr2="",
             sources=[("CUCM 15 media resources", "https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15.html")],
             ladders=[dict(title="Ad hoc", actors=["Alice", "CUCM", "Bridge", "Bob"], steps=[
                 (0, 1, "Conf", "req", "Alice presses conference and the first call is held."),
                 (0, 3, "Consult", "req", "The second party is dialed."),
                 (1, 2, "Allocate", "note", "The media resource group list on the phone must reach a bridge that speaks both codecs."),
                 (2, 3, "RTP", "media", "Both parties send RTP to the bridge, not to each other."),
             ])],
             prose="<p>A conference that drops to two-party audio failed the bridge, often on codec or on the media resource group list. DSP exhaustion shows up here and on transcoding.</p>"),
        dict(slug="park", symbol="P", title="Call park", kicker="CUCM feature", level="2 · Call control",
             lede="Park moves the call to a number anyone in the pickup group can retrieve. The original phone is no longer the anchor.",
             pr2="",
             sources=[("CUCM 15 feature configuration", "https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/cucm_b_feature-configuration-guide-for-15.html")],
             ladders=[dict(title="Park and retrieve", actors=["Alice", "CUCM", "Bob"], steps=[
                 (0, 1, "Park", "req", "CUCM places the call on a park number and tells Alice which one."),
                 (1, 0, "MOH", "media", "The waiting party hears music or silence from the park, not from Alice's handset."),
                 (2, 1, "Retrieve", "req", "Bob dials the park number. His CSS must be able to reach it."),
             ])],
             prose="<p>If retrieve reorders, look at the CSS of the retrieving phone before you look at the carrier.</p>"),
        dict(slug="shared-line", symbol="=", title="Shared line", kicker="CUCM line", level="2 · Call control",
             lede="Two phones with one directory number are one line appearance shared, not two extensions.",
             pr2="",
             sources=[("CUCM 15 system configuration", "https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15.html")],
             ladders=[dict(title="Remote in use", actors=["Caller", "Phone A", "Phone B"], steps=[
                 (0, 1, "INVITE", "req", "Both phones may ring, depending on the line settings."),
                 (1, 2, "Remote", "note", "When A answers, B shows remote in use. B is not a second call."),
                 (1, 0, "RTP", "media", "Audio is with A. Privacy and barge are explicit features, not the default media path."),
             ])],
             prose="<p>Busy behavior depends on the maximum calls and busy trigger on that shared line. A second call can still ring B while A is talking, until the busy trigger says otherwise.</p>"),
        dict(slug="snr", symbol="2", title="Single Number Reach", kicker="Mobility", level="2 · Call control",
             lede="SNR extends one enterprise number to a remote destination. The remote leg is another call, with its own timing.",
             pr2="",
             sources=[("CUCM 15 feature configuration", "https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/cucm_b_feature-configuration-guide-for-15.html")],
             ladders=[dict(title="Desk and mobile", actors=["Caller", "CUCM", "Mobile"], steps=[
                 (0, 1, "INVITE", "req", "The enterprise directory number is dialed."),
                 (1, 2, "INVITE", "req", "After the delay you configured, CUCM calls the remote destination."),
                 (2, 1, "200", "ok", "Answer on the mobile pulls the call. The desk phone stops."),
             ])],
             prose="<p>If the mobile rings and audio fails, treat the remote leg as a PSTN call: gateway, codec, and calling-number presentation. The desk phone's CSS is not the mobile's path.</p>"),
        dict(slug="t38", symbol="F", title="T.38 fax", kicker="RFC 3362", level="3 · Edge",
             lede="Fax can switch from audio to T.38 mid-call. A voice codec that looked fine will still fail a page.",
             pr2="",
             sources=[("RFC 3362", "https://www.rfc-editor.org/rfc/rfc3362")],
             ladders=[dict(title="Switchover", actors=["Fax", "CUBE", "Carrier"], steps=[
                 (0, 1, "INVITE", "req", "The call starts as audio so the fax tones can be heard."),
                 (0, 1, "re-INVITE", "req", "T.38 is offered when the tones are detected, if both legs allow the switch."),
                 (1, 2, "T.38", "media", "If the carrier stays on G.711 passthrough, do not force T.38 on only one leg."),
             ])],
             prose="<p>One leg on T.38 and the other on passthrough is a broken fax even when the SIP ladder shows 200 OK. NSE-based fax or passthrough for secure SIP lines is called out in the CUCM 15 gateway notes dated February 2026. Read that note before you change a secure fax trunk.</p>"),
    ]


def port_table() -> str:
    rows = [
        ("5060", "TCP and UDP", "SIP phone, gateway, and ICT", "Phones and gateways"),
        ("5061", "TCP", "SIP over TLS", "Phones and gateways"),
        ("2000", "TCP", "SCCP", "Phones and gateways"),
        ("2443", "TCP", "Secure SCCP", "Phones"),
        ("2427", "UDP", "MGCP control", "Gateways"),
        ("2428", "TCP", "MGCP backhaul", "Gateways"),
        ("1720", "TCP", "H.225 signaling", "H.323 gateways and ICT"),
        ("1719", "UDP", "H.225 RAS", "Gatekeeper"),
        ("69", "UDP", "TFTP", "Phones and gateways"),
        ("6970", "TCP", "HTTP firmware and configuration", "Phones and TFTP"),
        ("443, 8443", "TCP", "HTTPS administration and UDS", "Browsers and phones"),
        ("3804", "TCP", "CAPF, locally significant certificates", "Phones"),
        ("2748", "TCP", "CTI", "Applications"),
        ("2749", "TCP", "CTI over TLS", "JTAPI and TSP"),
        ("8443", "TCP", "AXL / SOAP", "Provisioning applications"),
        ("16384–32767", "UDP", "RTP and SRTP. CUCM itself uses 24576–32767", "Phones and gateways"),
        ("389, 636, 3268, 3269", "TCP", "LDAP and LDAPS, including global catalog", "Directory"),
        ("8090", "TCP", "Gateway recording HTTP", "Recording gateway"),
        ("443", "HTTPS", "Smart Licensing service to CSSM", "Cisco cloud"),
        ("123", "UDP", "NTP", "Time"),
        ("22", "TCP", "SFTP for a new subscriber and for DRS backups", "Cluster"),
        ("514", "UDP", "Syslog", "Endpoints to CUCM"),
        ("7501 / 7502", "TCP", "ILS certificate or password authentication", "Cluster"),
    ]
    body = []
    for port, proto, purpose, who in rows:
        body.append(f"<tr><td class='num'>{esc(port)}</td><td>{esc(proto)}</td><td>{esc(purpose)}</td><td>{esc(who)}</td></tr>")
    return f"""
<p class="kicker">Reference · CUCM 15</p>
<h1>Ports and protocols</h1>
<p class="lede">A working subset of the Release 15 port chapter. Ports move between releases. The chapter is the authority, and this table is a reading aid.</p>
<p><span class="num" id="portShown">{len(rows)}</span> rows shown · <span class="num">{len(rows)}</span> in the table</p>
<div class="filters"><input id="portQ" type="search" placeholder="Filter by port, protocol, or job" aria-label="Filter ports"></div>
<div class="table-scroll"><table id="portTable"><thead><tr><th>Port</th><th>Protocol</th><th>Job</th><th>Who</th></tr></thead><tbody>
{''.join(body)}
</tbody></table></div>
<div class="callout sand"><p>Multicast music-on-hold ports are whatever the administrator configured. The chapter does not publish one number for them. Ephemeral ports on the CUCM host are 32768–61000 and have to stay open for phones to remain registered.</p></div>
{sources([("CUCM 15 TCP and UDP port usage", PORT_DOC), RFC3261, ("RFC 3550", "https://www.rfc-editor.org/rfc/rfc3550")])}
"""


def ecosystem_pages() -> None:
    pages = {
        "index.html": ("Ecosystem", """
<p class="kicker">Around the call</p>
<h1 data-i18n="pageEco">Ecosystem</h1>
<p class="lede">Call control is the middle. Workforce management, recording, emergency location, analytics, CRM, and virtual agents fail in their own ways, and they fail the call when the identifier does not match.</p>
<div class="atlas">
<a class="card" href="glossary.html"><h2>Glossary</h2><p>Search 1,384 idea-pool cards and 88 cited study cards.</p></a>
<a class="card" href="mindmap.html"><h2>Mind map</h2><p>Unified CM in the middle. Sister systems on the rim.</p></a>
<a class="card" href="wfm.html"><h2>Workforce</h2><p>Intervals, adherence, and the agent id.</p></a>
<a class="card" href="recording.html"><h2>Recording and QM</h2><p>Fork the audio. A scorecard is not the audio.</p></a>
<a class="card" href="emergency.html"><h2>Emergency</h2><p>Location, callback, and on-site notice.</p></a>
<a class="card" href="analytics.html"><h2>Analytics</h2><p>Call type, CDR, CQD, Control Hub.</p></a>
<a class="card" href="crm.html"><h2>CRM</h2><p>Screen pop on a number the CRM can match.</p></a>
<a class="card" href="agents.html"><h2>AI agents</h2><p>Handoff, grounding, and a human escape.</p></a>
<a class="card" href="bridges.html"><h2>Bridges</h2><p>CUCM, Webex, Teams, and UCCE, plus hooks you can leave in a design.</p></a>
<a class="card glass iso-card" href="regions.html"><h2>Regions</h2><p>Cited residency and emergency rules. Coverage lists stay on the vendor page.</p></a>
</div>
"""),
        "wfm.html": ("Workforce management", f"""
<p class="kicker">Sister system</p>
<h1>Workforce management</h1>
<p class="lede">WFM forecasts staff from history and scores adherence from real-time state. It does not route the call.</p>
<div class="read"><div class="prose">
<h2>What you configure</h2>
<ul>
<li>The same agent identifier in the ACD and in the WFM feed. A display name is not an id.</li>
<li>Interval length, usually 15 or 30 minutes, aligned with the ACD's historical export.</li>
<li>Timezone of the contact center, not the timezone of the server that happened to receive the file.</li>
<li>Shrinkage, average handle time, and the queue or skill the forecast is for.</li>
</ul>
<h2>Troubleshooting</h2>
<ul>
<li>Adherence stuck on a talk state after the agent logged out: the logout event never arrived. Fix the feed, do not edit the agent's day by hand as the only record.</li>
<li>A missing interval after a CTI or API outage leaves a hole. The next interval does not backfill it unless the product says it does.</li>
<li>Skill ids that were renumbered in the ACD show up as a new queue. Yesterday's forecast no longer matches today's volume.</li>
</ul>
<p>Products engineers meet include NICE Workforce Management, Verint, Calabrio, Genesys workforce management, and Webex Workforce Optimization. The feed contract is in that product's current guide.</p>
{sources([("Webex help", "https://help.webex.com/"), ("UCCE", "https://www.cisco.com/c/en/us/support/customer-collaboration/unified-contact-center-enterprise/series.html")])}
</div><aside class="rail"><div class="paper"><p class="kicker">Proof</p><p>One interval file, one agent id, one logout event, one adherence row.</p></div></aside></div>
"""),
        "recording.html": ("Recording and quality management", f"""
<p class="kicker">Sister system</p>
<h1>Recording and quality management</h1>
<p class="lede">Recording captures audio. Quality management scores a sample of that audio. A report is not the recording.</p>
<div class="read"><div class="prose">
<h2>Where the fork happens</h2>
<ul>
<li>CUCM network-based recording can use the phone's built-in bridge or a gateway fork. The port chapter lists 8090/TCP for gateway recording HTTP between CUCM and the gateway.</li>
<li>SIPREC, RFC 7866, is the session-recording protocol an SBC can use to send a recording stream to a recorder.</li>
<li>Teams policy-based recording and Webex Calling recording follow those products' compliance settings. They are not the CUCM recording profile.</li>
</ul>
<h2>Troubleshooting</h2>
<ul>
<li>No audio file: recording profile not on the line, built-in bridge disabled, or the recorder rejected the codec.</li>
<li>One direction only: the forked stream has the same SDP bugs as a phone call. Capture the recorder leg.</li>
<li>QM has a score and the agent says the call never happened: you are looking at a different interaction id.</li>
</ul>
{sources([("RFC 7866", "https://www.rfc-editor.org/rfc/rfc7866"), ("CUCM 15 port usage", PORT_DOC)])}
</div><aside class="rail"><div class="paper"><p class="num">8090</p><p>Gateway recording HTTP in the CUCM 15 port chapter.</p></div></aside></div>
"""),
        "emergency.html": ("Emergency systems", f"""
<p class="kicker">Sister system</p>
<h1>Emergency location</h1>
<p class="lede">Kari's Law requires direct 911 and on-site notification from a multi-line telephone system. RAY BAUM'S Act is why the dispatchable location has to be good enough for a responder.</p>
<div class="read"><div class="prose">
<h2>Configuration</h2>
<ul>
<li>CUCM with Emergency Responder: switch-port discovery, ELIN, and a callback number that returns to the site that placed the call.</li>
<li>Webex Calling and Teams Phone: a location or emergency address on the user or the workspace, and a PSTN path that is allowed to carry 911. A Calling Plan location and a Direct Routing SBC do not share one setting.</li>
<li>Notification: a security desk, a screen, or a phone that rings when 911 is dialed. That path is tested separately from the PSAP call.</li>
</ul>
<h2>Troubleshooting</h2>
<ul>
<li>911 works for executives and reorders from the lobby: the lobby CSS lost the emergency partition. See the dial-plan lab.</li>
<li>The PSAP calls back and a headquarters receptionist answers: the ELIN or the emergency address is the headquarters one.</li>
<li>A prefix is required before 911: that design fails Kari's Law even if the call completes.</li>
</ul>
{sources([("FCC MLTS 911 requirements", "https://www.fcc.gov/mlts-911-requirements"), ("Emergency Responder", "https://www.cisco.com/c/en/us/support/unified-communications/emergency-responder/series.html")])}
</div><aside class="rail"><div class="callout rose"><p>Do not place a live 911 test because a lab page suggested it. Use the carrier's test number and the site's written procedure.</p></div></aside></div>
"""),
        "analytics.html": ("Analytics", f"""
<p class="kicker">Sister system</p>
<h1>Analytics</h1>
<p class="lede">Each platform has a counter. The counter is useless until you know which identifier it counts.</p>
<ul>
<li><strong>UCCE and CUIC.</strong> The call type is the report bucket. A skill-group report answers a different question.</li>
<li><strong>CUCM CDR and CMR.</strong> Call detail has to be enabled. A perfect SIP ladder with CDR off leaves no historical row.</li>
<li><strong>Teams Call Quality Dashboard.</strong> CQD is for media quality across calls, not for one user's SIP trace.</li>
<li><strong>Webex Control Hub.</strong> Calling analytics describe Webex Calling. They do not describe a CUCM phone that never moved.</li>
</ul>
<h2>Troubleshooting</h2>
<p>If the wallboard says zero calls and the agents are talking, the feed or the report filter is wrong. Check the interval timezone and the queue id before you restart anything.</p>
{sources([("Unified Intelligence Center", "https://www.cisco.com/c/en/us/support/customer-collaboration/unified-intelligence-center/series.html"), ("What is CQD", "https://learn.microsoft.com/en-us/microsoftteams/cqd-what-is-call-quality-dashboard")])}
"""),
        "crm.html": ("CRM", f"""
<p class="kicker">Sister system</p>
<h1>CRM screen pop</h1>
<p class="lede">The CTI event has to carry a number the CRM can find. Formatting is the usual break.</p>
<ul>
<li>Decide the system of record for the customer number: E.164, national, or an internal id.</li>
<li>Webex Contact Center, UCCE finesse gadgets, and Teams contact-center models each pop from their own event. A Salesforce record does not appear because CUCM rang a phone.</li>
<li>Screen pop misses: the ANI arrived as 10 digits and the CRM key is +E.164, or the CTI user cannot see the record.</li>
<li>Pop on the wrong record: two customers share a main number. The match rule needs more than ANI.</li>
</ul>
{sources([("Webex help", "https://help.webex.com/"), ("Teams contact center", "https://learn.microsoft.com/en-us/microsoftteams/teams-contact-center")])}
"""),
        "agents.html": ("AI agents", f"""
<p class="kicker">Sister system</p>
<h1>Virtual agents</h1>
<p class="lede">A virtual agent is an IVR with a model behind it. It still needs a queue, a failure prompt, and a person.</p>
<h2>Configuration</h2>
<ul>
<li>Intents or tasks the bot is allowed to finish, and an explicit handoff to a human queue.</li>
<li>A knowledge source you can name. If the bot cannot point at that source, it is guessing.</li>
<li>DTMF as a fallback when speech fails. Latency budget for the turn, because silence makes callers abandon.</li>
<li>A rule for transcripts and PII. Recording laws do not disappear because a model is in the path.</li>
</ul>
<h2>Troubleshooting</h2>
<ul>
<li>The bot never hands off: the confidence threshold or the flow has no escape edge.</li>
<li>The bot hands off immediately: the entry point is skipping the flow, or the language does not match.</li>
<li>The agent desktop gets the call and no context: the handoff payload did not include the interaction id.</li>
</ul>
<p>Webex Contact Center AI, Amazon Connect, and Google Contact Center AI are different products. Copy the idea of handoff and grounding. Copy the setting names from the current guide only.</p>
{sources([("Webex help", "https://help.webex.com/"), ("Teams contact center", "https://learn.microsoft.com/en-us/microsoftteams/teams-contact-center")])}
"""),
        "regions.html": ("Regions", """
<p class="kicker">Places</p>
<h1><span class="flag" aria-hidden="true">🇺🇸</span><span class="flag" aria-hidden="true">🇪🇺</span> Regions engineers actually name</h1>
<p class="lede">Only the rules below are cited. A country list for a calling plan changes. This page does not freeze one. Anything marked example is a teaching label, not coverage.</p>
<div class="region-grid">
<article class="card glass">
<h2><span class="flag" aria-hidden="true">🇺🇸</span> United States</h2>
<p>The FCC’s MLTS rules, from Kari’s Law and RAY BAUM’s Act section 506, require multi-line telephone systems to let a user dial 911 directly, to notify someone on site, and to send a dispatchable location. Read the current FCC page before you design a prefix or a location source.</p>
<p><a href="https://www.fcc.gov/mlts-911-requirements">FCC: Multi-line telephone systems</a></p>
</article>
<article class="card glass">
<h2><span class="flag" aria-hidden="true">🇪🇺</span> European Union</h2>
<p>Regulation (EU) 2016/679 is the GDPR. A recording of a person’s voice can be personal data. This lab does not invent a retention period or a member-state recording statute. Read the regulation and the recorder vendor’s current guide.</p>
<p><a href="https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32016R0679">EUR-Lex: Regulation (EU) 2016/679</a></p>
</article>
<article class="card glass">
<h2>Calling-plan countries</h2>
<p>Microsoft publishes which countries and regions have Calling Plans and Audio Conferencing. That list changes. Direct Routing is a customer SBC and is a different model. Cisco publishes Webex Calling availability in Webex Help. This lab links both and copies neither list.</p>
<p><a href="https://learn.microsoft.com/en-us/microsoftteams/country-and-region-availability-for-audio-conferencing-and-calling-plans">Microsoft: country and region availability</a></p>
<p><a href="https://help.webex.com/">Webex Help</a></p>
</article>
<article class="card glass">
<h2>Example numbering labels</h2>
<p><strong>Example, not a coverage claim.</strong> ITU-T E.164 is the international public numbering plan. Engineers say +1 for the North American plan, and they still have to confirm the national plan they are dialing. +91 and +81 below are examples of country codes in that plan. They are not a statement that any product in this lab sells PSTN there.</p>
<p><span class="flag" aria-hidden="true">🌐</span> +1 · +91 · +81 · <a href="https://www.itu.int/rec/T-REC-E.164/en">ITU-T E.164</a></p>
</article>
</div>
"""),
        "bridges.html": ("Bridges", f"""
<p class="kicker">Cross platform</p>
<h1>Bridges and future hooks</h1>
<p class="lede">These are the paths that already exist. The hooks at the bottom are design seams, not features this lab turns on in your network.</p>
<div class="table-scroll"><table><thead><tr><th>From</th><th>To</th><th>Bridge</th><th>Proof</th></tr></thead><tbody>
<tr><td>CUCM</td><td>PSTN</td><td>SIP trunk to CUBE or a gateway</td><td>Both dial-peers and both SDPs</td></tr>
<tr><td>CUCM</td><td>Webex Calling</td><td>Local gateway, or a migration of the number</td><td>The location's PSTN choice and one test call</td></tr>
<tr><td>CUCM</td><td>UCCE</td><td>Route point, dialed number, JTAPI</td><td>Call type in the script, phone rings</td></tr>
<tr><td>Teams</td><td>PSTN</td><td>Calling Plan, Operator Connect, or Direct Routing</td><td>The user's connectivity type, then OPTIONS if it is an SBC</td></tr>
<tr><td>Teams</td><td>A contact center</td><td>Connect, Extend, or Unify, as Microsoft documents them</td><td>The certified model, not a guessed port</td></tr>
<tr><td>Webex Contact Center</td><td>Teams</td><td>The published Webex Contact Center app for Teams</td><td>A consult between agent and a Teams user, with an interaction id</td></tr>
</tbody></table></div>
<h2>Hooks to leave in a design</h2>
<ul>
<li><strong>SIPREC</strong> on the SBC, so a future recorder has a defined leg. RFC 7866.</li>
<li><strong>CTI or the platform's webhook</strong> with a stable interaction id, so CRM and WFM can subscribe later.</li>
<li><strong>A test number</strong> that is not 911, routed like production, so each bridge has a canary.</li>
<li><strong>+E.164</strong> on every boundary, so the next system does not invent its own habit.</li>
</ul>
<p>None of these hooks place a call by themselves. They are names of interfaces you can write into a design review.</p>
{sources([("Teams contact center", "https://learn.microsoft.com/en-us/microsoftteams/teams-contact-center"), ("Direct Routing", "https://learn.microsoft.com/en-us/microsoftteams/direct-routing-plan"), ("RFC 7866", "https://www.rfc-editor.org/rfc/rfc7866")])}
"""),
    }
    for name, (title, body) in pages.items():
        write_page(f"ecosystem/{name}", title, body, title)


def mindmap_page(diagrams: list[Path]) -> None:
    inherited = ""
    for path in diagrams:
        if path.name == "mindmap.svg":
            inherited = f'<figure class="ladder"><img src="../assets/pool/ecosystem/mindmap.svg" alt="Idea-pool ecosystem drawing with Unified CM in the center"></figure>'
    body = f"""
<p class="kicker">Map</p>
<h1>Mind map</h1>
<p class="lede">Unified CM sits in the middle of the on-premises system. Sister systems and cloud platforms sit on the rim. Choose a node.</p>
<figure class="ladder mind"><svg viewBox="0 0 980 640" role="img" aria-label="Ecosystem mind map">
<rect width="980" height="640" rx="24" fill="#172033"/>
<text x="36" y="40" fill="#f4efe6" font-family="Georgia, serif" font-size="22">Collaboration ecosystem</text>
<a href="../flows/pstn.html"><circle cx="490" cy="320" r="78" fill="#0f6e62"/><text x="490" y="316" text-anchor="middle" fill="#f4fffc" font-size="16">Unified CM</text><text x="490" y="336" text-anchor="middle" fill="#d7fff8" font-size="12">call control</text></a>
<a href="wfm.html"><rect x="40" y="90" width="180" height="54" rx="10" fill="#1d1812" stroke="#f5b942"/><text x="130" y="122" text-anchor="middle" fill="#f8f1df">Workforce</text></a>
<a href="recording.html"><rect x="40" y="180" width="180" height="54" rx="10" fill="#1d1812" stroke="#f5b942"/><text x="130" y="212" text-anchor="middle" fill="#f8f1df">Recording / QM</text></a>
<a href="emergency.html"><rect x="40" y="270" width="180" height="54" rx="10" fill="#1d1812" stroke="#ff8fa3"/><text x="130" y="302" text-anchor="middle" fill="#f8f1df">Emergency</text></a>
<a href="analytics.html"><rect x="40" y="360" width="180" height="54" rx="10" fill="#1d1812" stroke="#7dcec4"/><text x="130" y="392" text-anchor="middle" fill="#f8f1df">Analytics</text></a>
<a href="crm.html"><rect x="40" y="450" width="180" height="54" rx="10" fill="#1d1812" stroke="#7dcec4"/><text x="130" y="482" text-anchor="middle" fill="#f8f1df">CRM</text></a>
<a href="agents.html"><rect x="40" y="540" width="180" height="54" rx="10" fill="#1d1812" stroke="#c4b5fd"/><text x="130" y="572" text-anchor="middle" fill="#f8f1df">AI agents</text></a>
<a href="../flows/webex-lgw.html"><rect x="760" y="120" width="180" height="54" rx="10" fill="#102033" stroke="#5eead4"/><text x="850" y="152" text-anchor="middle" fill="#e8eef8">Webex Calling</text></a>
<a href="../flows/teams-dr.html"><rect x="760" y="220" width="180" height="54" rx="10" fill="#102033" stroke="#5eead4"/><text x="850" y="252" text-anchor="middle" fill="#e8eef8">Teams Phone</text></a>
<a href="../flows/ucce.html"><rect x="760" y="320" width="180" height="54" rx="10" fill="#102033" stroke="#5eead4"/><text x="850" y="352" text-anchor="middle" fill="#e8eef8">UCCE</text></a>
<a href="../flows/cube.html"><rect x="760" y="420" width="180" height="54" rx="10" fill="#102033" stroke="#f0a36a"/><text x="850" y="452" text-anchor="middle" fill="#e8eef8">CUBE / SBC</text></a>
<a href="bridges.html"><rect x="760" y="520" width="180" height="54" rx="10" fill="#102033" stroke="#f0a36a"/><text x="850" y="552" text-anchor="middle" fill="#e8eef8">Bridges</text></a>
</svg></figure>
<h2>Drawing carried from the idea pool</h2>
{inherited}
<p class="muted">The inherited drawing uses the pool's own labels. The map above is the flagship navigation.</p>
"""
    write_page("ecosystem/mindmap.html", "Mind map", body, "Ecosystem mind map linking sister systems and call platforms.")


def other_pages(bank: dict, pool_images: list[str]) -> None:
    qn = len(bank["questions"])
    cn = len(bank["cards"])
    pn = len(bank["pr2Cards"])
    sn = len(bank["scenarios"])
    write_page("index.html", "UC Lab", f"""
<p class="kicker">Flagship studio · v21 campus underneath</p>
<h1>Voice, UC, and contact center. One lab.</h1>
<p class="lede">A static studio for people who run calls. Fundamentals first, then the edge, the cloud, and the systems around the agent. The 580-section campus is still here when you want the long library.</p>
<div class="hero">
  <div class="hero-copy">
    <div class="actions"><a class="btn dl" href="path.html">Start the path</a><a class="btn" href="flows/basic-call.html">Play a ladder</a><a class="btn" href="../campus/uc-lab-free-university.html">Open the deep campus</a></div>
    <p class="muted">Five themes. Motion can be turned off. Nothing is loaded from a CDN.</p>
  </div>
  <div class="stage">
    <svg class="float-art float-a" viewBox="0 0 80 120" aria-hidden="true"><rect x="18" y="8" width="44" height="104" rx="8" fill="#f4efe6"/><rect x="26" y="20" width="28" height="40" rx="2" fill="#172033"/><circle cx="40" cy="78" r="8" fill="#0f6e62"/></svg>
    <svg class="float-art float-b" viewBox="0 0 120 70" aria-hidden="true"><rect x="8" y="16" width="104" height="40" rx="8" fill="#0f6e62"/><circle cx="28" cy="36" r="6" fill="#f5b942"/><circle cx="48" cy="36" r="6" fill="#f4efe6"/><circle cx="68" cy="36" r="6" fill="#e07a5f"/><path d="M78 36h24" stroke="#f4efe6" stroke-width="3"/></svg>
    <canvas id="fabric" aria-label="Rotating diagram of a phone, CUCM, CUBE, the PSTN, and Webex Calling"></canvas>
  </div>
</div>
<div class="toggles" aria-label="Break a link in the diagram">
  <label><input type="checkbox" data-break="phone-cucm"> Phone–CUCM down</label>
  <label><input type="checkbox" data-break="cucm-cube"> Trunk down</label>
  <label><input type="checkbox" data-break="cube-pstn"> Carrier down</label>
  <label><input type="checkbox" data-break="cucm-webex"> Webex path down</label>
</div>
<section class="stats" aria-label="Counts">
  <div class="stat"><span class="num">29</span><span class="label">Playable flows</span></div>
  <div class="stat"><span class="num">{qn}</span><span class="label">Quiz questions</span></div>
  <div class="stat"><span class="num">{cn + pn}</span><span class="label">Flashcards</span></div>
  <div class="stat"><span class="num">{sn}</span><span class="label">Branching cases</span></div>
  <div class="stat"><span class="num">580</span><span class="label">Campus sections</span></div>
  <div class="stat"><span class="num">5</span><span class="label">Themes</span></div>
</section>
<h2>Guide, play, and cheat codes</h2>
<div class="atlas">
<a class="card" href="guide/index.html"><h2>Guide</h2><p>Architecture, deployment, cutover, security, interviews.</p></a>
<a class="card" href="play/index.html"><h2>Play</h2><p>Ports game, flow map, sandbox, daily challenge, badges.</p></a>
<a class="card" href="cheats/index.html"><h2>Cheat codes</h2><p>One-page sheets, flashcard files, and the offline zip.</p></a>
</div>
<h2>From fundamentals to the agent desktop</h2>
<div class="path">
  <a href="flows/registration.html"><span class="stepnum">01</span><strong>Signaling</strong><p class="muted">REGISTER, INVITE, SDP</p></a>
  <a href="flows/dial-plan.html"><span class="stepnum">02</span><strong>Dial plan</strong><p class="muted">CSS, partition, route</p></a>
  <a href="flows/cube.html"><span class="stepnum">03</span><strong>Edge</strong><p class="muted">CUBE, MRA, SRTP</p></a>
  <a href="flows/webex-lgw.html"><span class="stepnum">04</span><strong>Cloud</strong><p class="muted">Webex and Teams</p></a>
  <a href="flows/e911.html"><span class="stepnum">05</span><strong>Safety</strong><p class="muted">E911 and QoS</p></a>
  <a href="ecosystem/index.html"><span class="stepnum">06</span><strong>Ecosystem</strong><p class="muted">WFM, QM, CRM, AI</p></a>
</div>
<h2>A short clip of an INVITE</h2>
<p>The GIF is generated in this repo. The animated drawing next to it is the same hop, drawn as SVG so it stays sharp.</p>
<img class="clip" src="assets/clips/invite.gif" alt="Animation of an INVITE moving from a phone toward a proxy and a 100 Trying coming back">
<img class="clip" src="assets/clips/invite.svg" alt="Animated SVG of the same INVITE and 100 Trying">
<h2>Real numbers you will reuse</h2>
<div class="stats">
  <div class="stat"><span class="num">5060</span><span class="label">SIP</span></div>
  <div class="stat"><span class="num">5061</span><span class="label">SIP TLS</span></div>
  <div class="stat"><span class="num">46</span><span class="label">DSCP for EF</span></div>
  <div class="stat"><span class="num">150</span><span class="label">ms planning delay</span></div>
  <div class="stat"><span class="num">87.2</span><span class="label">kbit/s G.711 + Ethernet</span></div>
  <div class="stat"><span class="num">8090</span><span class="label">Gateway recording</span></div>
</div>
""", "Flagship UC lab with call flows, ecosystem, quiz, and the deep campus."),
    write_page("path.html", "Path", """
<p class="kicker">Sequence</p>
<h1>Fundamentals to advanced</h1>
<p class="lede">Do not start at the contact center. A queue makes no sense until you can say which leg failed.</p>
<ol>
<li><a href="flows/registration.html">Registration</a> and the <a href="flows/basic-call.html">basic call</a>, then <a href="flows/sdp.html">offer and answer</a>.</li>
<li><a href="flows/dial-plan.html">Dial plan</a>, <a href="flows/hunt.html">hunt</a>, <a href="flows/hold.html">hold</a>, <a href="flows/transfer.html">transfer</a>, <a href="flows/voicemail.html">voicemail</a>.</li>
<li><a href="flows/cube.html">CUBE</a>, <a href="flows/pstn.html">PSTN</a>, <a href="flows/mra.html">MRA</a>, <a href="flows/one-way.html">one-way audio</a>, <a href="flows/srtp.html">SRTP</a>.</li>
<li><a href="flows/webex-lgw.html">Webex local gateway</a>, <a href="flows/teams-dr.html">Teams Direct Routing</a>, <a href="flows/migration.html">migration</a>.</li>
<li><a href="flows/e911.html">Emergency</a> and <a href="flows/qos.html">QoS</a>.</li>
<li><a href="flows/ucce.html">UCCE</a>, <a href="flows/webex-cc.html">Webex Contact Center</a>, then the <a href="ecosystem/index.html">ecosystem</a>.</li>
<li><a href="cases.html">Cases</a>, the <a href="quiz.html">quiz</a>, and the <a href="../campus/uc-lab-free-university.html">580-section campus</a>.</li>
</ol>
<p>Certification names and dates are on the <a href="certifications.html">certifications</a> page. They are a map of exams, not a promise that this lab covers an exam blueprint.</p>
""", "Study order from SIP fundamentals to contact-center ecosystems.")

    cases = []
    for scenario in bank["scenarios"]:
        cases.append(
            f"<li><button type='button' class='btn' data-case='{esc(scenario['id'])}'>{esc(scenario['title'])}</button> "
            f"<span class='muted'>{esc(scenario.get('blurb') or '')}</span></li>"
        )
    write_page("cases.html", "Cases", f"""
<p class="kicker">Idea pool</p>
<h1>Troubleshooting cases</h1>
<p class="lede"><span class="num">{sn}</span> branching cases. Each one starts from a symptom. Wrong branches say why they are wrong and send you back.</p>
<div class="read"><div class="prose"><ol>{''.join(cases)}</ol></div>
<aside class="rail"><div id="casePlayer" class="paper"><p>Choose a case.</p></div></aside></div>
""", "29 branching troubleshooting cases from the idea pool.")

    write_page("quiz.html", "Quiz", f"""
<p class="kicker">Scored in this browser</p>
<h1>Quiz</h1>
<p class="lede">The bank has <span class="num" id="quizTotal">{qn}</span> questions from the idea-pool study set. The correct choice is the reason line that came with the question. Nothing was added to fill a blank why.</p>
<div id="quiz">
<label>Track <select id="quizTrack"><option value="all">All tracks</option></select></label>
<div id="quizCard" class="paper"></div>
<p id="quizScore">0 correct · 0 answered · {qn} in the bank</p>
<button type="button" class="btn" id="quizNext">Next question</button>
</div>
""", "Scored quiz using the idea-pool question bank.")

    write_page("cards.html", "Flashcards", f"""
<p class="kicker">Two decks</p>
<h1>Flashcards</h1>
<p class="lede"><span class="num">{cn}</span> idea-pool cards and <span class="num">{pn}</span> cited study cards. Sentences marked TODO-verify are unfinished counts from the source. They are not guesses filled in here.</p>
<div id="cards">
<label>Deck <select id="cardDeck"><option value="pool">Idea pool · {cn}</option><option value="study">Cited study cards · {pn}</option></select></label>
<div id="cardFace" class="cardface" role="button" tabindex="0">Loading the deck.</div>
<p id="cardCounts">Known 0 · Remaining {cn} · Deck {cn}</p>
<div class="actions"><button type="button" class="btn" id="cardKnow">Known</button><button type="button" class="btn" id="cardAgain">Again</button></div>
</div>
""", "Flashcards from the idea pool and the cited SIP study set.")

    write_page("labs.html", "Labs", """
<p class="kicker">Teaching models</p>
<h1>Labs</h1>
<p class="lede">These run in the browser. They do not log in to a cluster.</p>
<div class="lab-grid">
<section class="paper">
<h2>Codec bandwidth</h2>
<p>Layer 3 is (payload + 40) × 8 × (1000 / ptime) / 1000. Add the layer-2 header you choose.</p>
<form id="codecForm">
<label class="field">Payload bytes <input id="payload" type="number" value="160" min="1"></label>
<label class="field">ptime ms <input id="ptime" type="number" value="20" min="1"></label>
<label class="field">L2 bytes <input id="l2" type="number" value="18" min="0"></label>
</form>
<p id="codecOut" class="num"></p>
<p class="muted">G.711 at 20 ms with an 18-byte Ethernet header is 87.2 kbit/s.</p>
</section>
<section class="paper">
<h2>CSS order</h2>
<p>Move Emergency above PSTN, then dial 911. Inside a partition the best match wins. Across partitions, order is searched as you list it. A 9.@ in an earlier partition can consume 911.</p>
<div id="cssLab">
<ol id="cssOrder">
<li data-part="PSTN">PSTN · 9.@ <button type="button" data-move="PSTN" data-dir="-1">Up</button> <button type="button" data-move="PSTN" data-dir="1">Down</button></li>
<li data-part="Emergency">Emergency · 911 <button type="button" data-move="Emergency" data-dir="-1">Up</button> <button type="button" data-move="Emergency" data-dir="1">Down</button></li>
<li data-part="Internal">Internal · directory numbers <button type="button" data-move="Internal" data-dir="-1">Up</button> <button type="button" data-move="Internal" data-dir="1">Down</button></li>
</ol>
<label>Digits <input id="cssDial" value="911" aria-label="Digits to test"></label>
<p id="cssOut"></p>
</div>
</section>
<section class="paper">
<h2>SIP response</h2>
<label>Code <input id="sipCode" inputmode="numeric" placeholder="180" aria-label="SIP response code"></label>
<p id="sipOut">Type a code from the list.</p>
<ul>
<li id="sip-100" data-mean="100 Trying is hop-by-hop. It is not ringing.">100 Trying</li>
<li id="sip-180" data-mean="180 Ringing means alerting started. A To tag can create an early dialog.">180 Ringing</li>
<li id="sip-183" data-mean="183 Session Progress often carries early media. It is not answer.">183 Session Progress</li>
<li id="sip-200" data-mean="200 OK accepts the request. For INVITE, the dialog is confirmed when ACK completes.">200 OK</li>
<li id="sip-202" data-mean="202 Accepted takes a REFER. It does not mean the transferred call was answered.">202 Accepted</li>
<li id="sip-401" data-mean="401 Unauthorized is a registrar challenge. The next REGISTER carries Authorization.">401 Unauthorized</li>
<li id="sip-407" data-mean="407 is a proxy challenge. It is not the same hop as 401.">407 Proxy Authentication Required</li>
<li id="sip-486" data-mean="486 Busy Here is a final response from the user agent.">486 Busy Here</li>
<li id="sip-487" data-mean="487 Request Terminated. The request was cancelled or otherwise given up.">487 Request Terminated</li>
<li id="sip-488" data-mean="488 Not Acceptable Here. The SDP was rejected.">488 Not Acceptable Here</li>
<li id="sip-503" data-mean="503 Service Unavailable is a server failure, not a user busy.">503 Service Unavailable</li>
</ul>
</section>
<section class="paper">
<h2>One-way checklist</h2>
<ol>
<li>Is there a 200 OK on both SIP legs?</li>
<li>Does each 200 that should carry an answer actually contain SDP?</li>
<li>Is c= an address the other side can route to?</li>
<li>Are RTP packets present in both directions after ACK?</li>
<li>Only then look at DSCP and the jitter buffer.</li>
</ol>
</section>
</div>
""", "Browser labs for bandwidth, CSS order, and SIP codes.")

    write_page("licensing.html", "Licensing", f"""
<p class="kicker">Commercial names change</p>
<h1>Licensing</h1>
<p class="lede">A license error and a route error look different. Check which one you have before you touch a dial-peer.</p>
<h2>Unified CM</h2>
<p>Release 15 uses Cisco Smart Licensing. The port chapter says the Smart Licensing service sends usage to Cisco Smart Software Manager on 443/HTTPS. Transport details for a specific SU belong in that SU's release notes. This page does not pick Call Home or Smart Transport for you.</p>
<h2>Webex Calling</h2>
<p>Subscriptions are assigned to people and workspaces in Control Hub. A user without a calling license is not a SIP failure. Read the current subscription names in Control Hub help rather than a mnemonic from an older tenant.</p>
<h2>Teams Phone</h2>
<p>Teams Phone is a license plus a PSTN choice: Calling Plan, Operator Connect, or Direct Routing. The choice decides whether an SBC is on the path. The Florida Crystals deployment, linked on the integrations page, used Direct Routing and later Operator Connect. Those are not interchangeable troubleshooting targets.</p>
{sources([("CUCM 15 port usage", PORT_DOC), ("Webex help", "https://help.webex.com/"), ("Direct Routing plan", "https://learn.microsoft.com/en-us/microsoftteams/direct-routing-plan")])}
""", "How CUCM, Webex Calling, and Teams Phone licensing shows up in a design.")

    write_page("certifications.html", "Certifications", f"""
<p class="kicker">Exams as of the February 2026 Cisco update</p>
<h1>Certifications</h1>
<p class="lede">This lab is not an exam dump and it is not official training. The names below are the public exam names so you can aim your reading.</p>
<div class="table-scroll"><table><thead><tr><th>Exam</th><th>What Cisco published</th></tr></thead><tbody>
<tr><td>350-801 CLCOR</td><td>Implementing Cisco Collaboration Core Technologies. 120 minutes. Core for CCNP Collaboration and CCIE Collaboration. v2.0 topics start 3 February 2026. v1.2 testing ended 2 February 2026.</td></tr>
<tr><td>300-815 CLACC</td><td>Implementing Cisco Advanced Call Control On-Premises. v2.0 is a 90-minute concentration. Cisco's topic page includes signaling and media, CUBE, dial plan, and mobility.</td></tr>
<tr><td>300-820 CLHCT</td><td>Implementing Cisco Collaboration Hybrid and Cloud Technologies. Updated to v2.0 on the same February 2026 date, per Cisco's learning blog.</td></tr>
<tr><td>300-830 CLCCE</td><td>Implementing Cisco Collaboration Cloud Customer Experience. Cisco's February 2026 blog introduces this concentration.</td></tr>
</tbody></table></div>
<p>CCNP Collaboration remains a core exam plus one concentration. The blog describes the v2.0 set as a 50/50 split between cloud and on-premises topics. Confirm the live blueprint before you book a seat. Prices on Cisco's pages move.</p>
<p>Microsoft publishes Teams Phone and collaboration certifications on Microsoft Learn. Confirm the current exam code there. This lab does not freeze a Microsoft exam number that the page you book might already have replaced.</p>
<div class="path">
<a href="flows/basic-call.html"><span class="stepnum">CLCOR</span><strong>Protocols and call control</strong></a>
<a href="flows/cube.html"><span class="stepnum">CLACC</span><strong>CUBE and dial plan</strong></a>
<a href="flows/webex-lgw.html"><span class="stepnum">CLHCT</span><strong>Hybrid and cloud</strong></a>
<a href="flows/ucce.html"><span class="stepnum">CLCCE</span><strong>Customer experience</strong></a>
</div>
{sources([("Cisco learning blog, 2026 collaboration update", "https://blogs.cisco.com/learning/the-future-of-collaboration-is-here"), ("350-801 CLCOR", "https://www.cisco.com/site/us/en/learn/training-certifications/exams/clcor.html"), ("300-815 CLACC topics", "https://learningnetwork.cisco.com/s/clacc-exam-topics")])}
""", "Cisco collaboration certification names after the February 2026 update.")

    write_page("roadmap.html", "Roadmap", f"""
<p class="kicker">Study timeline</p>
<h1>Roadmap</h1>
<p class="lede">This is a reading order and a few dated public facts. It is not a vendor's product roadmap.</p>
<div class="table-scroll"><table><thead><tr><th>When</th><th>What is public</th></tr></thead><tbody>
<tr><td>2002</td><td>RFC 3261 obsoletes the first SIP RFC and is still the call-setup reference.</td></tr>
<tr><td>2018</td><td>Kari's Law and RAY BAUM'S Act set MLTS duties in the United States: direct 911, notification, and a dispatchable location.</td></tr>
<tr><td>3 Feb 2026</td><td>Cisco starts CCNP Collaboration v2.0 testing: CLCOR, CLACC, CLHCT, and the new CLCCE concentration. The blog calls it a 50/50 cloud and on-premises split.</td></tr>
<tr><td>This lab</td><td>Learn the leg first. Add cloud PSTN only after you can name which product owns the number. Add WFM, QM, CRM, and virtual agents only after the call has an id they can share.</td></tr>
</tbody></table></div>
<h2>Your next 12 sessions</h2>
<ol>
<li>Registration, basic call, SDP.</li>
<li>Dial plan and the CSS lab.</li>
<li>Hold, transfer, hunt, voicemail.</li>
<li>CUBE and the PSTN ladder.</li>
<li>One-way audio and OPTIONS.</li>
<li>MRA and certificates, as symptoms, not as a rebuild.</li>
<li>Emergency and QoS.</li>
<li>Webex local gateway and Teams Direct Routing, side by side.</li>
<li>Migration dual-run.</li>
<li>UCCE call type and Webex Contact Center entry point.</li>
<li>Ecosystem: recording, WFM, CRM, virtual agent.</li>
<li>Ten quiz questions and one branching case, written up as leg, id, counter, capture.</li>
</ol>
{sources([("Cisco learning blog", "https://blogs.cisco.com/learning/the-future-of-collaboration-is-here"), ("FCC MLTS", "https://www.fcc.gov/mlts-911-requirements"), RFC3261])}
""", "A study roadmap and the February 2026 certification date.")

    write_page("integrations.html", "Integrations", f"""
<p class="kicker">Published stories only</p>
<h1>Customer integrations</h1>
<p class="lede">Names below are taken from the vendor's public story or from a published marketplace listing. They are not this lab's customers, and the numbers are the publisher's numbers.</p>
<article class="paper">
<h2>Florida Crystals · Teams Phone</h2>
<p>Microsoft's customer story says telecom expenses dropped by 78 percent after the company consolidated PBX exposure, removed leased lines, and deployed Teams Phone. Direct Routing as a Service, and later Operator Connect, provided PSTN. The story counts 2,322 phone users on Operator Connect, says all on-premises PBX lines were decommissioned, and counts 400 devices with Teams Phone plus SIP common-area phones. Partners named in the story include Logitech, HP | Poly, AudioCodes, and NTT Data.</p>
<p><a href="https://www.microsoft.com/en/customers/story/1804528563383903958-florida-crystals-corporation-microsoft-teams-phone-manufacturing-en-united-states">Microsoft customer story</a></p>
</article>
<article class="paper">
<h2>AudioCodes · Teams Phone on Azure</h2>
<p>Microsoft's customer story quotes Benny Matityahu, VP Unified Communications at AudioCodes: a proof of concept that used to take six to eight weeks could be set up in a day after the move to Azure, and in many cases a new customer could be onboarded to Teams Phone within a week. The same story describes Voca as AudioCodes' Teams-native contact center, using Azure Cognitive Services, with routing, queuing, and CRM integration named as product capabilities.</p>
<p><a href="https://www.microsoft.com/en/customers/story/1722208281384472910-audiocodes-azurecognitiveservices-telecommunications-and-media-en-israel">Microsoft customer story</a></p>
</article>
<article class="paper">
<h2>A published pattern, not a measured end customer</h2>
<p>Logicalis lists a service to integrate Microsoft Teams Calling with Webex Contact Center using Teams Direct Routing and a Cisco CUBE as the SBC. That is a partner offer. It is not a case study with an outcome, and it is not evidence that every Teams plus Webex Contact Center design uses CUBE.</p>
<p>Separately, Cisco publishes a Webex Contact Center integration for Microsoft Teams on Microsoft AppSource. The listing describes skills-based routing of inbound calls, consult between agents and subject-matter experts, and support for Microsoft PSTN and third-party Direct Routing. Read the current listing before you design to a sentence on this page.</p>
<p><a href="https://appsource.microsoft.com/en-us/product/web-apps/cisco.webex-contact-center-microsoft-team?tab=Overview">Webex Contact Center for Microsoft Teams</a></p>
<p><a href="https://learn.microsoft.com/en-us/microsoftteams/teams-contact-center">Teams contact center models</a></p>
</article>
{sources([("Florida Crystals story", "https://www.microsoft.com/en/customers/story/1804528563383903958-florida-crystals-corporation-microsoft-teams-phone-manufacturing-en-united-states"), ("AudioCodes story", "https://www.microsoft.com/en/customers/story/1722208281384472910-audiocodes-azurecognitiveservices-telecommunications-and-media-en-israel")])}
""", "Published Teams Phone and contact-center integration stories.")

    imgs = []
    for rel in pool_images:
        imgs.append(f"<figure class='paper'><img src='assets/pool/{esc(rel)}' alt='Idea-pool diagram {esc(rel)}'><figcaption>{esc(rel)}</figcaption></figure>")
    write_page("rooms.html", "Diagrams", f"""
<p class="kicker">Idea pool</p>
<h1>Diagrams carried forward</h1>
<p class="lede">{len(pool_images)} drawings from the idea-pool branch. An older room archive was not readable from this build, so it is not silently rewritten here.</p>
{''.join(imgs)}
""", "SVG diagrams copied from the idea-pool branch.")

    write_page("download.html", "Download", download_body(), "Offline zip of the flagship lab and the classic campus.")

    glossary = f"""
<p class="kicker">Search</p>
<h1>Glossary</h1>
<p class="lede"><span class="num" id="glossCount">{cn + pn}</span> entries load from the two decks. The short list below is readable with scripts off.</p>
<label>Find a term <input id="glossQ" type="search" aria-label="Search glossary"></label>
<div id="glossHits"></div>
<h2>Short list</h2>
<div class="table-scroll"><table><thead><tr><th>Term</th><th>Use it this way</th></tr></thead><tbody>
<tr><td>CSS</td><td>An ordered list of partitions. Line CSS is consulted before device CSS.</td></tr>
<tr><td>Partition</td><td>A bucket of patterns. Order inside the CSS decides which bucket is searched first.</td></tr>
<tr><td>Dial-peer 0</td><td>No inbound peer you configured matched.</td></tr>
<tr><td>Early offer</td><td>SDP in the INVITE.</td></tr>
<tr><td>Delayed offer</td><td>SDP in the 200, answer in the ACK.</td></tr>
<tr><td>B2BUA</td><td>Two legs. CUBE is one. Read both.</td></tr>
<tr><td>ELIN</td><td>The callback number that should return to the site that dialed emergency services.</td></tr>
<tr><td>Call type</td><td>In UCCE, the object the dialed number selects and the bucket CUIC reports.</td></tr>
<tr><td>EF / 46</td><td>The DSCP commonly used for voice RTP. A queue still has to honor it.</td></tr>
<tr><td>SIPREC</td><td>RFC 7866 recording session from an SBC to a recorder.</td></tr>
</tbody></table></div>
"""
    write_page("ecosystem/glossary.html", "Glossary", glossary, "Searchable glossary of idea-pool and study cards.")


def write_bank() -> dict:
    raw = git_show(POOL, "campus/assets/idea-pool.js")
    data, _end = json.JSONDecoder().raw_decode(raw[raw.find("{") :])
    pr2 = git_show(LEARN, "learn/flashcards.html")
    match = re.search(r"const CARDS = (\[.*?\]);\s*const KEY", pr2, re.S)
    if not match:
        raise SystemExit("PR2 flashcards did not parse")
    pr2_cards = json.loads(match.group(1))
    bank = {
        "questions": data["questions"],
        "cards": data["cards"],
        "scenarios": data["scenarios"],
        "pr2Cards": pr2_cards,
    }
    text = "/* Flagship study bank. Idea pool plus the October 2026 cited cards. */\nwindow.UC_FLAGSHIP_BANK = "
    (OUT / "assets").mkdir(parents=True, exist_ok=True)
    (OUT / "assets" / "bank.js").write_text(text + json.dumps(bank, ensure_ascii=False) + ";\n", encoding="utf-8")
    return bank


def copy_assets() -> list[str]:
    inherited = OUT / "assets" / "inherited"
    inherited.mkdir(parents=True, exist_ok=True)
    listing = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", LEARN, "learn/svg"], text=True)
    for path in listing.split():
        if path.endswith(".svg"):
            (inherited / Path(path).name).write_bytes(git_bytes(LEARN, path))
    downloads = OUT / "downloads"
    downloads.mkdir(parents=True, exist_ok=True)
    listing = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", LEARN, "learn/pdf"], text=True)
    for path in listing.split():
        if path.endswith(".pdf"):
            (downloads / Path(path).name).write_bytes(git_bytes(LEARN, path))
    pool = OUT / "assets" / "pool"
    listing = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", POOL, "campus/assets/idea-pool-diagrams"], text=True)
    rels = []
    for path in listing.split():
        if not path.endswith(".svg"):
            continue
        rel = path.split("idea-pool-diagrams/", 1)[1]
        dest = pool / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(git_bytes(POOL, path))
        rels.append(rel)
    return rels


def write_clips() -> None:
    clips = OUT / "assets" / "clips"
    clips.mkdir(parents=True, exist_ok=True)
    frames = clips / "_frames"
    frames.mkdir(exist_ok=True)
    width, height = 320, 180
    for i in range(12):
        px = bytearray([18, 28, 48]) * (width * height)
        def set_px(x: int, y: int, rgb: tuple[int, int, int]) -> None:
            if 0 <= x < width and 0 <= y < height:
                o = (y * width + x) * 3
                px[o:o + 3] = bytes(rgb)
        for x in (60, 160, 260):
            for y in range(36, 160):
                set_px(x, y, (80, 96, 112))
        y = 50 + i * 8
        x0, x1 = 60, 60 + int((min(i, 8) / 8) * 100)
        for x in range(x0, x1):
            set_px(x, y, (94, 234, 212))
            set_px(x, y + 1, (94, 234, 212))
        if i > 8:
            for x in range(160, 160 + (i - 8) * 30):
                set_px(x, 70, (240, 179, 41))
        blob = b"P6\n320 180\n255\n" + bytes(px)
        (frames / f"f{i:02d}.ppm").write_bytes(blob)
    gif = clips / "invite.gif"
    subprocess.check_call([
        "ffmpeg", "-y", "-framerate", "8", "-i", str(frames / "f%02d.ppm"),
        "-loop", "0", str(gif),
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    shutil.rmtree(frames)
    (clips / "invite.svg").write_text("""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 180" role="img" aria-label="INVITE traveling to a proxy">
<rect width="320" height="180" fill="#121c30"/>
<line x1="60" y1="36" x2="60" y2="160" stroke="#506070"/>
<line x1="160" y1="36" x2="160" y2="160" stroke="#506070"/>
<line x1="260" y1="36" x2="260" y2="160" stroke="#506070"/>
<text x="60" y="24" text-anchor="middle" fill="#f4efe6" font-size="12">Phone</text>
<text x="160" y="24" text-anchor="middle" fill="#f4efe6" font-size="12">Proxy</text>
<text x="260" y="24" text-anchor="middle" fill="#f4efe6" font-size="12">Far end</text>
<circle r="5" fill="#5eead4"><animate attributeName="cx" values="60;160;160" dur="2.4s" repeatCount="indefinite"/><animate attributeName="cy" values="60;60;60" dur="2.4s" repeatCount="indefinite"/></circle>
<text x="110" y="52" fill="#5eead4" font-size="12">INVITE<animate attributeName="opacity" values="0;1;1;0" dur="2.4s" repeatCount="indefinite"/></text>
<text x="200" y="90" fill="#f0b429" font-size="12">100<animate attributeName="opacity" values="0;0;1;0" dur="2.4s" repeatCount="indefinite"/></text>
</svg>
""", encoding="utf-8")


def write_static_files() -> None:
    (OUT / "assets" / "icon.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 36 36"><rect width="36" height="36" rx="10" fill="#172033"/>'
        '<path d="M6 22c4-8 8-8 12 0s8 8 12 0" fill="none" stroke="#7dcec4" stroke-width="2"/></svg>',
        encoding="utf-8",
    )
    (OUT / "manifest.webmanifest").write_text(json.dumps({
        "name": "UC Lab Free University",
        "short_name": "UC Lab",
        "start_url": "./index.html",
        "display": "standalone",
        "background_color": "#f4efe6",
        "theme_color": "#172033",
        "icons": [{"src": "assets/icon.svg", "sizes": "any", "type": "image/svg+xml"}],
    }, indent=2), encoding="utf-8")
    (OUT / "sw.js").write_text(r"""
var CACHE = "uc-flagship-v1";
var CORE = ["./index.html", "./assets/site.css", "./assets/site.js", "./assets/play.js", "./assets/bank.js", "./assets/icon.svg", "./manifest.webmanifest"];
self.addEventListener("install", function (event) {
  event.waitUntil(caches.open(CACHE).then(function (cache) { return cache.addAll(CORE); }));
});
self.addEventListener("activate", function (event) {
  event.waitUntil(self.clients.claim());
});
self.addEventListener("fetch", function (event) {
  if (event.request.method !== "GET") return;
  event.respondWith(caches.match(event.request).then(function (hit) {
    var fetched = fetch(event.request).then(function (res) {
      if (res && res.status === 200) {
        var copy = res.clone();
        caches.open(CACHE).then(function (cache) { cache.put(event.request, copy); });
      }
      return res;
    }).catch(function () { return hit; });
    return hit || fetched;
  }));
});
""", encoding="utf-8")


def human_size(size: int) -> str:
    if size >= 1_000_000:
        return f"{size / 1_000_000:4.1f} MB"
    if size >= 1000:
        return f"{size / 1000:.0f} KB"
    return f"{size} B"


def file_icon(kind: str) -> str:
    color = {"ZIP": "#fde047", "PDF": "#fb7185", "PNG": "#22d3ee", "MP3": "#e879f9"}.get(kind, "#22d3ee")
    return (
        f'<svg class="file-ico" viewBox="0 0 48 48" aria-hidden="true">'
        f'<rect x="8" y="6" width="26" height="36" rx="4" fill="#141028" stroke="{color}" stroke-width="2"/>'
        f'<path d="M26 6v10h10" fill="none" stroke="{color}" stroke-width="2"/>'
        f'<text x="21" y="33" text-anchor="middle" font-size="9" font-family="Segoe UI, sans-serif" fill="{color}">{kind}</text>'
        f"</svg>"
    )


def file_card(href: str, title: str, kind: str, size_label: str) -> str:
    return (
        f'<a class="file-card glass" href="{esc(href)}" download>'
        f"{file_icon(kind)}<strong>{esc(title)}</strong><em>{esc(size_label)}</em></a>"
    )


def download_body() -> str:
    cards = [
        file_card("uc-lab-flagship.zip", "Studio zip", "ZIP", "00.0 MB"),
    ]
    campus = ROOT / "releases" / "uc-lab-free-university.html.zip"
    if campus.is_file():
        cards.append(file_card("../releases/uc-lab-free-university.html.zip", "Campus zip", "ZIP", human_size(campus.stat().st_size)))
    audio_names = {
        "architect-tour.mp3": "How to view the lab",
        "architect-practice.mp3": "How to practise and share",
    }
    for name, title in audio_names.items():
        path = OUT / "audio" / name
        if path.is_file():
            cards.append(file_card(f"audio/{name}", title, "MP3", human_size(path.stat().st_size)))
    for path in sorted((OUT / "downloads").glob("*.pdf")):
        cards.append(file_card(f"downloads/{path.name}", path.stem.replace("-", " "), "PDF", human_size(path.stat().st_size)))
    for path in sorted((OUT / "cheats").glob("*.pdf")):
        cards.append(file_card(f"cheats/{path.name}", f"{path.stem.replace('-', ' ')} sheet", "PDF", human_size(path.stat().st_size)))
    for path in sorted((OUT / "cheats").glob("*.png")):
        cards.append(file_card(f"cheats/{path.name}", f"{path.stem.replace('-', ' ')} image", "PNG", human_size(path.stat().st_size)))
    return f"""
<p class="kicker">Offline</p>
<h1 data-i18n="pageDownloads">Download this lab</h1>
<p class="lede">The timeline says what each group is for. The grid is the file. One click downloads it.</p>
<div class="pack-layout">
<ol class="timeline" id="packLine">
<li><button type="button" aria-expanded="true" data-pack="studio">01 · Studio zip</button><div class="time-body"><p>Flagship pages, drawings, quiz bank, cheat sheets, and the audio player. Open index.html after you unzip it.</p></div></li>
<li><button type="button" aria-expanded="false" data-pack="campus">02 · Deep campus</button><div class="time-body" hidden><p>580 sections, kept as the long library. The campus zip is the second card in the grid.</p></div></li>
<li><button type="button" aria-expanded="false" data-pack="sheets">03 · One-page sheets</button><div class="time-body" hidden><p>Each cheat code is one page, as PDF and PNG, plus the October study PDFs.</p></div></li>
<li><button type="button" aria-expanded="false" data-pack="audio">04 · Audio slots</button><div class="time-body" hidden><p>The player reads <code>audio/architect-tour.mp3</code> and <code>audio/architect-practice.mp3</code>. A later recording can replace those files without a new page.</p></div></li>
</ol>
<div class="file-grid">{''.join(cards)}</div>
</div>
<p>When this folder is served over http, the service worker caches the shell for the next visit. The zip does not need the network after you have it.</p>
"""


def write_zip() -> None:
    target = OUT / "uc-lab-flagship.zip"
    if target.exists():
        target.unlink()
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(OUT.rglob("*")):
            if not path.is_file() or path == target or path.name == ".DS_Store":
                continue
            zf.write(path, arcname=str(path.relative_to(OUT)))


def main() -> None:
    if OUT.exists():
        for child in OUT.iterdir():
            if child.name == "assets" and (child / "site.css").exists():
                continue
        # Rebuild generated HTML only. Keep hand-written css and js.
    pool_images = copy_assets()
    write_static_files()
    write_clips()
    bank = write_bank()
    build_flows()
    write_page("ports.html", "Ports and protocols", port_table(), "CUCM 15 ports engineers actually filter for.")
    ecosystem_pages()
    mindmap_page([OUT / "assets" / "pool" / rel for rel in pool_images])
    other_pages(bank, pool_images)
    from round2_pages import build_round2
    from round3_pages import build_round3
    build_round2(write_page, sources, bank)
    build_round3(write_page, sources, bank, ORDER)
    write_zip()
    page = OUT / "download.html"
    stamped = page.read_text(encoding="utf-8").replace(
        ">00.0 MB<",
        ">" + f"{(OUT / 'uc-lab-flagship.zip').stat().st_size / 1_000_000:4.1f} MB" + "<",
        1,
    )
    page.write_text(stamped, encoding="utf-8")
    write_zip()
    subprocess.check_call([sys.executable, str(ROOT / "scripts" / "check-flagship.py")])
    print(f"questions {len(bank['questions'])} cards {len(bank['cards'])} pr2 {len(bank['pr2Cards'])} cases {len(bank['scenarios'])} diagrams {len(pool_images)}")


if __name__ == "__main__":
    main()
