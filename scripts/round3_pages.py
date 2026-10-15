"""Round-3 atlas, charts, tracks, search index, and the repo-root front door."""

from __future__ import annotations

import html
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "flagship"

# Section counts from this repo's campus catalog (README). They sum to 580.
CAMPUS_TRACKS = [
    ("start", "Start here", 6, "Explain a call with a leg, an identifier, a counter, and a capture.", "flows/basic-call.html"),
    ("sip", "SIP and media", 9, "Separate signaling from RTP before you blame the queue.", "flows/sdp.html"),
    ("cucm", "CUCM and CUBE", 12, "Trace CSS, route pattern, dial-peer, and the trunk.", "flows/dial-plan.html"),
    ("cloud", "Webex Calling and Teams Phone", 121, "Name the PSTN model before you open a trace.", "flows/webex-lgw.html"),
    ("ucce", "Contact center — UCCE and PCCE", 6, "Dialed number, call type, script, then the agent phone.", "flows/ucce.html"),
    ("ccaas", "CCaaS and UCaaS platforms", 105, "Follow one contact across the platforms you still meet.", "flows/webex-cc.html"),
    ("e911", "Emergency calling", 3, "Location, callback, and on-site notification.", "flows/e911.html"),
    ("qos", "Voice network and QoS", 16, "EF is a mark. The priority queue is the behavior.", "flows/qos.html"),
    ("migrate", "Migrations", 61, "Canary, evidence, and a rollback you wrote down.", "guide/migration.html"),
    ("trouble", "Troubleshooting", 112, "One hypothesis, one change, one capture.", "guide/playbooks.html"),
    ("evidence", "Evidence habits", 33, "Write the proof before you touch production.", "cases.html"),
    ("design", "Design notes", 35, "Identity, recording, and failure domains.", "guide/architecture.html"),
    ("practice", "Practice", 56, "Drill the fault without a customer on the line.", "play/index.html"),
    ("reference", "Reference", 5, "Glossary and the official-doc index.", "ecosystem/glossary.html"),
]

FLOW_GROUPS = [
    ("Signaling", 8),
    ("Edge and media", 6),
    ("Cloud PSTN", 3),
    ("Safety", 2),
    ("Features", 8),
    ("Contact center", 2),
]


def esc(value: str) -> str:
    return html.escape(str(value), quote=True)


def flow_svg(actors: list[str], hops: list[tuple[int, int, str]], animated: bool) -> str:
    col = 150
    width = col * len(actors)
    row = 46
    height = 56 + row * max(len(hops), 1) + 16
    xs = [int(col * (i + 0.5)) for i in range(len(actors))]
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" data-animated="{"true" if animated else "false"}" role="img">'
    ]
    lines.append('<rect width="100%" height="100%" fill="#0b0618"/>')
    if animated:
        lines.append(
            "<style>.hop{stroke-dasharray:7 5;animation:dash 1.1s linear infinite}"
            ".pkt{animation:ride 2.6s linear infinite}"
            "@keyframes dash{to{stroke-dashoffset:-24}}"
            "@keyframes ride{to{offset-distance:100%}}</style>"
        )
    for i, name in enumerate(actors):
        lines.append(
            f'<text x="{xs[i]}" y="24" text-anchor="middle" font-size="14" font-family="Georgia, serif" fill="#f5f7ff">{esc(name)}</text>'
            f'<line x1="{xs[i]}" y1="34" x2="{xs[i]}" y2="{height - 10}" stroke="#3b3260"/>'
        )
    for i, (a, b, label) in enumerate(hops):
        y = 58 + i * row
        x1, x2 = xs[a], xs[b]
        lines.append(
            f'<line class="hop" x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="#5eead4" stroke-width="2"/>'
            f'<text x="{(x1 + x2) / 2}" y="{y - 8}" text-anchor="middle" font-size="12" font-family="Segoe UI, sans-serif" fill="#f9a8d4">{esc(label)}</text>'
        )
        if animated:
            lines.append(
                f'<circle class="pkt" r="5" fill="#e07a5f" style="offset-path: path(\'M {x1} {y} H {x2}\'); offset-rotate: 0deg;"/>'
            )
    lines.append("</svg>")
    return "\n".join(lines)


def block_svg(boxes: list[tuple[str, str]], animated: bool) -> str:
    width = 860
    height = 86 + 74 * len(boxes)
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" data-animated="{"true" if animated else "false"}" role="img">'
        f'<rect width="{width}" height="{height}" fill="#0b0618"/>'
    ]
    if animated:
        lines.append("<style>.pulse{animation:pop 1.8s ease-in-out infinite}@keyframes pop{50%{opacity:.45}}</style>")
    for i, (title, note) in enumerate(boxes):
        y = 24 + i * 74
        klass = "pulse" if animated else ""
        lines.append(
            f'<rect class="{klass}" x="40" y="{y}" width="780" height="60" rx="12" fill="#141028" stroke="#e879f9"/>'
            f'<text x="60" y="{y + 26}" font-size="16" font-family="Georgia, serif" fill="#f5f7ff">{esc(title)}</text>'
            f'<text x="60" y="{y + 46}" font-size="13" font-family="Segoe UI, sans-serif" fill="#c4b5fd">{esc(note)}</text>'
        )
    lines.append("</svg>")
    return "\n".join(lines)


