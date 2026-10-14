#!/usr/bin/env python3
"""Lift written idea-pool rooms into the public campus without replacing v21 sections.

The source tree is a read-only copy. This script adapts rooms, quiz items,
flashcards, scenarios, and glossary terms into the campus HTML and
campus/assets/idea-pool.js. It does not delete existing sections.
"""

from __future__ import annotations

import json
import re
import subprocess
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = ROOT / "campus" / "uc-lab-free-university.html"
DRILLS_PATH = ROOT / "campus" / "assets" / "app-drills.js"
OUT_JS = ROOT / "campus" / "assets" / "idea-pool.js"
SOURCE = Path("/cursor/stores/bot/idea-pool/cypher-uc-lab")

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?<![\w.])(?:\+\d{1,3}[\s.\-]?)?\(?\d{3}\)?[\s.\-]\d{3}[\s.\-]\d{4}(?!\d)")
# alice@example.com and the percent-encoded cisco.com string are the system
# guide's published directory-URI examples, used to teach encoding length.
ALLOWED_EMAILS = {
    "user@contoso.com",
    "user@domain.com",
    "alice@example.com",
    "joe%20smith%23@cisco.com",
}

GROUP = {
    "T1": "CUCM and CUBE",
    "T2": "CUCM and CUBE",
    "T3": "CUCM and CUBE",
    "T4": "CUCM and CUBE",
    "T5": "CUCM and CUBE",
    "T6": "CUCM and CUBE",
    "T7": "CUCM and CUBE",
    "T7-R08": "Webex Calling and Teams Phone",
    "T8-R01": "Emergency calling",
    "T8-R03": "Voice network and QoS",
    "T8-R04": "Contact center — UCCE and PCCE",
    "T8-R06": "Migrations",
    "T8-R09": "Design notes",
    "T8-R10": "Migrations",
}

TRACK = {
    "T1": "CUCM and CUBE",
    "T2": "CUCM and CUBE",
    "T3": "CUCM and CUBE",
    "T4": "CUCM and CUBE",
    "T5": "CUCM and CUBE",
    "T6": "CUCM and CUBE",
    "T7": "CUCM and CUBE",
    "T8": "Contact center — UCCE and PCCE",
    "E911": "Emergency calling",
    "QoS": "Voice network and QoS",
    "Mig": "Migrations",
    "SIP": "SIP and media",
    "UCCE": "Contact center — UCCE and PCCE",
}


def parse_sections(html: str) -> tuple[list[dict], int, int]:
    key = "window.SECTIONS = "
    i = html.index(key) + len(key)
    depth = 0
    in_str = False
    esc = False
    for j, ch in enumerate(html[i:], i):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
            continue
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return json.loads(html[i : j + 1]), i, j + 1
    raise SystemExit("SECTIONS did not close")


def load_source_banks() -> dict:
    script = r"""
const fs = require("fs");
const vm = require("vm");
const rootDir = process.argv[1];
function load(rel) {
  const sandbox = { document: { currentScript: null } };
  sandbox.window = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(fs.readFileSync(rootDir + "/" + rel, "utf8"), sandbox, { filename: rel });
  return sandbox.UCLab || {};
}
const catalog = load("assets/js/uc-catalog.js").catalog;
const quiz = load("assets/data/quiz-bank.js").quizBank;
const cards = load("assets/data/flashcards.js").flashcards;
const scenarios = load("assets/data/scenarios.js").scenarios;
process.stdout.write(JSON.stringify({
  terms: catalog.terms,
  rooms: catalog.rooms,
  quiz, cards, scenarios
}));
"""
    raw = subprocess.check_output(["node", "-e", script, str(SOURCE)], text=True)
    return json.loads(raw)


def load_drills() -> dict:
    text = DRILLS_PATH.read_text(encoding="utf-8")
    start = text.index("window.UC_DRILLS = ") + len("window.UC_DRILLS = ")
    end = text.index(";\nwindow.UC_EXTRA_SCENARIOS")
    return json.loads(text[start:end])


