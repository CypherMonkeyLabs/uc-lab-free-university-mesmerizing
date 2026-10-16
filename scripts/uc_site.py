#!/usr/bin/env python3
"""Write UC university HTML, SVG, sheets, and office exports."""
from __future__ import annotations

import html
import json
import re
import zipfile
from pathlib import Path

from build_uc_round2 import (
    CONTACT,
    ORG,
    SECTIONS,
    TRACKS,
    WEB,
    arch_svg,
    build_diagrams,
    dl_buttons,
    esc,
    flow_svg,
    footer,
    rooms,
    write_page,
)

ROOT = Path(__file__).resolve().parent.parent


def diagram_svg(item: dict) -> str:
    if item["kind"] == "flow":
        return flow_svg(item)
    return arch_svg(item)


def room_body(room: dict, pre: str) -> str:
    bullets = "".join(f"<li>{esc(item)}</li>" for item in room["five"])
    questions = []
    for index, (prompt, why, choices, answer) in enumerate(room["quiz"], start=1):
        buttons = "".join(
            f'<button type="button" class="choice ghost" data-choice="{esc(choice)}">{esc(choice)}</button>'
            for choice in choices
        )
        questions.append(
            f'<div class="quiz" data-quiz data-answer="{esc(answer)}"><p><strong>{index}.</strong> {esc(prompt)}</p>'
            f"{buttons}<p class=\"quiz-note\" hidden>{esc(why)}</p></div>"
        )
    sources = "".join(f'<li><a href="{href}">{esc(title)}</a></li>' for title, href in room["sources"])
    glossary = "".join(f"<li><strong>{esc(term)}</strong> — {esc(meaning)}</li>" for term, meaning in room["glossary"])
    confirm = f'<p class="confirm">Confirm before relying. {esc(room["confirm"])}</p>' if room.get("confirm") else ""
    sheet = room["sheet"]
    return f"""
<div class="wrap">
<p class="kicker">{esc(room["track"])} · {esc(room["id"])}</p>
<h1>{esc(room["title"])}</h1>
{dl_buttons(pre, room["diagram"], sheet)}
<section id="five" class="five"><h2>Learn it in 5 minutes</h2><ul>{bullets}</ul></section>
<section id="visual"><h2>Visual</h2><div class="diagram-frame"><img src="{pre}assets/diagrams/university/{room["diagram"]}.svg" alt="{esc(room["title"])} diagram"></div></section>
<section id="core"><h2>What is going on</h2><p>{esc(room["core"])}</p>{confirm}</section>
<section id="example" class="worked"><h2>Worked example</h2><p>{esc(room["example"])}</p></section>
<section id="quiz"><h2>Quiz</h2>{''.join(questions)}</section>
<section id="eco" class="eco-panel"><h2>Ecosystem</h2>
<p>{esc(room["eco"])}</p>
<ul>{glossary}</ul>
<p><strong>Config.</strong> {esc(room["config"])}</p>
<p><strong>Troubleshooting.</strong> {esc(room["trouble"])}</p>
<p><strong>Bridge.</strong> {esc(room["bridge"])}</p>
<p>Mind map, sister technologies, and future hooks live on the <a href="{pre}ecosystem.html">ecosystem page</a>.</p>
</section>
<section id="sources" class="sources"><h2>Sources</h2><ul>{sources}</ul>
<p>Product screens move. Confirm the guide for your release before you change a live system.</p></section>
{dl_buttons(pre, room["diagram"], sheet)}
</div>
"""


def page_wrap(inner: str) -> str:
    return f'<div class="wrap">{inner}</div>'


def emit_diagrams(items: list[dict]) -> None:
    svg_dir = ROOT / "assets" / "diagrams" / "university"
    html_dir = ROOT / "downloads" / "diagrams"
    svg_dir.mkdir(parents=True, exist_ok=True)
    html_dir.mkdir(parents=True, exist_ok=True)
    for item in items:
        svg = diagram_svg(item)
        (svg_dir / f"{item['slug']}.svg").write_text(svg, encoding="utf-8")
        standalone = (
            "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\">"
            f"<title>{esc(item['title'])}</title>"
            "<link rel=\"stylesheet\" href=\"../../assets/css/footer.css\">"
            "<style>body{margin:0;background:#0b1020;color:#e0e7ff;font-family:system-ui,sans-serif}svg{width:100%;height:auto}</style>"
            f"</head><body><h1 style=\"padding:12px 16px\">{esc(item['title'])}</h1>{svg}{footer()}</body></html>"
        )
        (html_dir / f"{item['slug']}.html").write_text(standalone, encoding="utf-8")


def emit_rooms(room_rows: list[dict]) -> None:
    for room in room_rows:
        rel = f"rooms/{room['slug']}.html"
        write_page(rel, room["title"], room["five"][0], "learn", room_body(room, "../"), room["track"])


