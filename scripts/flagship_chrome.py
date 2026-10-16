"""Shared flagship page chrome: menu, brand buttons, favicon, deferred scripts."""

from __future__ import annotations

import html

CONTACT = "https://cyphermonkeylabs.com/#contact"

NAV = [
    ("Home", "index.html", "navHome", "The front door and where to start", "home"),
    ("Diagrams", "diagrams/index.html", "navDiagrams", "Animated ladders and architecture drawings", "diagrams"),
    ("Flows", "flows/index.html", "navFlows", "Step a call one message at a time", "flows"),
    ("Charts", "charts/index.html", "navCharts", "Section counts, quiz tracks, and bandwidth", "charts"),
    ("Cheat Codes", "cheats/index.html", "navCheats", "One-page sheets you can print", "cheats"),
    ("Play", "play/index.html", "navPlay", "Ports game, map, sandbox, and daily drill", "play"),
    ("Ecosystem", "ecosystem/index.html", "navEco", "WFM, recording, CRM, and regions", "eco"),
    ("Downloads", "download.html", "navDownloads", "Take the studio and the campus offline", "downloads"),
    ("Careers", "guide/interview.html", "navCareers", "Interview practice with no invented wages", "careers"),
]

ICONS = {
    "home": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 3.2 3 11h2v9h5v-6h4v6h5v-9h2L12 3.2z"/></svg>',
    "diagrams": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="1.8" d="M5 7h4v4H5zm10-2h4v4h-4zm0 10h4v4h-4zM9 9l6-2M9 11l6 6"/></svg>',
    "flows": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" d="M4 7h12M4 12h16M4 17h9"/></svg>',
    "charts": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M4 19h16v2H4zM6 17V9h3v8H6zm5 0V5h3v12h-3zm5 0v-6h3v6h-3z"/></svg>',
    "cheats": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="1.8" d="M7 3h8l4 4v14H7zM15 3v4h4M9 12h6M9 16h6"/></svg>',
    "play": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M8 5v14l12-7z"/></svg>',
    "eco": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8" fill="none" stroke="currentColor" stroke-width="1.8"/><path fill="none" stroke="currentColor" stroke-width="1.6" d="M12 4c2 3 2 13 0 16M4.5 12h15"/></svg>',
    "downloads": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" d="M12 4v10m0 0 4-4m-4 4-4-4M5 19h14"/></svg>',
    "careers": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="8" r="3" fill="none" stroke="currentColor" stroke-width="1.8"/><path fill="none" stroke="currentColor" stroke-width="1.8" d="M5 19c1.5-3 4-4.5 7-4.5S17.5 16 19 19"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M4 6h16v2H4zm0 5h16v2H4zm0 5h16v2H4z"/></svg>',
    "listen": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M4 10h2v4H4zm4-3h2v10H8zm4-3h2v16h-2zm4 4h2v8h-2zm4 2h2v4h-2z"/></svg>',
    "github": '<svg viewBox="0 0 16 16" aria-hidden="true"><path fill="currentColor" d="M8 0C3.58 0 0 3.58 0 8a8 8 0 0 0 5.47 7.59c.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82A7.7 7.7 0 0 1 8 3.87c.67 0 1.35.09 1.98.26 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8z"/></svg>',
    "x": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M14.6 10.4 21.8 2h-1.7l-6.3 7.2L8.7 2H2.2l7.6 10.9L2.2 22h1.7l6.7-7.6L15.1 22h6.5l-7-11.6zm-2.4 2.7-.8-1.1L4.7 3.5h2.7l5.1 7.2.8 1.1 6.5 9.2h-2.7l-5.4-7.9z"/></svg>',
    "hf": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="1.7"/><circle cx="9" cy="10" r="1.15" fill="currentColor"/><circle cx="15" cy="10" r="1.15" fill="currentColor"/><path d="M8.2 14.2c1.1 1.7 6.5 1.7 7.6 0" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg>',
    "labs": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="currentColor" stroke-width="1.7"/><path d="M6 15c2.2-4 4.4-4 6.6 0s4.4 4 6.6 0" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg>',
}