def diagram_catalog() -> list[tuple[str, str, str, bool]]:
    phone = ["Phone", "CUCM", "CUBE", "PSTN"]
    ladders = [
        ("registration", "SIP registration", phone[:2], [(0, 1, "REGISTER"), (1, 0, "401"), (0, 1, "REGISTER"), (1, 0, "200 OK")], True),
        ("basic-call", "Basic call", phone, [(0, 1, "INVITE"), (1, 2, "INVITE"), (2, 3, "INVITE"), (3, 2, "180"), (2, 1, "200"), (1, 0, "ACK")], True),
        ("hold", "Hold re-INVITE", ["Alice", "CUCM", "Bob"], [(0, 1, "re-INVITE sendonly"), (1, 2, "re-INVITE"), (2, 1, "200 recvonly"), (1, 0, "ACK")], True),
        ("blind-transfer", "Blind transfer", ["Alice", "CUCM", "Carol"], [(0, 1, "REFER"), (1, 0, "202"), (1, 2, "INVITE"), (2, 1, "NOTIFY")], True),
        ("attended-transfer", "Attended transfer", ["Alice", "CUCM", "Bob", "Carol"], [(0, 1, "INVITE Bob"), (1, 2, "200"), (0, 1, "REFER Carol"), (1, 3, "INVITE replaces")], True),
        ("early-media", "Early media", phone[:3], [(0, 1, "INVITE"), (1, 2, "INVITE"), (2, 1, "183 SDP"), (1, 0, "183 SDP")], True),
        ("prack", "PRACK", phone[:3], [(0, 1, "INVITE 100rel"), (1, 0, "183 RSeq"), (0, 1, "PRACK"), (1, 0, "200 PRACK")], True),
        ("session-refresh", "Session refresh", ["CUCM", "CUBE", "PSTN"], [(0, 1, "UPDATE"), (1, 2, "UPDATE"), (2, 1, "200"), (1, 0, "200")], True),
        ("one-way", "One-way audio", ["Phone A", "SBC", "Phone B"], [(0, 1, "200 OK"), (1, 2, "200 OK"), (0, 2, "RTP one way"), (2, 0, "no RTP")], True),
        ("cube", "CUBE two legs", ["CUCM", "CUBE", "ITSP"], [(0, 1, "INVITE peer 1"), (1, 2, "INVITE peer 2"), (2, 1, "SDP answer"), (1, 0, "SDP answer")], True),
        ("teams-options", "Teams OPTIONS", ["SBC", "Teams"], [(0, 1, "OPTIONS"), (1, 0, "200"), (0, 1, "INVITE"), (1, 0, "180")], True),
        ("e911", "Emergency callback", ["Phone", "CUCM", "Gateway", "PSAP"], [(0, 1, "911"), (1, 2, "INVITE ELIN"), (2, 3, "to PSAP"), (3, 2, "callback")], True),
        ("migration-cutover", "Cutover canary", ["Old PBX", "SBC", "New cloud"], [(0, 1, "canary DID"), (1, 2, "INVITE"), (2, 1, "200"), (1, 0, "rollback path")], True),
        ("hunt", "Hunt pilot", ["Caller", "CUCM", "Line 1", "Line 2"], [(0, 1, "to pilot"), (1, 2, "ring"), (2, 1, "no answer"), (1, 3, "next member")], True),
    ]
    out = []
    for slug, title, actors, hops, animated in ladders:
        out.append((slug, title, flow_svg(actors, hops, animated), animated))
    blocks = [
        ("architecture", "Five planes", [("Identity", "Directory number, user, device, certificate"), ("Signaling", "SIP 5060 or 5061, or SCCP 2000"), ("Media", "RTP between the SDP addresses"), ("Policy", "CSS, dial-peer, voice route, emergency"), ("Observe", "CDR, CUIC, CQD, the ladder")], False),
        ("deployment", "Deployment order", [("Publisher", "Install the first node before subscribers"), ("Time", "NTP on 123/UDP or certificates lie"), ("Names", "cisco-uds inside, collab-edge outside"), ("Files", "TFTP 69 and HTTP 6970"), ("Backup", "DRS to SFTP on 22")], False),
        ("firewall-zones", "Firewall zones", [("Phones to CUCM", "69, 6970, 5060, 5061, 2000, 2443, 3804"), ("Gateways", "2427 MGCP or 1720 H.225, plus RTP"), ("Applications", "2748 CTI, 8443 AXL, 8090 recording"), ("CUCM outward", "123 NTP, LDAP, 443 CSSM")], False),
        ("qos-marks", "QoS marks", [("Voice RTP", "Commonly EF, DSCP 46, then a priority queue"), ("Signaling", "Cisco designs often use CS3. RFC 4594 assigns CS5."), ("Unmarked", "A mark without a queue is only a label")], False),
        ("wfm-forecast", "Forecast then schedule", [("Offered load", "Calls per hour times handle time, divided by 3600"), ("Interval", "Usually 15 or 30 minutes, contact-center timezone"), ("Schedule", "Does not route the call. The ACD still owns the queue")], False),
        ("recording-fork", "Recording fork", [("Call", "Two phones, or a phone and the PSTN"), ("Fork", "Gateway HTTP 8090, or SIPREC on the SBC"), ("Score", "Quality management scores the audio. It is not the file")], False),
        ("crm-pop", "Screen pop", [("Key", "Pick +E.164, national digits, or a customer id"), ("Event", "Finesse, Webex Contact Center, or a Teams model"), ("Miss", "Often formatting. A wrong record is often a shared main number")], False),
        ("css-order", "Line CSS then device CSS", [("Emergency", "Partition searched before any 9.@ partition"), ("Line CSS", "Searched first"), ("Device CSS", "Searched after the line"), ("Block", "A miss never reaches CUBE")], False),
        ("mra-dns", "MRA names", [("Inside", "_cisco-uds._tcp answers for on-premises phones"), ("Outside", "_collab-edge._tls for remote Jabber"), ("Wrong publish", "A public cisco-uds answer is the wrong record")], False),
        ("tls-srtp", "TLS is not SRTP", [("5061", "TLS locks the signaling hop"), ("SRTP", "RFC 3711 locks the audio"), ("Both", "Require both only on a hop that can answer both")], False),
        ("cc-route", "Contact center route", [("Number", "UCCE dialed number or a Webex entry point"), ("Script", "Call type, then the script"), ("Agent", "Reserved on the desktop is not the same as ringing")], False),
        ("trouble-tree", "Troubleshooting tree", [("Registered?", "DNS, TFTP or edge, 401, time, certificate"), ("Reorder outside?", "CSS, then route list, then an empty CUBE trace"), ("One-way?", "SDP on both answers, then RTP both ways"), ("Silent agent?", "Capture the phone leg")], False),
        ("codec-stack", "G.711 at 20 ms", [("Payload", "160 bytes"), ("Layer 3", "80 kbit/s with a 40-byte IP/UDP/RTP header"), ("Ethernet", "87.2 kbit/s with an 18-byte header")], False),
        ("dial-peer", "Dial-peer match", [("Inbound", "If nothing matches, the leg is dial-peer 0"), ("Outbound", "Longest destination-pattern, then lowest preference"), ("Offer", "Write down early offer or delayed offer per leg")], False),
    ]
    for slug, title, boxes, animated in blocks:
        out.append((slug, title, block_svg(boxes, animated), animated))
    return out