def emit_tracks(room_rows: list[dict]) -> None:
    for tid, name, blurb, color in TRACKS:
        cards = []
        for room in room_rows:
            if room["track"] != tid:
                continue
            cards.append(
                f'<a class="room-card" href="../rooms/{room["slug"]}.html"><h2>{esc(room["title"])}</h2><p>{esc(room["five"][0])}</p></a>'
            )
        body = page_wrap(
            f'<p class="kicker">{esc(tid)}</p><h1>{esc(name)}</h1><p class="lede">{esc(blurb)}</p>'
            f'<div class="room-downloads"><a class="dl-btn" href="../downloads/sheets/{sheet_for(tid)}.html">Cheat sheet</a></div>'
            f'<div class="card-grid">{"".join(cards)}</div>'
        )
        write_page(f"tracks/{tid}.html", name, blurb, "learn", body, tid)


def sheet_for(tid: str) -> str:
    return {
        "T1": "sip",
        "T2": "dial-plan",
        "T3": "cube",
        "T4": "expressway",
        "T5": "qos",
        "T6": "ucce",
        "T7": "migration",
        "T8": "trouble",
    }[tid]


SHEETS = {
    "sip": ("SIP in one page", ["A transaction is not a dialog.", "180 is alerting. 200 accepts. ACK finishes a 2xx.", "REGISTER stores a Contact.", "Early offer puts SDP in the INVITE.", "PRACK answers a reliable 183.", "RTP may skip the proxy.", "Source: RFC 3261, RFC 3264, RFC 3262."]),
    "dial-plan": ("CUCM dial plan", ["A CSS is an ordered list of partitions.", "First match in that order wins.", "Route pattern, route list, route group, gateway.", "Called and calling numbers are different fields.", "A trunk in service can still have an empty CSS.", "Source: Cisco Unified Communications Manager documentation."]),
    "cube": ("CUBE, dial peers, SRST", ["CUBE is a B2BUA with two dialogs.", "Confirm inbound match order for your IOS release.", "Longest match, then preference, on outbound peers.", "SRST is a subset dial plan, not a clone of CUCM.", "A local gateway toward Webex Calling is a different peer.", "Source: Cisco CUBE and SRST documentation. Confirm call caps."]),
    "expressway": ("Expressway and MRA", ["C inside, E at the edge, traversal zone between them.", "MRA still registers to CUCM.", "Do not copy a port list from memory.", "Signaling up does not prove media.", "Source: Cisco Expressway deployment guides."]),
    "qos": ("Voice QoS", ["EF is DSCP 46.", "Cisco signaling designs often use CS3. RFC 4594 points signaling at CS5.", "G.711 at 20 ms is about 80 kbit/s at layer 3.", "LLQ schedules bandwidth. It does not create it.", "CUCM locations do not mark packets.", "G.114 is the usual 150 ms planning citation. Confirm the current text."]),
    "ucce": ("UCCE bridge", ["Ingress, script, queue, and agent are different stages.", "A label must be a number CUCM can route.", "Queue audio is not an agent ringing.", "Webex Contact Center is a different product.", "Source: Cisco UCCE design guides."]),
    "migration": ("Webex Calling migration", ["Calling and Dedicated Instance are different offers.", "Dual-run a number you can return.", "Save the old route before you edit it.", "SRST does not automatically cover Webex apps.", "Confirm survivability features on your subscription."]),
    "trouble": ("Troubleshooting habit", ["One hypothesis. One change.", "Read one SIP leg at a time.", "A 200 OK does not prove two-way audio.", "Compare SDP addresses with the packets you see.", "Revert if the symptom does not move."]),
    "e911": ("Emergency calling note", ["Emergency calling is regional law plus a carrier design.", "A lab ladder is not an emergency plan.", "Test callback identity on the path you will use.", "Confirm Kari's Law and RAY BAUM's Act only as US examples, and confirm your own jurisdiction.", "Source: your carrier and local regulation. Confirm before relying."]),
    "bandwidth": ("Bandwidth sketch", ["G.711 20 ms payload is 160 bytes.", "IP, UDP, and RTP add 40 bytes.", "Layer 3 is about 80 kbit/s.", "An 18-byte Ethernet header makes about 87.2 kbit/s.", "Size the priority queue from admitted calls.", "Formula: (payload + 40 + L2) x 8 x (1000 / ptime) / 1000."]),
    "ports-note": ("Ports, without a fake matrix", ["SIP is often 5060 and 5061. That is not a firewall design.", "Media ranges differ for phones, CUBE, and Expressway.", "Open the table in the guide for your version.", "Write source, destination, and direction.", "Confirm before relying."]),
    "evidence": ("Evidence pack", ["Time, calling number, called number.", "Hypothesis in one sentence.", "The ladder or the trace.", "The single change.", "The result, including a revert."]),
}