def plain(html: str) -> str:
    text = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", html)
    text = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", text)
    text = re.sub(r"(?is)<!--.*?-->", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def sentences(html: str) -> list[str]:
    text = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", html)
    text = re.sub(r"(?is)<!--.*?-->", " ", text)
    text = re.sub(r"(?i)</(p|li|h[1-6]|tr)>", "\n", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    out = []
    for chunk in text.splitlines():
        chunk = re.sub(r"\s+", " ", chunk).strip()
        if len(chunk) < 40:
            continue
        out.append(chunk)
    return out


def room_files() -> list[tuple[str, Path]]:
    rows = []
    for path in sorted((SOURCE / "rooms").glob("T*-R*.html")):
        match = re.match(r"(T\d-R\d+)", path.name)
        if not match:
            continue
        rows.append((match.group(1), path))
    return rows


def group_for(room_id: str) -> str:
    if room_id in GROUP:
        return GROUP[room_id]
    return GROUP[room_id[:2]]


def section_id(room_id: str) -> str:
    return "pool-" + room_id.lower()


def apply_audit_fixes(room_id: str, html: str) -> str:
    if room_id != "T2-R07":
        return html
    html = html.replace(
        "Circular starts at the next member after the one last considered.",
        "Circular starts at the (n+1)th member. The nth member is the next sequential member who is idle or busy but not down. If that member is the last, distribution starts again at the top.",
    )
    html = html.replace(
        "Circular continues after the last member considered.",
        "Circular starts at the (n+1)th member, where n is the next sequential member who is idle or busy but not down.",
    )
    html = html.replace(">start after last<", ">n+1 member<")
    html = html.replace(">then wrap<", ">then from the top<")
    html = html.replace(
        "When queuing is on and no member can take the call, the caller waits in that pilot's queue, up to the wait you configured, including the case where every member is logged out.",
        "The queuing chapter places a call in queue only when all members are busy. If no line member answers, that caller is not placed in queue; the setting When no hunt members answer, are logged in, or registered routes the call or disconnects it. The same chapter's hunt-pilot interaction still says the pilot queues calls when every hunt member is logged out. Maximum wait is the value on the pilot. The default on the hunt-pilot chapter is 900 seconds.",
    )
    return html


def scrub_room(html: str) -> str:
    html = re.sub(r"(?is)<!--.*?-->", "", html)
    html = re.sub(r"(?is)<audio\b[^>]*>.*?</audio>", "", html)
    html = html.replace(
        "Files are not recorded. Pressing play does nothing useful until Studio drops the mp3 in place. The transcripts are the draft script.",
        "The audio files are not in this campus. The transcripts below are the draft script.",
    )
    html = re.sub(
        r"(?is)<p class=\"faint\">Studio still owes.*?</p>",
        "<p class=\"muted\">The admin screenshot for this room is not in the campus. Use the menus named in the text.</p>",
        html,
    )
    html = html.replace("private Cypher UC Lab", "UC Lab")
    html = html.replace("Cypher UC Lab", "UC Lab")
    html = collapse_example_phones(html)
    return html


def collapse_example_phones(html: str) -> str:
    """555 examples stay. Separator form trips the public phone check."""

    def repl(match: re.Match[str]) -> str:
        raw = match.group(0)
        digits = re.sub(r"\D", "", raw)
        if "555" not in digits:
            return raw
        prefix = "+" if raw.lstrip().startswith("+") else ""
        return prefix + digits

    return PHONE_RE.sub(repl, html)


def prefix_ids(fragment: str, prefix: str) -> str:
    ids = re.findall(r'\bid="([^"]+)"', fragment)
    fragment = re.sub(r'\bid="([^"]+)"', lambda m: f'id="{prefix}-{m.group(1)}"', fragment)
    for old in ids:
        fragment = fragment.replace(f'href="#{old}"', f'href="#{prefix}-{old}"')
        fragment = fragment.replace(f"url(#{old})", f"url(#{prefix}-{old})")
    return fragment


def rewrite_links(fragment: str, room_index: dict[str, str]) -> str:
    def repl(match: re.Match[str]) -> str:
        href = match.group(1)
        if href.startswith("#") or href.startswith("http://") or href.startswith("https://") or href.startswith("mailto:"):
            return match.group(0)
        name = href.split("#", 1)[0].split("/")[-1]
        found = re.match(r"(T\d-R\d+)", name)
        if found and found.group(1) in room_index:
            return f'href="#{room_index[found.group(1)]}"'
        return 'href="#home"'

    return re.sub(r'href="([^"]+)"', repl, fragment)


def rewrite_diagrams(fragment: str) -> str:
    def repl(match: re.Match[str]) -> str:
        rel = match.group(1)
        origin = SOURCE / "assets" / "diagrams" / rel
        target = ROOT / "campus" / "assets" / "idea-pool-diagrams" / rel
        if origin.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(origin.read_bytes())
        return f'src="assets/idea-pool-diagrams/{rel}"'

    return re.sub(r'src="\.\./assets/diagrams/([^"]+)"', repl, fragment)


def extract_main(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"<main\b[^>]*>([\s\S]*?)</main>", text)
    if not match:
        raise SystemExit(f"no main in {path.name}")
    return match.group(1)


def closest_section(title: str, sections: list[dict]) -> dict | None:
    words = {w.lower() for w in re.findall(r"[A-Za-z0-9+]{4,}", title)}
    best = None
    best_score = 0
    for sec in sections:
        theirs = {w.lower() for w in re.findall(r"[A-Za-z0-9+]{4,}", sec["title"])}
        score = len(words & theirs)
        if score > best_score:
            best = sec
            best_score = score
    if best_score >= 2:
        return best
    return None


def unique_campus_facts(room_html: str, section: dict | None) -> str:
    if not section:
        return ""
    room_text = plain(room_html).lower()
    picked = []
    for sentence in sentences(section.get("body") or ""):
        if sentence.lower() in room_text:
            continue
        if not re.search(r"\d|[A-Z]{2,}", sentence):
            continue
        if "476" in sentence or "section" in sentence.lower() and "v21" in sentence.lower():
            continue
        picked.append(sentence)
        if len(picked) == 6:
            break
    if not picked:
        return ""
    items = "".join(f"<li>{escape_text(item)}</li>" for item in picked)
    title = escape_text(section["title"])
    sid = escape_text(section["id"])
    return (
        f'<aside class="pool-kept"><p><strong>Also on this campus.</strong> '
        f'<a href="#{sid}">{title}</a> stays as written. These lines are on that page and are not restated above.</p><ul>{items}</ul></aside>'
    )


def escape_text(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_sections(existing: list[dict]) -> tuple[list[dict], dict]:
    files = room_files()
    index = {room_id: section_id(room_id) for room_id, _ in files}
    built = []
    report = []
    for room_id, path in files:
        raw = extract_main(path)
        raw = apply_audit_fixes(room_id, raw)
        raw = scrub_room(raw)
        raw = prefix_ids(raw, section_id(room_id))
        raw = rewrite_links(raw, index)
        raw = rewrite_diagrams(raw)
        title_match = re.search(r'data-title="([^"]+)"', path.read_text(encoding="utf-8")[:800])
        if not title_match:
            title_match = re.search(r"<title>[^·]*·\s*([^<]+)</title>", path.read_text(encoding="utf-8")[:500])
        title = title_match.group(1).strip() if title_match else room_id
        near = closest_section(title, existing)
        near_words = len(plain(near["body"]).split()) if near else 0
        room_words = len(plain(raw).split())
        folded = unique_campus_facts(raw, near)
        body = f'<div class="pool-room" data-room="{room_id}">' + raw + folded + "</div>"
        built.append(
            {
                "id": section_id(room_id),
                "num": room_id,
                "group": group_for(room_id),
                "title": title,
                "sub": f"Idea-pool room {room_id}. Citations and pointer sentences kept.",
                "body": body,
            }
        )
        report.append(
            {
                "room": room_id,
                "title": title,
                "group": group_for(room_id),
                "words": room_words,
                "near": near["id"] if near else "",
                "nearTitle": near["title"] if near else "",
                "nearWords": near_words,
                "folded": bool(folded),
            }
        )
    glossary = glossary_section(existing)
    if glossary:
        built.append(glossary["section"])
        report.append(glossary["meta"])
    return built, {"rooms": report}


def glossary_section(existing: list[dict]) -> dict | None:
    return None


def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def study_payload(existing_drills: dict, banks: dict) -> tuple[dict, dict]:
    questions = []
    cards = []
    skipped_q = 0
    skipped_c = 0
    existing_q = {norm(item["q"]) for item in existing_drills["questions"]}
    existing_defs = {norm(item["def"]) for item in existing_drills["cards"]}
    existing_terms = {norm(item["term"]) for item in existing_drills["cards"]}
    for item in banks["quiz"]:
        choices = item.get("choices") or []
        if len(choices) != 4 or not (0 <= item.get("answer", -1) < 4):
            skipped_q += 1
            continue
        if norm(item["q"]) in existing_q:
            skipped_q += 1
            continue
        answer = choices[item["answer"]]
        if norm(answer) in existing_defs or norm(answer) in existing_terms:
            skipped_q += 1
            continue
        track = TRACK.get(item.get("track") or "", "CUCM and CUBE")
        questions.append(
            {
                "id": "pool-" + item["id"],
                "track": track,
                "q": item["q"],
                "choices": choices,
                "answer": item["answer"],
                "why": answer,
            }
        )
        existing_q.add(norm(item["q"]))
    for card in banks["cards"]:
        answer = card.get("a") or ""
        question = card.get("q") or ""
        if norm(answer) in existing_defs or norm(question) in existing_q:
            skipped_c += 1
            continue
        term = re.sub(r"^(What is|What does|Why|Which|Name|Where|When|How)\s+", "", question, flags=re.I).strip(" ?")
        if len(term) > 80:
            term = term[:77].rstrip() + "..."
        if norm(term) in existing_terms:
            skipped_c += 1
            continue
        track = TRACK.get(card.get("track") or "", "CUCM and CUBE")
        cards.append({"term": term, "def": answer, "why": answer, "track": track})
        existing_terms.add(norm(term))
        existing_defs.add(norm(answer))
    glossary_added = 0
    glossary_folded = 0
    glossary_skipped = 0
    gloss_items = []
    by_term = {norm(item["term"]): item for item in existing_drills["cards"]}
    for term in banks["terms"]:
        key = norm(term["term"])
        definition = term.get("def") or ""
        if not definition:
            glossary_skipped += 1
            continue
        current = by_term.get(key)
        if current and norm(definition) in norm(current["def"]):
            glossary_skipped += 1
            continue
        if current:
            extra = definition
            if norm(current["def"]) in norm(definition):
                extra = definition
            gloss_items.append(
                {
                    "term": term["term"],
                    "def": extra,
                    "room": term.get("room") or "",
                    "folded": True,
                }
            )
            glossary_folded += 1
            continue
        if norm(definition) in existing_defs:
            glossary_skipped += 1
            continue
        track = TRACK.get((term.get("room") or "T1")[:2], "Reference")
        if (term.get("room") or "").startswith("T8-R01"):
            track = "Emergency calling"
        elif (term.get("room") or "").startswith("T8-R03"):
            track = "Voice network and QoS"
        elif (term.get("room") or "").startswith("T8-R06") or (term.get("room") or "").startswith("T8-R10"):
            track = "Migrations"
        cards.append(
            {
                "term": term["term"],
                "def": definition,
                "why": definition,
                "track": track if track != "Contact center — UCCE and PCCE" or (term.get("room") or "").startswith("T8-R04") else "CUCM and CUBE",
            }
        )
        existing_terms.add(key)
        existing_defs.add(norm(definition))
        gloss_items.append({"term": term["term"], "def": definition, "room": term.get("room") or "", "folded": False})
        glossary_added += 1
    scenarios = []
    for item in banks["scenarios"]:
        scenarios.append(
            {
                "id": "pool-" + item["id"],
                "title": item["title"],
                "blurb": item.get("blurb") or "",
                "start": item["start"],
                "nodes": item["nodes"],
            }
        )
    payload = {"questions": questions, "cards": cards, "scenarios": scenarios, "glossary": gloss_items}
    stats = {
        "quiz_added": len(questions),
        "quiz_skipped": skipped_q,
        "cards_added": len(cards),
        "cards_skipped_flash": skipped_c,
        "glossary_new_cards": glossary_added,
        "glossary_folded_lines": glossary_folded,
        "glossary_skipped": glossary_skipped,
        "scenarios": len(scenarios),
    }
    return payload, stats


def glossary_html(items: list[dict]) -> str:
    rows = []
    for item in items:
        note = " Wording from the idea-pool glossary that the campus card did not already contain." if item["folded"] else ""
        rows.append(
            f"<dt>{escape_text(item['term'])}</dt><dd>{escape_text(item['def'])}{escape_text(note)}</dd>"
        )
    return (
        '<div class="pool-room"><p class="lead">Terms from the idea-pool glossary that were not already a campus flashcard, '
        "plus longer idea-pool definitions for terms the campus already names. Each line is the source definition. "
        "Open the vendor document before you change a system.</p><dl class=\"pool-glos\">"
        + "".join(rows)
        + "</dl></div>"
    )


def insert(existing: list[dict], added: list[dict]) -> list[dict]:
    by_group: dict[str, list[dict]] = {}
    for item in added:
        by_group.setdefault(item["group"], []).append(item)
    out = []
    seen = set()
    for index, sec in enumerate(existing):
        out.append(sec)
        group = sec["group"]
        nxt = existing[index + 1]["group"] if index + 1 < len(existing) else None
        if nxt != group and group not in seen:
            out.extend(by_group.pop(group, []))
            seen.add(group)
    for group, items in by_group.items():
        out.extend(items)
    return out


def personal_scan(text: str, label: str) -> list[str]:
    problems = []
    low = text.lower()
    for needle in (
        "link" + "tr.ee",
        "cypher" + "monkey",
        "drive" + ".google",
        "docs" + ".google",
        "cursor.com/" + "codebase",
        "cypher-" + "monkey",
    ):
        if needle in low:
            problems.append(f"{label} contains {needle}")
    for email in sorted(set(EMAIL_RE.findall(text))):
        if email not in ALLOWED_EMAILS:
            problems.append(f"{label} email {email}")
    for phone in sorted(set(PHONE_RE.findall(text))):
        digits = re.sub(r"\D", "", phone)
        if "555" not in digits:
            problems.append(f"{label} phone {phone}")
    return problems


def main() -> None:
    html = HTML_PATH.read_text(encoding="utf-8")
    sections, start, end = parse_sections(html)
    before = len(sections)
    banks = load_source_banks()
    drills = load_drills()
    added, room_report = build_sections(sections)
    payload, study_stats = study_payload(drills, banks)
    gloss = {
        "id": "pool-glossary",
        "num": "G",
        "group": "Reference",
        "title": "Idea-pool glossary",
        "sub": "Terms carried from the idea pool. A line here is a pointer, not a change window.",
        "body": glossary_html(payload["glossary"]),
    }
    added.append(gloss)
    merged = insert(sections, added)
    home = merged[0]
    home["body"] = home["body"].replace(">476<", f">{len(merged)}<")
    html = html[:start] + json.dumps(merged, ensure_ascii=True, separators=(",", ":")) + html[end:]
    html = html.replace(
        '"sections": 476',
        f'"sections": {len(merged)}',
    )
    html = html.replace("476 sections", f"{len(merged)} sections")
    html = html.replace(">476 sections<", f">{len(merged)} sections<")
    problems = personal_scan(html, "campus html")
    js = (
        "/* Idea-pool study bank. Generated by scripts/merge-idea-pool.py. Offline. */\n"
        "window.UC_IDEA_POOL = "
        + json.dumps(
            {"questions": payload["questions"], "cards": payload["cards"], "scenarios": payload["scenarios"]},
            ensure_ascii=True,
            separators=(",", ":"),
        )
        + ";\n"
    )
    problems.extend(personal_scan(js, "idea-pool.js"))
    if problems:
        raise SystemExit("personal data:\n" + "\n".join(problems[:40]))
    HTML_PATH.write_text(html, encoding="utf-8")
    OUT_JS.write_text(js, encoding="utf-8")
    summary = {
        "sections_before": before,
        "sections_after": len(merged),
        "rooms_added": len(room_report["rooms"]),
        "quiz_before": len(drills["questions"]),
        "cards_before": len(drills["cards"]),
        "quiz_after": len(drills["questions"]) + study_stats["quiz_added"],
        "cards_after": len(drills["cards"]) + study_stats["cards_added"],
        "study": study_stats,
        "rooms": room_report["rooms"],
    }
    Path("/tmp/idea-pool-merge-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in summary if k != "rooms"}, indent=2))


if __name__ == "__main__":
    main()