def render_mermaid(folder: Path) -> list[tuple[str, str]]:
    sources = {
        "mermaid-register": ("Mermaid registration", "sequenceDiagram\n  participant Phone\n  participant CUCM\n  Phone->>CUCM: REGISTER\n  CUCM-->>Phone: 401\n  Phone->>CUCM: REGISTER\n  CUCM-->>Phone: 200 OK"),
        "mermaid-refer": ("Mermaid REFER", "sequenceDiagram\n  participant Alice\n  participant CUCM\n  participant Carol\n  Alice->>CUCM: REFER\n  CUCM-->>Alice: 202 Accepted\n  CUCM->>Carol: INVITE\n  Carol-->>CUCM: 200 OK"),
        "mermaid-options": ("Mermaid OPTIONS", "sequenceDiagram\n  participant SBC\n  participant Teams\n  SBC->>Teams: OPTIONS\n  Teams-->>SBC: 200 OK\n  SBC->>Teams: INVITE"),
        "mermaid-cutover": ("Mermaid cutover", "flowchart LR\n  Discover --> Normalize\n  Normalize --> Canary\n  Canary --> Cut\n  Cut --> Evidence\n  Canary -->|failed proof| Rollback"),
    }
    made = []
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return made
    script = OUT / "assets" / "vendor" / "mermaid.min.js"
    if not script.is_file():
        return made
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page()
        page.goto("about:blank")
        page.add_script_tag(path=str(script))
        for slug, (title, source) in sources.items():
            try:
                svg = page.evaluate(
                    """async (source) => {
                      mermaid.initialize({ startOnLoad: false, securityLevel: 'loose' });
                      const out = await mermaid.render('m' + Math.random().toString(16).slice(2), source);
                      return out.svg;
                    }""",
                    source,
                )
            except Exception as exc:
                print(f"mermaid skip {slug}: {exc}")
                continue
            svg = svg.replace("<svg ", '<svg data-animated="false" ', 1)
            (folder / f"{slug}.svg").write_text(svg, encoding="utf-8")
            made.append((slug, title))
        browser.close()
    return made