def emit_sheets() -> None:
    folder = ROOT / "downloads" / "sheets"
    folder.mkdir(parents=True, exist_ok=True)
    for slug, (title, lines) in SHEETS.items():
        items = "".join(f"<li>{esc(line)}</li>" for line in lines)
        doc = (
            "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\">"
            f"<title>{esc(title)}</title><link rel=\"stylesheet\" href=\"../../assets/css/footer.css\">"
            "<style>body{font-family:system-ui,sans-serif;margin:24px;background:#f8fafc;color:#0f172a}ul{font-size:1.15rem;line-height:1.5}</style>"
            f"</head><body><h1>{esc(title)}</h1><ul>{items}</ul>{footer()}</body></html>"
        )
        (folder / f"{slug}.html").write_text(doc, encoding="utf-8")


def emit_home(room_rows: list[dict], items: list[dict]) -> None:
    tiles = []
    for tid, name, blurb, color in TRACKS:
        count = sum(1 for room in room_rows if room["track"] == tid)
        tiles.append(
            f'<a class="track-tile" style="--card:{color}" href="tracks/{tid}.html"><h2>{esc(name)}</h2><p>{esc(blurb)}</p><p>{count} rooms</p></a>'
        )
    flows = sum(1 for item in items if item["kind"] == "flow")
    body = f"""
<section class="wrap hero-band">
<div>
<p class="kicker">CUCM · SIP · gateways · contact center</p>
<h1>Voice, then the dial plan, then the edge.</h1>
<p class="lede">A free study lab for Unified Communications: SIP, CUCM, CUBE, SRST, Expressway, voice QoS, UCCE, and a careful move toward Webex Calling. Figures that depend on a release are marked confirm before relying.</p>
<div class="actions">
<a class="btn" href="start.html">Start here</a>
<a class="ghost" href="diagrams.html">Diagrams</a>
<a class="ghost" href="downloads.html">Downloads</a>
<a class="ghost" href="campus/uc-lab-free-university.html">Deep campus</a>
</div>
</div>
<div class="diagram-frame"><img src="assets/diagrams/university/uc-stack.svg" alt="Teaching UC stack"></div>
</section>
<section class="wrap">
<div class="stat-row" aria-label="Counts from this repository">
<div class="stat"><b data-count="{len(room_rows)}">{len(room_rows)}</b><span>rooms</span></div>
<div class="stat"><b data-count="{len(items)}">{len(items)}</b><span>diagrams</span></div>
<div class="stat"><b data-count="{flows}">{flows}</b><span>flows</span></div>
<div class="stat"><b data-count="8">8</b><span>tracks</span></div>
</div>
<h2>Eight paths</h2>
<div class="track-map">{''.join(tiles)}</div>
<p class="lede">The older flagship studio remains at <a href="flagship/index.html">flagship/index.html</a>. The 580-section campus remains beside it. This front door is the round-2 course.</p>
</section>
"""
    write_page("index.html", "UC Lab Free University", "SIP, CUCM, CUBE, SRST, Expressway, QoS, UCCE, and Webex Calling migration.", "home", body)


def emit_start(room_rows: list[dict]) -> None:
    ten = room_rows[:4]
    links = "".join(f'<li><a href="rooms/{room["slug"]}.html">{esc(room["title"])}</a> — {esc(room["five"][0])}</li>' for room in ten)
    full = "".join(
        f'<li><a href="tracks/{tid}.html">{esc(name)}</a> — {esc(blurb)}</li>' for tid, name, blurb, _color in TRACKS
    )
    body = page_wrap(
        f"""
<h1>Start here</h1>
<section id="ten"><h2>Finish in 10 minutes</h2>
<p>Read four SIP rooms. You will be able to tell a transaction from a dialog and a 180 from a 200.</p>
<ol>{links}</ol>
<div class="room-downloads"><a class="dl-btn" href="downloads/sheets/sip.html">SIP sheet</a></div>
</section>
<section id="path"><h2>Full course</h2>
<p>Fundamentals, the dial plan, the gateway, the edge, QoS, the contact-center bridge, migration, then the troubleshooting habit.</p>
<ol>{full}</ol>
</section>
<section><h2>Certifications</h2>
<p>Cisco's collaboration exam names change. <a href="https://www.cisco.com/c/en/us/training-events/training-certifications.html">Confirm the current title</a> before you pay. This lab is study material, not an exam voucher.</p>
</section>
"""
    )
    write_page("start.html", "Start here", "Ten minutes or the full UC course.", "learn", body)


def emit_diagram_indexes(items: list[dict]) -> None:
    cards = []
    flows = []
    for item in items:
        cards.append(
            f'<article class="room-card"><h2>{esc(item["title"])}</h2><div class="diagram-frame"><img src="assets/diagrams/university/{item["slug"]}.svg" alt="{esc(item["title"])}"></div>'
            f'<div class="room-downloads"><a class="dl-btn" href="assets/diagrams/university/{item["slug"]}.svg" download>SVG</a>'
            f'<a class="dl-btn" href="downloads/diagrams/{item["slug"]}.png" download>PNG</a>'
            f'<a class="dl-btn" href="downloads/diagrams/{item["slug"]}.html" download>HTML</a></div></article>'
        )
        if item["kind"] == "flow":
            flows.append(cards[-1])
    write_page("diagrams.html", "Diagrams", "UC diagrams as SVG, PNG, and HTML.", "diagrams", page_wrap(f"<h1>Diagrams</h1><p>{len(items)} drawings.</p><div class=\"card-grid\">{''.join(cards)}</div>"))
    write_page("flows.html", "Flows", "Animated UC call flows.", "flows", page_wrap(f"<h1>Flows</h1><p>{len(flows)} ladders with a moving packet. Reduced motion keeps every step visible in the SVG.</p><div class=\"card-grid\">{''.join(flows)}</div>"))