BRANDS = [
    ("https://github.com/cipher0x9", "Visit my GitHub", "github"),
    ("https://github.com/CypherMonkeyLabs", "Visit the Labs org", "github"),
    ("https://cyphermonkeylabs.com", "Visit Cypher Monkey Labs", "labs"),
    ("https://x.com/Cypher0x9", "X", "x"),
    ("https://huggingface.co/Cypher0x9", "Hugging Face", "hf"),
]


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def brand_links(label: str = "Lucky and the labs") -> str:
    links = []
    for href, text, icon in BRANDS:
        links.append(
            f'<a class="brand-btn" href="{esc(href)}">'
            f'{ICONS[icon]}<span>{esc(text)}</span></a>'
        )
    return f'<nav class="brand-links" aria-label="{esc(label)}">{"".join(links)}</nav>'


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


def render_chrome(rel: str, title: str, body: str, description: str, order: list[tuple[str, str]]) -> str:
    depth = rel.count("/")
    root = "../" * depth
    current = rel

    def marked(href: str) -> str:
        section = href.split("/")[0] if href.endswith("/index.html") else ""
        on_section = bool(section) and current.startswith(section + "/")
        if href == current or on_section:
            return ' aria-current="page"'
        return ""

    tabs = []
    sheet = []
    for label, href, key, blurb, icon in NAV:
        abs_href = root + href
        here = marked(href)
        tabs.append(
            f'<a href="{esc(abs_href)}"{here} data-i18n="{key}">{esc(label)}</a>'
        )
        sheet.append(
            f'<a class="nav-item" href="{esc(abs_href)}"{here}>'
            f'<span class="nav-ico">{ICONS[icon]}</span>'
            f'<span class="nav-copy"><strong data-i18n="{key}">{esc(label)}</strong>'
            f"<small>{esc(blurb)}</small></span></a>"
        )
    quick = [
        ("Home", "index.html", "navHome", "home"),
        ("Diagrams", "diagrams/index.html", "navDiagrams", "diagrams"),
        ("Flows", "flows/index.html", "navFlows", "flows"),
        ("Play", "play/index.html", "navPlay", "play"),
    ]
    quick_html = "".join(
        f'<a href="{esc(root + href)}"{marked(href)}>'
        f'<span class="qb-ico">{ICONS[icon]}</span>'
        f'<span data-i18n="{key}">{esc(label)}</span></a>'
        for label, href, key, icon in quick
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
    found = [i for i, (href, _) in enumerate(order) if href == rel]
    if found:
        idx = found[0]
        prev_h, prev_l = order[(idx - 1) % len(order)]
        next_h, next_l = order[(idx + 1) % len(order)]
    else:
        prev_h, prev_l = ("cheats/index.html", "Cheat codes")
        next_h, next_l = ("download.html", "Offline download")

    def rel_to(target: str) -> str:
        if target.startswith("../"):
            return target
        return root + target

    sisters = [
        ("https://cyphermonkeylabs.com/ai-lab-free-university-mesmerizing/", "AI Lab"),
        ("https://cyphermonkeylabs.com/amazon-connect-lab-free-university-mesmerizing/", "Amazon Connect"),
        ("https://cyphermonkeylabs.com/microsoft-voice-cc-lab-free-university-mesmerizing/", "Microsoft Voice"),
        ("https://cyphermonkeylabs.com/five9-lab-free-university-mesmerizing/", "Five9"),
        ("https://cyphermonkeylabs.com/genesys-cloud-lab-free-university-mesmerizing/", "Genesys Cloud"),
        ("https://cyphermonkeylabs.com/nice-cxone-lab-free-university-mesmerizing/", "NICE CXone"),
        ("https://cyphermonkeylabs.com/sip-universe-lab-free-university-mesmerizing/", "SIP Universe"),
        (rel_to("path.html"), "Study path"),
    ]
    sister_html = "".join(
        f'<a class="card" href="{esc(href)}"><strong>{esc(label)}</strong></a>' for href, label in sisters
    )
    effects_html = ""
    if "data-effects" in body or rel in ("index.html", "diagrams/index.html", "charts/index.html"):
        effects_html = f'<script type="module" src="{root}assets/effects.js"></script>'
    confetti_html = ""
    if 'id="quiz"' in body:
        confetti_html = f'<script src="{root}assets/vendor/confetti.browser.js" defer></script>'
    bank_html = ""
    if any(token in body for token in ('id="quiz"', 'id="cards"', 'id="casePlayer"', 'id="dailyHost"')):
        bank_html = f'<script src="{root}assets/bank.js" defer></script>'
    brands = brand_links()
    who = (
        "Lucky is a lifelong student and an AI enthusiast. The path runs from systems, "
        "networking, voice, and the contact center into AI omni-channel agents."
    )
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="neon">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · UC Lab Free University</title>
<meta name="description" content="{esc(description)}">
<link rel="icon" href="{root}assets/favicon.ico" sizes="32x32">
<link rel="icon" href="{root}assets/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{root}assets/icon.svg">
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
    <div class="tools">
      {theme_html}
      <button type="button" class="btn mode-btn" data-i18n="mode">Light</button>
      <button type="button" class="btn motion-btn">Motion</button>
      <a class="btn dl" href="{root}download.html">Offline</a>
      <button type="button" class="btn settings-open" data-open="settings">Settings</button>
      <button type="button" class="btn menu-btn" data-open="menu" aria-expanded="false" aria-controls="siteMenu"><span class="burger" aria-hidden="true"></span><span data-i18n="menu">Menu</span></button>
    </div>
    <form class="site-search" role="search">
      <input id="siteSearch" class="js-search" type="search" placeholder="Search" aria-label="Search the lab" autocomplete="off" data-i18n-placeholder="searchPh">
      <div class="search-pop" hidden></div>
    </form>
  </div>
  <nav class="tabs" aria-label="Lab">{''.join(tabs)}</nav>
  {lang_html}
  <p class="progress" id="visitProgress">Progress</p>
</header>
<main id="content" class="wrap">
{crumbs_for(rel, title, root)}
{body}
</main>
<footer class="site-foot">
  <div class="wrap">
    <p class="kicker">Next</p>
    <p><a href="{esc(rel_to(prev_h))}">Previous · {esc(prev_l)}</a> · <a href="{esc(rel_to(next_h))}">Next · {esc(next_l)}</a> · <a href="{root}../campus/uc-lab-free-university.html">Deep campus · 580 sections</a></p>
    {brands}
    <p class="who">{esc(who)}</p>
    <div class="sister">{sister_html}</div>
    <p class="disc">Independent educational project, not affiliated with vendors. Trademarks belong to their owners. MIT code, CC BY-NC-SA content. Teaching models do not change a live system. Check the vendor's current document before you change production.</p>
    <p><a href="https://github.com/cipher0x9">Visit my GitHub</a> · <a href="{CONTACT}">Report a concern or takedown</a> · <a href="{CONTACT}">Work with us</a></p>
    <p class="copy">© 2026 CypherMonkeyLabs 🐒</p>
  </div>
</footer>
<div id="siteMenu" class="site-menu" hidden role="dialog" aria-modal="true" aria-labelledby="menuTitle">
  <div class="sheet-bar">
    <h2 id="menuTitle" data-i18n="menu">Menu</h2>
    <button type="button" class="btn sheet-close" data-close="menu" data-i18n="close">Close</button>
  </div>
  <form class="site-search menu-search" role="search">
    <input class="js-search" type="search" placeholder="Search diagrams, flows, charts, cheat codes" aria-label="Search the menu" autocomplete="off">
    <div class="search-pop" hidden></div>
  </form>
  <nav class="sheet-nav" aria-label="Sections">{''.join(sheet)}</nav>
  {brands}
  <div class="menu-actions">
    <button type="button" class="btn" data-open="listen" data-i18n="quickListen">Listen</button>
    <button type="button" class="btn settings-open" data-open="settings" data-i18n="settings">Settings</button>
  </div>
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
    <p class="kicker">Find Lucky</p>
    {brands}
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
  <button type="button" class="quick-menu" data-open="menu" aria-expanded="false" aria-controls="siteMenu"><span class="qb-ico">{ICONS["menu"]}</span><span data-i18n="menu">Menu</span></button>
</nav>
<button type="button" class="guide-launch" id="guideLaunch" aria-expanded="false" aria-controls="guideBot"><span class="guide-mark" aria-hidden="true">?</span><span>Guide</span></button>
<script src="{root}assets/search.js" defer></script>
{bank_html}
<script src="{root}assets/site.js" defer></script>
<script src="{root}assets/play.js" defer></script>
<script src="{root}assets/guide-launch.js" defer></script>
{effects_html}
{confetti_html}
</body>
</html>
"""