def bar_chart(chart_id: str, title: str, pairs: list[tuple[str, float]], note: str, unit: str) -> str:
    width = 860
    height = 36 + 28 * len(pairs) + 28
    peak = max((value for _, value in pairs), default=1) or 1
    rows = [
        f'<svg class="chart" data-chart="{esc(chart_id)}" viewBox="0 0 {width} {height}" role="img" aria-label="{esc(title)}">'
        f'<rect width="{width}" height="{height}" rx="16" fill="#0b0618"/>'
        f'<text x="16" y="22" font-size="16" font-family="Georgia, serif" fill="#f5f7ff">{esc(title)}</text>'
    ]
    for i, (label, value) in enumerate(pairs):
        y = 36 + i * 28
        bar = max(int((width - 280) * (value / peak)), 2)
        shown = f"{value:g}{unit}"
        rows.append(
            f'<g class="bar-row" tabindex="0"><title>{esc(label)}: {esc(shown)}. {esc(note)}</title>'
            f'<text x="16" y="{y + 16}" font-size="12" font-family="Segoe UI, sans-serif" fill="#e8eeff">{esc(label)}</text>'
            f'<rect class="bar" x="230" y="{y + 4}" width="{bar}" height="16" rx="4" fill="#5eead4"/>'
            f'<text x="{238 + bar}" y="{y + 16}" font-size="12" fill="#fde047">{esc(shown)}</text></g>'
        )
    rows.append(f'<text x="16" y="{height - 8}" font-size="11" fill="#c4b5fd">{esc(note)}</text></svg>')
    return "\n".join(rows)


def mascot(mood: str) -> str:
    mouth = {
        "study": '<path d="M28 58c6 6 14 6 20 0" fill="none" stroke="#172033" stroke-width="2"/>',
        "alert": '<circle cx="38" cy="58" r="4" fill="#172033"/>',
        "celebrate": '<path d="M28 54c6 10 14 10 20 0" fill="none" stroke="#172033" stroke-width="2"/>',
    }[mood]
    return f'''<svg class="mascot" viewBox="0 0 76 96" data-mood="{mood}" data-variant="{mood}" aria-hidden="true">
<ellipse cx="38" cy="36" rx="22" ry="20" fill="var(--fur, #fde047)"/>
<circle class="ear" cx="18" cy="22" r="8" fill="var(--ear, #e879f9)"/><circle class="ear" cx="58" cy="22" r="8" fill="var(--ear, #22d3ee)"/>
<g class="eyes"><ellipse cx="30" cy="34" rx="3.2" ry="3.2" fill="#172033"/><ellipse cx="46" cy="34" rx="3.2" ry="3.2" fill="#172033"/>
<ellipse class="lid" cx="30" cy="34" rx="4.2" ry="3.6" fill="var(--fur, #fde047)"/><ellipse class="lid" cx="46" cy="34" rx="4.2" ry="3.6" fill="var(--fur, #fde047)"/></g>
{mouth}
<rect x="24" y="62" width="28" height="22" rx="8" fill="var(--suit, #22d3ee)"/>
<g class="arm"><path d="M20 68c-8 2-12 10-8 14 4-2 8-2 10 2" fill="var(--fur, #fde047)" stroke="#172033" stroke-width="1"/></g>
</svg>'''


_ISO = 0


def iso_icon(kind: str) -> str:
    global _ISO
    _ISO += 1
    gid = f"iso{_ISO}"
    pair = {
        "diagram": ("#22d3ee", "#e879f9"),
        "flow": ("#fde047", "#fb7185"),
        "chart": ("#86efac", "#22d3ee"),
        "cheat": ("#f0abfc", "#818cf8"),
        "play": ("#fb7185", "#fde047"),
        "career": ("#67e8f9", "#a78bfa"),
        "download": ("#fde047", "#22d3ee"),
        "globe": ("#38bdf8", "#a3e635"),
        "phone": ("#e879f9", "#22d3ee"),
    }.get(kind, ("#22d3ee", "#e879f9"))
    return f'''<svg class="iso" viewBox="0 0 120 120" aria-hidden="true">
<defs><linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{pair[0]}"/><stop offset="1" stop-color="{pair[1]}"/></linearGradient></defs>
<ellipse cx="60" cy="104" rx="34" ry="8" fill="#000" opacity="0.35"/>
<polygon points="60,18 102,40 60,62 18,40" fill="url(#{gid})"/>
<polygon points="18,40 60,62 60,96 18,74" fill="{pair[0]}" opacity="0.85"/>
<polygon points="102,40 60,62 60,96 102,74" fill="{pair[1]}" opacity="0.9"/>
<polygon points="60,34 78,44 60,54 42,44" fill="#fff" opacity="0.85"/>
</svg>'''