def emit_charts(room_rows: list[dict], items: list[dict]) -> None:
    bars = []
    for tid, name, _blurb, color in TRACKS:
        count = sum(1 for room in room_rows if room["track"] == tid)
        width = count * 18
        bars.append(
            f'<div data-chart="rooms-{tid}"><span>{esc(name)} · {count}</span><div class="chart-bar" style="width:{width}px;background:{color}"></div></div>'
        )
    flows = sum(1 for item in items if item["kind"] == "flow")
    arches = len(items) - flows
    extra = f"""
<div data-chart="flows"><span>Animated flows · {flows}</span><div class="chart-bar" style="width:{flows * 8}px"></div></div>
<div data-chart="arches"><span>Still diagrams · {arches}</span><div class="chart-bar" style="width:{arches * 8}px"></div></div>
<div data-chart="g711"><span>G.711 layer 3 · 80 kbit/s</span><div class="chart-bar" style="width:160px"></div></div>
<div data-chart="g711-l2"><span>G.711 plus Ethernet · 87.2 kbit/s</span><div class="chart-bar" style="width:174px"></div></div>
"""
    body = page_wrap("<h1>Charts</h1><p>Counts from this repository, plus the standard G.711 sketch. No traffic and no revenue.</p>" + "".join(bars) + extra)
    write_page("charts.html", "Charts", "Counts from this UC lab.", "diagrams", body)


def emit_play() -> None:
    body = page_wrap(
        """
<h1>Play</h1>
<p>Three checks. Nothing is stored on a server.</p>
<div class="quiz" data-quiz data-answer="Alerting, not answer"><p>What is 180 Ringing?</p>
<button type="button" class="choice ghost" data-choice="Alerting, not answer">Alerting, not answer</button>
<button type="button" class="choice ghost" data-choice="The call is up">The call is up</button>
<p class="quiz-note" hidden>RFC 3261. The 200 accepts the session.</p></div>
<div class="quiz" data-quiz data-answer="DSCP 46"><p>What is EF?</p>
<button type="button" class="choice ghost" data-choice="DSCP 46">DSCP 46</button>
<button type="button" class="choice ghost" data-choice="A CUCM partition">A CUCM partition</button>
<p class="quiz-note" hidden>RFC 3246. Telephony uses this mark in RFC 4594.</p></div>
<div class="quiz" data-quiz data-answer="Two dialogs"><p>What does a B2BUA create?</p>
<button type="button" class="choice ghost" data-choice="Two dialogs">Two dialogs</button>
<button type="button" class="choice ghost" data-choice="One proxy transaction">One proxy transaction</button>
<p class="quiz-note" hidden>CUBE and CUCM on a trunk are B2BUAs. Count the Call-IDs.</p></div>
<div class="room-downloads"><a class="dl-btn" href="downloads/flashcards.html">Flashcards</a></div>
"""
    )
    write_page("play.html", "Play", "A short UC drill.", "play", body)


def emit_listen() -> None:
    body = page_wrap(
        """
<h1>Listen</h1>
<p>The phone bar and the guide can read this page aloud. Recorded desk notes from the flagship studio are optional and separate from the guide voice.</p>
<audio controls preload="none" src="flagship/audio/architect-tour.mp3"><a href="flagship/audio/architect-tour.mp3">Tour notes</a></audio>
<audio controls preload="none" src="flagship/audio/architect-practice.mp3"><a href="flagship/audio/architect-practice.mp3">Practice notes</a></audio>
<p><a href="flagship/audio/scripts/architect-tour.md">Tour script</a></p>
<div class="room-downloads"><button type="button" class="dl-btn" data-listen>Read this page</button></div>
"""
    )
    write_page("listen.html", "Listen", "Read-along and recorded notes.", "listen", body)


def emit_ecosystem(room_rows: list[dict]) -> None:
    terms = []
    for room in room_rows:
        for term, meaning in room["glossary"]:
            terms.append(f"<li><strong>{esc(term)}</strong> — {esc(meaning)}</li>")
    body = page_wrap(
        f"""
<h1>Ecosystem</h1>
<section><h2>Glossary</h2><ul>{''.join(terms)}</ul></section>
<section><h2>Mind map</h2><div class="diagram-frame"><img src="assets/diagrams/university/glossary-map.svg" alt="Glossary mind map"></div></section>
<section><h2>Sister technologies</h2><p>SIP, RTP, CUCM dial plan, IOS dial peers, Expressway traversal, DiffServ, and UCCE scripts are sisters. Learn the object each word names.</p></section>
<section><h2>Integration map</h2><div class="diagram-frame"><img src="assets/diagrams/university/integration-map.svg" alt="Integration map">
<p>CUCM, UCCE, and Webex Calling meet on explicit trunks and labels. A shared vendor is not a shared dial plan.</p></section>
<section><h2>Future hooks</h2><div class="diagram-frame"><img src="assets/diagrams/university/future-hooks.svg" alt="Future hooks"></div>
<p>Releases, carriers, and emergency law stay outside this lab until you confirm them.</p></section>
<div class="room-downloads"><a class="dl-btn" href="assets/diagrams/university/glossary-map.svg" download>SVG</a></div>
"""
    )
    write_page("ecosystem.html", "Ecosystem", "Glossary and bridges for the UC lab.", "ecosystem", body)


def emit_help_legal() -> None:
    help_body = page_wrap(
        """
<h1>Help</h1>
<section><h2>Menu</h2><p>The Menu button is at the top left. The drawer slides in. Escape or a tap on the dimmed page closes it. On a phone the same Menu is the left side of the bottom bar.</p></section>
<section><h2>Course</h2><p>Learn opens a ten-minute SIP path and the eight-track course. Each room has a five-minute block, a drawing, a worked example, a quiz, and sources.</p></section>
<section><h2>Bot</h2><p>The monkey greets once after the tour, then sits at the right. Drag it. It can read the page aloud, take a typed question, or try the mic. Ambient sound is off until you turn it on. After a few quiet minutes it may offer help. Not now dismisses that offer. Stop offering keeps it quiet.</p>
<p><button type="button" data-tour-open>Replay the tour</button></p></section>
<section><h2>Downloads</h2><p>Every room has SVG, PNG, HTML, and a cheat sheet. The Downloads page lists the deck, the cards, the templates, and one zip.</p></section>
<div class="room-downloads"><a class="dl-btn" href="downloads.html">Open downloads</a></div>
"""
    )
    legal_body = page_wrap(
        f"""
<h1>Legal and credits</h1>
<section><h2>Copyright</h2><p>The words and drawings in this round-2 course are a student project, © 2026 CypherMonkeyLabs. The deep campus and flagship keep their own notices.</p></section>
<section><h2>Trademarks</h2><p>Cisco, CUCM, CUBE, SRST, Expressway, Unified Contact Center Enterprise, Webex, and Webex Calling are trademarks of their owners. This lab is not affiliated with or endorsed by them.</p></section>
<section><h2>Licences</h2><p>Code written for this course is MIT, matching the repository licence. Vendored libraries under flagship/assets/vendor keep MIT, ISC, and BSD-style notices beside the files. Drawings in this course are shared CC BY-NC-SA unless a file says otherwise. RFC text stays with the IETF and the RFC Editor.</p></section>
<section><h2>Privacy</h2><p>There is no account and no tracker. Progress, the tour flag, voice settings, and badge names stay in this browser.</p></section>
<section><h2>Accessibility</h2><p>Display sets font size and font colour. Bright is the default. Dark is optional. The tour and the drawer work from the keyboard. Escape closes them.</p></section>
<section><h2>Removal</h2><p>Write via <a href="{CONTACT}">{CONTACT}</a> and the page will be corrected or removed.</p></section>
"""
    )
    write_page("help.html", "Help", "How to use the UC lab.", "help", help_body)
    write_page("legal.html", "Legal and credits", "Copyright, trademarks, privacy, and removal.", "help", legal_body)


def emit_quizzes(room_rows: list[dict]) -> None:
    blocks = []
    for room in room_rows:
        for prompt, why, choices, answer in room["quiz"]:
            buttons = "".join(
                f'<button type="button" class="choice ghost" data-choice="{esc(choice)}">{esc(choice)}</button>' for choice in choices
            )
            blocks.append(
                f'<div class="quiz" data-quiz data-answer="{esc(answer)}"><p><a href="rooms/{room["slug"]}.html">{esc(room["title"])}</a>. {esc(prompt)}</p>{buttons}<p class="quiz-note" hidden>{esc(why)}</p></div>'
            )
    write_page("quizzes.html", "Quizzes", "Room quizzes in one list.", "play", page_wrap(f"<h1>Quizzes</h1>{''.join(blocks)}"))


def cards_for(room_rows: list[dict]) -> list[dict]:
    cards = []
    for room in room_rows:
        for term, meaning in room["glossary"]:
            cards.append({"front": term, "back": meaning, "source": room["sources"][0][0]})
        cards.append({"front": room["title"], "back": room["five"][0], "source": room["sources"][0][0]})
        for prompt, why, _choices, answer in room["quiz"]:
            cards.append({"front": prompt, "back": f"{answer}. {why}", "source": room["sources"][0][0]})
    return cards