def track_strip(count: int, symbol: str, number: str, label: str, shape: str = "sip") -> str:
    return f'''<div class="track-face" data-effects data-parallax>
<div class="parallax">
  <span class="tilt" data-depth="0.15">{mascot("study")}</span>
  <span class="tilt" data-depth="0.28">{mascot("alert")}</span>
  <span class="tilt" data-depth="0.4">{mascot("celebrate")}</span>
  <canvas data-mini3d data-shape="{esc(shape)}" width="140" height="140" aria-hidden="true"></canvas>
</div>
<section class="stats" aria-label="Track counts">
  <div class="stat"><span class="num" data-count="{count}">{count}</span><span class="label">Campus sections</span></div>
  <div class="stat"><span class="num">{esc(symbol)}</span><span class="label">{esc(label)}</span></div>
  <div class="stat"><span class="num">{esc(number)}</span><span class="label">Symbol on this track</span></div>
</section>
</div>'''


def symbols_for(slug: str) -> tuple[str, str, str]:
    table = {
        "start": ("01", "Leg", "First counter"),
        "sip": ("5060", "SIP", "Signaling port"),
        "cucm": ("CSS", "Line", "Searched first"),
        "cloud": ("SBC", "OPTIONS", "Direct Routing"),
        "ucce": ("DN", "Call type", "Script bucket"),
        "ccaas": ("EP", "Entry", "Cloud entry point"),
        "e911": ("911", "ELIN", "Callback identity"),
        "qos": ("46", "EF", "DSCP"),
        "migrate": ("+E", "164", "Normalize first"),
        "trouble": ("1", "Change", "Then capture"),
        "evidence": ("CDR", "Ladder", "Keep both"),
        "design": ("5", "Planes", "Identity to observe"),
        "practice": ("29", "Cases", "Branching set"),
        "reference": ("RFC", "3261", "Cite the hop"),
    }
    number, symbol, label = table[slug]
    return symbol, number, label