def emit_flashcards(cards: list[dict]) -> None:
    folder = ROOT / "downloads"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "flashcards.json").write_text(json.dumps({"cards": cards}, indent=2), encoding="utf-8")
    rows = "".join(
        f"<article><h2>{esc(card['front'])}</h2><p>{esc(card['back'])}</p><p>Source: {esc(card['source'])}</p></article>"
        for card in cards
    )
    doc = (
        "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\"><title>UC flashcards</title>"
        "<link rel=\"stylesheet\" href=\"../assets/css/footer.css\">"
        "<style>body{font-family:system-ui,sans-serif;margin:24px;background:#fff;color:#0f172a}article{break-inside:avoid;border:1px solid #99f6e4;border-radius:12px;padding:12px;margin:8px 0}</style>"
        f"</head><body><h1>UC flashcards</h1>{rows}{footer()}</body></html>"
    )
    (folder / "flashcards.html").write_text(doc, encoding="utf-8")
    (folder / "flashcards-print.html").write_text(doc, encoding="utf-8")
    write_page(
        "flashcards.html",
        "Flashcards",
        "Know or again, in this browser.",
        "play",
        page_wrap(
            f"<h1>Flashcards</h1><p>{len(cards)} cards. The deck file is a download. This page shows the first questions from the same list.</p>"
            + "".join(
                f'<article class="room-card"><h2>{esc(card["front"])}</h2><p>{esc(card["back"])}</p></article>'
                for card in cards[:12]
            )
            + '<div class="room-downloads"><a class="dl-btn" href="downloads/flashcards.json" download>JSON</a><a class="dl-btn" href="downloads/flashcards.html">HTML</a><a class="dl-btn" href="downloads/flashcards.pdf">PDF</a></div>'
        ),
    )


def emit_office(cards: list[dict]) -> None:
    from docx import Document
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    templates = ROOT / "downloads" / "templates"
    templates.mkdir(parents=True, exist_ok=True)
    sheets = ROOT / "downloads" / "sheets"

    def pdf(path: Path, title: str, lines: list[str]) -> None:
        c = canvas.Canvas(str(path), pagesize=letter)
        width, height = letter
        y = height - 54
        c.setFont("Helvetica-Bold", 16)
        c.drawString(48, y, title[:90])
        y -= 28
        c.setFont("Helvetica", 11)
        for line in lines:
            for chunk in re.findall(r".{1,90}(?:\s|$)", line) or [line]:
                if y < 72:
                    c.showPage()
                    c.setFont("Helvetica", 11)
                    y = height - 54
                c.drawString(48, y, chunk.strip())
                y -= 16
        y -= 12
        note = "Independent free learning-only student project. Trademarks belong to their owners. Not affiliated or endorsed. Contact: https://cyphermonkeylabs.com/#contact. Nothing is sold."
        for chunk in re.findall(r".{1,90}(?:\s|$)", note):
            c.drawString(48, y, chunk.strip())
            y -= 14
        c.save()

    for slug, (title, lines) in SHEETS.items():
        pdf(sheets / f"{slug}.pdf", title, lines)
    pdf(ROOT / "downloads" / "flashcards.pdf", "UC flashcards", [f"{card['front']} — {card['back']}" for card in cards])

    template_text = {
        "evidence-pack": ["Evidence pack", "Hypothesis:", "Time:", "Calling number:", "Called number:", "One change:", "Result:", "Revert plan:"],
        "cutover-checklist": ["Cutover checklist", "Number moved:", "Old route saved:", "Test call passed:", "Caller identity checked:", "Rollback owner:", "Emergency test window:"],
        "dial-plan-worksheet": ["Dial plan worksheet", "Partition:", "CSS order:", "Pattern:", "Route list:", "Gateway or trunk:", "Called transform:", "Calling transform:"],
    }
    for slug, lines in template_text.items():
        html_doc = (
            "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\">"
            f"<title>{esc(lines[0])}</title><link rel=\"stylesheet\" href=\"../../assets/css/footer.css\"></head><body>"
            f"<h1>{esc(lines[0])}</h1><ul>" + "".join(f"<li>{esc(line)}</li>" for line in lines[1:]) + f"</ul>{footer()}</body></html>"
        )
        (templates / f"{slug}.html").write_text(html_doc, encoding="utf-8")
        pdf(templates / f"{slug}.pdf", lines[0], lines[1:])
        document = Document()
        document.add_heading(lines[0], 0)
        for line in lines[1:]:
            document.add_paragraph(line)
        document.add_paragraph("Independent, free, learning-only student project. Trademarks belong to their owners. Not affiliated or endorsed. Concerns via https://cyphermonkeylabs.com/#contact. Nothing is sold.")
        document.save(templates / f"{slug}.docx")

    pres = Presentation()
    slides = [
        ("UC Lab Free University", "SIP, CUCM, CUBE, SRST, Expressway, QoS, UCCE, Webex Calling migration."),
        ("SIP", "A transaction is not a dialog. 180 alerts. 200 accepts. ACK finishes."),
        ("Dial plan", "Partitions, ordered CSS, route list, route group."),
        ("CUBE", "Two dialogs. Read both legs."),
        ("SRST", "A planned subset when CUCM is unreachable."),
        ("Expressway", "C, E, and a traversal zone. Confirm ports."),
        ("QoS", "EF is DSCP 46. LLQ does not create bandwidth."),
        ("UCCE", "Script, label, then a number CUCM can route."),
        ("Migration", "Dual-run a number you can return."),
        ("Troubleshooting", "One hypothesis. One change. Save the ladder."),
        ("Disclaimer", "Independent free learning project. Not affiliated or endorsed. Contact cyphermonkeylabs.com. Nothing is sold."),
    ]
    for title, line in slides:
        layout = pres.slide_layouts[1]
        slide = pres.slides.add_slide(layout)
        slide.shapes.title.text = title
        slide.placeholders[1].text = line
        for shape in slide.shapes:
            if not shape.has_text_frame:
                continue
            for paragraph in shape.text_frame.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(20)
                    run.font.name = "Calibri"
    pres.save(ROOT / "downloads" / "uc-lab-deck.pptx")


def emit_catalog(room_rows: list[dict]) -> None:
    pages = [
        {"title": "Home", "href": "index.html", "blurb": "Eight tracks", "keys": ["home", "start"]},
        {"title": "Learn", "href": "start.html", "blurb": "Ten minutes or the full course", "keys": ["learn", "course"]},
        {"title": "Diagrams", "href": "diagrams.html", "blurb": "Drawings", "keys": ["diagram"]},
        {"title": "Flows", "href": "flows.html", "blurb": "Ladders", "keys": ["flow", "ladder"]},
        {"title": "Play", "href": "play.html", "blurb": "Drill", "keys": ["play", "quiz"]},
        {"title": "Listen", "href": "listen.html", "blurb": "Read along", "keys": ["listen", "audio"]},
        {"title": "Downloads", "href": "downloads.html", "blurb": "Exports", "keys": ["download", "export"]},
        {"title": "Ecosystem", "href": "ecosystem.html", "blurb": "Glossary", "keys": ["glossary", "ecosystem"]},
        {"title": "Help", "href": "help.html", "blurb": "Tour and bot", "keys": ["help", "tour"]},
        {"title": "Legal", "href": "legal.html", "blurb": "Credits", "keys": ["legal", "privacy"]},
    ]
    for room in room_rows:
        pages.append(
            {
                "title": room["title"],
                "href": f"rooms/{room['slug']}.html",
                "blurb": room["five"][0],
                "keys": [room["slug"].replace("-", " "), room["id"].lower(), track_key(room["track"])],
            }
        )
    path = ROOT / "assets" / "data"
    path.mkdir(parents=True, exist_ok=True)
    (path / "catalog.json").write_text(json.dumps({"pages": pages}, indent=2), encoding="utf-8")


def track_key(tid: str) -> str:
    for row in TRACKS:
        if row[0] == tid:
            return row[1].lower()
    return tid