def build_round3(write_page, sources, bank: dict, order: list) -> None:
    if sum(row[2] for row in CAMPUS_TRACKS) != 580:
        raise SystemExit("campus track counts must sum to 580")
    if sum(count for _, count in FLOW_GROUPS) != 29:
        raise SystemExit("flow groups must sum to 29")
    folder = OUT / "diagrams"
    folder.mkdir(parents=True, exist_ok=True)
    catalog = diagram_catalog()
    for slug, _title, svg, _animated in catalog:
        (folder / f"{slug}.svg").write_text(svg, encoding="utf-8")
    mermaid_made = render_mermaid(folder)
    cards = []
    for slug, title, _svg, animated in catalog:
        kind = "Animated flow" if animated else "Diagram"
        cards.append(
            '<article class="card glass shot-card">'
            f'<button type="button" class="shot" data-why="{esc(title)}. A teaching drawing. Open the page for the caption.">'
            f'<img src="{slug}.svg" alt="{esc(title)}"></button>'
            f'<h2><a href="{slug}.html">{esc(title)}</a></h2><p>{kind}</p></article>'
        )
        write_page(
            f"diagrams/{slug}.html",
            title,
            f'<p class="kicker">Diagram atlas</p><h1>{esc(title)}</h1>'
            f'<figure class="ladder">{(folder / (slug + ".svg")).read_text(encoding="utf-8")}</figure>'
            f'<p><a href="index.html">Back to the atlas</a></p>',
            title,
        )
    for slug, title in mermaid_made:
        cards.append(
            '<article class="card glass shot-card">'
            f'<button type="button" class="shot" data-why="{esc(title)}. Rendered with Mermaid at build time.">'
            f'<img src="{slug}.svg" alt="{esc(title)}"></button>'
            f'<h2><a href="{slug}.svg">{esc(title)}</a></h2><p>Rendered with Mermaid at build time</p></article>'
        )
    write_page(
        "diagrams/index.html",
        "Diagrams",
        f'<p class="kicker">Atlas</p><h1 data-i18n="pageDiagrams">Diagram atlas</h1>'
        f'<p class="lede" data-effects>{len(catalog) + len(mermaid_made)} custom diagrams. '
        f'{sum(1 for item in catalog if item[3])} of the hand-built ladders and trees are animated. '
        f'Mermaid sequence and flow charts, when present, were rendered at build time from the vendored library.</p>'
        f'<div class="flow-atlas">{"".join(cards)}</div>',
        "Browsable diagram atlas of call flows, architecture, and cutover.",
    )

    q_counts = Counter((item.get("track") or "General") for item in bank["questions"])
    c_counts = Counter((item.get("track") or "General") for item in bank["cards"])
    q_pairs = sorted(q_counts.items(), key=lambda item: (-item[1], item[0]))[:8]
    c_pairs = sorted(c_counts.items(), key=lambda item: (-item[1], item[0]))[:8]
    charts = [
        bar_chart("campus-sections", "Campus sections by track", [(row[1], row[2]) for row in CAMPUS_TRACKS], "Counts from this repo's 580-section catalog. They sum to 580.", ""),
        bar_chart("quiz-tracks", "Quiz questions by track", q_pairs, f"Top tracks in the {len(bank['questions'])} idea-pool questions.", ""),
        bar_chart("card-tracks", "Idea-pool cards by track", c_pairs, f"Top tracks in the {len(bank['cards'])} idea-pool cards.", ""),
        bar_chart("flows", "Playable flows by family", FLOW_GROUPS, "The 29 flagship ladders, grouped. They sum to 29.", ""),
        bar_chart("g711", "G.711 20 ms bandwidth", [("Layer 3", 80), ("With 18-byte Ethernet", 87.2)], "Payload 160 bytes. Layer 3 adds a 40-byte IP/UDP/RTP header.", " kbit/s"),
        bar_chart("ports", "Port chapter families", [("Signaling", 4), ("Phone files", 3), ("CTI and AXL", 3), ("Media range", 1), ("Time and license", 2)], "Families in the flagship firewall sheet, from the CUCM 15 port chapter.", ""),
    ]
    write_page(
        "charts/index.html",
        "Charts",
        '<p class="kicker">Counted</p><h1 data-i18n="pageCharts">Charts</h1>'
        '<p class="lede" data-effects>Six charts. Hover a bar for the source. Pin one chart in the stage. The numbers are the campus catalog, the question bank, the 29 flows, the G.711 formula already used in the labs, or the port-chapter families. Nothing here is a market share.</p>'
        '<div class="dash" id="chartDash"><div class="dash-stage glass" id="chartStage"></div><div class="dash-picks" id="chartPicks"></div></div>'
        f'<div class="chart-stack">{"".join(f"<figure class=\"chart-card glass\" data-chart-card>{svg}</figure>" for svg in charts)}</div>'
        '<h2>Sketch of a troubleshooting tree</h2>'
        '<svg id="roughBoard" viewBox="0 0 780 120" data-effects></svg>'
        + sources([
            ("CUCM 15 port usage", "https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15/cucm_m_tcp-and-udp-port-usage-12-0.html"),
            ("RFC 4594", "https://www.rfc-editor.org/rfc/rfc4594"),
        ]),
        "Charts drawn from the lab catalog and cited formulas.",
    )

    track_icons = {
        "start": "phone", "sip": "flow", "cucm": "diagram", "cloud": "globe", "ucce": "chart",
        "ccaas": "globe", "e911": "phone", "qos": "chart", "migrate": "flow", "trouble": "diagram",
        "evidence": "cheat", "design": "diagram", "practice": "play", "reference": "cheat",
    }
    track_cards = []
    for slug, title, count, blurb, href in CAMPUS_TRACKS:
        symbol, number, label = symbols_for(slug)
        track_cards.append(
            f'<a class="card glass iso-card" href="{slug}.html">{iso_icon(track_icons.get(slug, "phone"))}'
            f'<h2>{esc(title)}</h2><p>{count} sections</p></a>'
        )
        write_page(
            f"tracks/{slug}.html",
            title,
            f'<p class="kicker">Track</p><h1>{esc(title)}</h1><p class="lede">{esc(blurb)}</p>'
            f'{track_strip(count, symbol, number, label, slug)}'
            f'<p><a class="btn" href="../{href}">Open the working page</a></p>',
            blurb,
        )
    write_page(
        "tracks/index.html",
        "Tracks",
        f'<p class="kicker">Catalog</p><h1>Tracks</h1>'
        f'<p class="lede">Fourteen tracks. The section counts are the campus catalog and sum to 580.</p>'
        f'{track_strip(580, "580", "14", "Tracks in the catalog")}'
        f'<div class="atlas">{"".join(track_cards)}</div>',
        "Campus tracks with section counts.",
    )

    icon_names = {
        "start": "Start", "sip": "SIP", "cucm": "CUCM", "cloud": "Webex", "ucce": "UCCE",
        "ccaas": "CCaaS", "e911": "E911", "qos": "QoS", "migrate": "Migrate", "trouble": "Trouble",
        "evidence": "Evidence", "design": "Design", "practice": "Practice", "reference": "Reference",
    }
    qn = len(bank["questions"])
    cn = len(bank["cards"])
    pn = len(bank["pr2Cards"])
    sn = len(bank["scenarios"])
    write_page(
        "index.html",
        "UC Lab",
        f'''<section class="bleed" data-effects data-parallax>
<div class="icon-dock" id="iconDock">
<div class="icon-track">
<canvas id="iconStage" aria-hidden="true"></canvas>
<div class="icon-links">{"".join(
    f'<a href="tracks/{slug}.html" data-shape="{slug}"><span>{esc(icon_names.get(slug, title.split("—")[0].strip()))}</span></a>'
    for slug, title, count, blurb, href in CAMPUS_TRACKS
)}</div>
</div>
</div>
<div class="neon-fallback" aria-hidden="true">
  <div class="grid"></div>
  <div class="sparks"></div>
  <div class="ring r1"></div>
  <div class="ring r2"></div>
  <div class="ring r3"></div>
  <div class="orbit"><b></b><b></b><b></b><b></b></div>
</div>
<canvas id="hero3d" aria-label="Orbiting call path with labelled CUCM, Webex, UCCE, SBC, PSTN, and Teams nodes"></canvas>
<div class="bleed-copy">
<p class="kicker" data-i18n="greet">Welcome to the lab</p>
<h1 data-i18n="heroTitle">Voice, UC, and contact center.</h1>
<p class="symbols" aria-label="Symbols"><span>5060</span><span>5061</span><span>EF 46</span><span>RTP</span></p>
<p class="lede" data-i18n="heroLede">Fundamentals, then the edge, the cloud, and the systems around the agent.</p>
<div class="actions">
<a class="btn dl" href="path.html" data-i18n="startPath">Start the path</a>
<a class="btn" href="diagrams/index.html" data-i18n="openDiagrams">Open diagrams</a>
<a class="btn" href="campus/uc-lab-free-university.html" data-i18n="campus">Deep campus</a>
</div>
</div>
<div class="hero-mascot">{mascot("study")}</div>
<div class="ticker" aria-hidden="true"><span>5060 SIP · 5061 TLS · 2000 SCCP · 2443 Secure SCCP · 69 TFTP · 6970 HTTP · EF 46 · RTP 16384–32767 · 911 direct dial · </span></div>
<section class="stats" aria-label="Counts">
<div class="stat glass"><svg class="visit-ring" viewBox="0 0 42 42" aria-hidden="true"><circle cx="21" cy="21" r="16"></circle><circle class="fg" id="visitRing" cx="21" cy="21" r="16"></circle></svg><span class="num" data-count="29">29</span><span class="label">Playable flows</span></div>
<div class="stat glass"><span class="num" data-count="{qn}">{qn}</span><span class="label">Quiz questions</span></div>
<div class="stat glass"><span class="num" data-count="{cn + pn}">{cn + pn}</span><span class="label">Flashcards</span></div>
<div class="stat glass"><span class="num" data-count="{sn}">{sn}</span><span class="label">Branching cases</span></div>
<div class="stat glass"><span class="num" data-count="580">580</span><span class="label">Campus sections</span></div>
<div class="stat glass"><span class="num" data-count="{len(catalog)}">{len(catalog)}</span><span class="label">Atlas diagrams</span></div>
</section>
</section>
<div class="toggles" aria-label="Break a link in the diagram">
<label><input type="checkbox" data-break="phone-cucm"> Phone–CUCM down</label>
<label><input type="checkbox" data-break="cucm-cube"> Trunk down</label>
<label><input type="checkbox" data-break="cube-pstn"> Carrier down</label>
</div>
<section class="wall">
<h2 data-i18n="wall">Signal wall</h2>
<p class="lede">Large drawings. Click one to enlarge it, then step the hops.</p>
<div class="wall-grid">
<button type="button" class="shot glass" data-why="REGISTER stores a binding. It does not create a call. RFC 3261 section 10."><img src="diagrams/registration.svg" alt="SIP registration ladder"></button>
<button type="button" class="shot glass" data-why="The call is not up until ACK. Media can skip the proxy. RFC 3261."><img src="diagrams/basic-call.svg" alt="Basic call ladder"></button>
<button type="button" class="shot glass" data-why="Voice RTP is commonly EF, DSCP 46. Cisco signaling designs often use CS3. RFC 4594 assigns signaling CS5."><img src="diagrams/qos-marks.svg" alt="QoS marks"></button>
<button type="button" class="shot glass" data-why="Emergency calling needs a callback identity. This drawing is a teaching ladder, not a carrier design."><img src="diagrams/e911.svg" alt="Emergency callback ladder"></button>
</div>
</section>
<h2 data-i18n="next">Where to go next</h2>
<div class="atlas">
<a class="card glass iso-card" href="diagrams/index.html">{iso_icon("diagram")}<h2>Diagrams</h2><p>Animated ladders and the architecture set.</p></a>
<a class="card glass iso-card" href="flows/index.html">{iso_icon("flow")}<h2>Flows</h2><p>Large ladders you can step.</p></a>
<a class="card glass iso-card" href="charts/index.html">{iso_icon("chart")}<h2>Charts</h2><p>Section counts, quiz tracks, bandwidth.</p></a>
<a class="card glass iso-card" href="cheats/index.html">{iso_icon("cheat")}<h2>Cheat Codes</h2><p>One-page sheets and the offline zip.</p></a>
<a class="card glass iso-card" href="play/index.html">{iso_icon("play")}<h2>Play</h2><p>Ports game, map, sandbox, daily challenge.</p></a>
<a class="card glass iso-card" href="ecosystem/index.html">{iso_icon("globe")}<h2>Ecosystem</h2><p>WFM, recording, CRM, regions.</p></a>
<a class="card glass iso-card" href="download.html">{iso_icon("download")}<h2>Downloads</h2><p>Flagship zip and the campus zip.</p></a>
<a class="card glass iso-card" href="guide/interview.html">{iso_icon("career")}<h2>Careers</h2><p>Interview questions and a path with no invented wages.</p></a>
<a class="card glass iso-card" href="ecosystem/regions.html">{iso_icon("globe")}<h2>Regions</h2><p>Cited emergency and privacy rules. Coverage stays on the vendor page.</p></a>
</div>
<section class="audio-dock glass">
<h2 data-i18n="audioTitle">Architect conversation</h2>
<p>Two short clips. Maya asks. Jules answers. About a minute and a half together.</p>
<audio controls preload="none" src="audio/architect-tour.mp3">
  <a href="audio/architect-tour.mp3">How to view the lab</a>
</audio>
<p>How to view the lab. <a href="audio/scripts/architect-tour.md">Script</a></p>
<audio controls preload="none" src="audio/architect-practice.mp3">
  <a href="audio/architect-practice.mp3">How to practise and share</a>
</audio>
<p>How to practise and share. <a href="audio/scripts/architect-practice.md">Script</a></p>
<p><a href="https://github.com/cipher0x9/uc-lab-free-university-mesmerizing">Rate, comment, or share this lab on GitHub</a> · <a href="https://cyphermonkeylabs.com/#contact">Work with the studio</a></p>
</section>''',
        "Flagship UC lab. The repository root opens this studio.",
    )
    # The deep campus link on the flagship copy must climb out of flagship/.
    flagship_home = (OUT / "index.html").read_text(encoding="utf-8")
    flagship_home = flagship_home.replace('href="campus/uc-lab-free-university.html"', 'href="../campus/uc-lab-free-university.html"')
    (OUT / "index.html").write_text(flagship_home, encoding="utf-8")

    def node(content, children=None):
        return {"content": content, "children": children or []}

    mind = node("UC Lab", [
        node("Signaling", [node("REGISTER"), node("INVITE"), node("SDP")]),
        node("Edge", [node("CUBE"), node("MRA"), node("SRTP")]),
        node("Cloud", [node("Webex Calling"), node("Teams Phone")]),
        node("Around the agent", [node("WFM"), node("Recording"), node("CRM")]),
    ])
    write_page(
        "ecosystem/mindmap.html",
        "Mind map",
        '<p class="kicker">Map</p><h1>Mind map</h1>'
        '<p class="lede">An interactive map drawn with Markmap and D3, both vendored. The static drawing under it is the idea-pool ecosystem.</p>'
        f'<svg id="mind" class="mind-live"></svg>'
        '<figure class="ladder"><img src="../assets/pool/ecosystem/mindmap.svg" alt="Idea-pool ecosystem drawing"></figure>'
        '<script src="../assets/vendor/d3.min.js"></script>'
        '<script src="../assets/vendor/markmap-view.js"></script>'
        f'<script>markmap.Markmap.create("#mind", {{}}, {json.dumps(mind)});</script>',
        "Interactive mind map of the lab.",
    )

    entries = [{"title": label, "href": href, "text": label} for href, label in order]
    for slug, title, _svg, _animated in catalog:
        entries.append({"title": title, "href": f"diagrams/{slug}.html", "text": title})
    (OUT / "assets" / "search.js").write_text(
        "window.UC_SEARCH = " + json.dumps(entries) + ";\n",
        encoding="utf-8",
    )
    publish_root()


def publish_root() -> None:
    text = (OUT / "index.html").read_text(encoding="utf-8")

    def rewrite(match: re.Match) -> str:
        attr, quote, url = match.group(1), match.group(2), match.group(3)
        if url.startswith(("http://", "https://", "mailto:", "#", "data:", "//")):
            return match.group(0)
        if url.startswith("../campus/"):
            url = url[3:]
        elif url.startswith("./"):
            url = url[2:]
            if url != "index.html":
                url = "flagship/" + url
        elif url != "index.html" and not url.startswith("campus/"):
            url = "flagship/" + url
        return f"{attr}={quote}{url}{quote}"

    text = re.sub(r'\b(href|src)=(["\'])([^"\']+)\2', rewrite, text)
    text = text.replace('data-root=""', 'data-root="flagship/"')
    text = text.replace('href="flagship/campus/', 'href="campus/')
    if 'http-equiv="refresh"' in text:
        raise SystemExit("root front door must not be a refresh")
    (ROOT / "index.html").write_text(text, encoding="utf-8")