def emit_downloads(items: list[dict]) -> None:
    rows = []
    interesting = []
    for folder in (ROOT / "downloads", ROOT / "assets" / "diagrams" / "university"):
        for path in sorted(folder.rglob("*")):
            if not path.is_file():
                continue
            if path.suffix.lower() not in {".html", ".pdf", ".png", ".svg", ".json", ".docx", ".pptx", ".zip"}:
                continue
            interesting.append(path)
    # The zip is added after this table is first built. Include planned zip if present.
    for path in interesting:
        text = ""
        if path.suffix.lower() in {".html", ".svg", ".json"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
        has_note = "learning-only" in text or path.suffix.lower() in {".pdf", ".docx", ".pptx", ".png", ".zip"}
        rel = path.relative_to(ROOT).as_posix()
        rows.append(f"<tr><td>{esc(rel)}</td><td>{path.stat().st_size}</td><td>{'yes' if has_note else 'check'}</td></tr>")
    body = page_wrap(
        f"""
<h1>Downloads</h1>
<p><a class="btn" href="index.html">Open app</a> <a class="ghost" href="{ORG}">View repo</a></p>
<div class="room-downloads">
<a class="dl-btn" href="downloads/uc-lab-deck.pptx" download>PPTX deck</a>
<a class="dl-btn" href="downloads/flashcards.json" download>Flashcards JSON</a>
<a class="dl-btn" href="downloads/flashcards.pdf" download>Flashcards PDF</a>
<a class="dl-btn" href="downloads/flashcards.html">Flashcards HTML</a>
<a class="dl-btn" href="downloads/templates/evidence-pack.docx" download>Evidence DOCX</a>
<a class="dl-btn" href="downloads/uc-lab-university.zip" download>Everything zip</a>
</div>
<h2>Cheat sheets</h2>
<div class="room-downloads">
{''.join(f'<a class="dl-btn" href="downloads/sheets/{esc(slug)}.html">{esc(slug)} HTML</a><a class="dl-btn" href="downloads/sheets/{esc(slug)}.pdf">{esc(slug)} PDF</a><a class="dl-btn" href="downloads/sheets/{esc(slug)}.png">{esc(slug)} PNG</a>' for slug in SHEETS)}
</div>
<h2>Templates</h2>
<div class="room-downloads">
<a class="dl-btn" href="downloads/templates/evidence-pack.html">Evidence HTML</a>
<a class="dl-btn" href="downloads/templates/cutover-checklist.pdf">Cutover PDF</a>
<a class="dl-btn" href="downloads/templates/dial-plan-worksheet.docx">Dial plan DOCX</a>
</div>
<h2>Headless test table</h2>
<p>Sizes are bytes on disk after the build. HTML and SVG rows contain the learning-only disclaimer. PDF, DOCX, and PPTX include the same note in the document text. PNG files are raster copies of those pages.</p>
<div class="table-wrap"><table class="plain"><thead><tr><th>File</th><th>Bytes</th><th>Disclaimer</th></tr></thead><tbody>
{''.join(rows)}
</tbody></table></div>
<p>{len(items)} diagrams are linked from <a href="diagrams.html">Diagrams</a>.</p>
"""
    )
    write_page("downloads.html", "Downloads", "Sheets, cards, templates, and the zip.", "downloads", body)


def render_pngs() -> None:
    import subprocess
    from concurrent.futures import ThreadPoolExecutor

    pairs = []
    for folder in (ROOT / "downloads" / "diagrams", ROOT / "downloads" / "sheets"):
        for html_path in sorted(folder.glob("*.html")):
            pairs.append((html_path, html_path.with_suffix(".png")))

    def shot(pair: tuple[Path, Path]) -> None:
        html_path, png_path = pair
        profile = f"/tmp/ucpng-{png_path.stem}"
        subprocess.run(
            [
                "/usr/bin/google-chrome-stable",
                "--headless=new",
                "--no-sandbox",
                "--disable-gpu",
                f"--user-data-dir={profile}",
                "--hide-scrollbars",
                "--window-size=1100,800",
                f"--screenshot={png_path}",
                html_path.as_uri(),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(shot, pairs))


def emit_zip() -> None:
    target = ROOT / "downloads" / "uc-lab-university.zip"
    include_roots = ["index.html", "start.html", "diagrams.html", "flows.html", "downloads.html", "help.html", "legal.html", "assets", "guide", "rooms", "tracks", "downloads", "sw.js", "manifest.webmanifest", "favicon.svg"]
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in include_roots:
            path = ROOT / name
            if path.is_file():
                archive.write(path, name)
            elif path.is_dir():
                for file in path.rglob("*"):
                    if not file.is_file():
                        continue
                    if "uc-lab-university.zip" in file.name:
                        continue
                    if file.suffix == ".png" and "screenshots" in file.parts:
                        continue
                    archive.write(file, file.relative_to(ROOT).as_posix())


def scrub_legacy() -> int:
    changed = 0
    email = re.compile(r"([A-Za-z0-9._%+-]+)@([A-Za-z0-9-]+\.[A-Za-z]{2,})")
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".html", ".md", ".js", ".css", ".json"}:
            continue
        if any(part in {".git", "vendor", "node_modules"} for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        original = text
        if path.suffix.lower() == ".html" and "data-uc-page" not in text:
            text = re.sub(r'<nav class="brand-links".*?</nav>', "", text, flags=re.S)
            text = email.sub(r"\1 at \2", text)
        text = text.replace("https://github.com/cipher0x9", ORG)
        text = re.sub(r"https://x\.com/[^\s\"'<)]+", WEB, text)
        text = re.sub(r"https://huggingface\.co/[^\s\"'<)]+", WEB, text)
        text = re.sub(r"https://(www\.)?linkedin\.com/[^\s\"'<)]+", WEB, text)
        text = re.sub(r"mailto:[^\s\"'<)]+", CONTACT, text)
        if path.suffix.lower() == ".html" and "data-uc-page" not in text and "learning-only student project" not in text:
            depth = len(path.relative_to(ROOT).parts) - 1
            pre = "../" * depth
            snippet = (
                f'<p class="uc-legacy-dl"><a href="{pre}downloads.html">Download exports</a></p>'
                + footer()
            )
            if "</body>" in text:
                text = text.replace("</body>", snippet + "</body>", 1)
            else:
                text += snippet
        if text != original:
            path.write_text(text, encoding="utf-8")
            changed += 1
    return changed


def main() -> None:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    items = build_diagrams()
    room_rows = rooms()
    emit_diagrams(items)
    emit_sheets()
    emit_rooms(room_rows)
    emit_tracks(room_rows)
    emit_home(room_rows, items)
    emit_start(room_rows)
    emit_diagram_indexes(items)
    emit_charts(room_rows, items)
    emit_play()
    emit_listen()
    emit_ecosystem(room_rows)
    emit_help_legal()
    emit_quizzes(room_rows)
    card_rows = cards_for(room_rows)
    emit_flashcards(card_rows)
    emit_office(card_rows)
    emit_catalog(room_rows)
    render_pngs()
    emit_downloads(items)
    scrubbed = scrub_legacy()
    emit_zip()
    print(f"rooms {len(room_rows)} diagrams {len(items)} cards {len(card_rows)} scrubbed {scrubbed}")


if __name__ == "__main__":
    main()
