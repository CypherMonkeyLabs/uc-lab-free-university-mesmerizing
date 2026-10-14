#!/usr/bin/env python3
"""Split the monolithic campus into per-section modules.

Reads campus/uc-lab-free-university.html while it still contains
window.SECTIONS, applies the in-file body additions, and writes:

  campus/assets/curriculum/manifest.js
  campus/assets/curriculum/walks.js
  campus/assets/curriculum/sections/<id>.js

Safe to re-run only while the HTML still embeds window.SECTIONS.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = ROOT / "campus" / "uc-lab-free-university.html"
FLOW_PATH = ROOT / "campus" / "assets" / "flow-catalog.js"
OUT = ROOT / "campus" / "assets" / "curriculum"
SECTION_DIR = OUT / "sections"

CC_GROUPS = {
    "Contact center — UCCE and PCCE",
    "CCaaS and UCaaS platforms",
}
MIXED_GROUP = "Webex Calling and Teams Phone"
KEYWORD_GROUPS = {
    "Practice",
    "Troubleshooting",
    "Migrations",
    "Design notes",
    "Evidence habits",
    "Reference",
}
TEAMS_RE = re.compile(
    r"teams|direct routing|operator connect|microsoft|ms-teams",
    re.I,
)
WEBEX_RE = re.compile(r"webex", re.I)
CC_RE = re.compile(
    r"ucce|pcce|finesse|\bcvp\b|\bicm\b|cuic|genesys|five9|amazon connect|"
    r"wxcc|contact center|ccaas|\bnice\b|talkdesk|ccaip",
    re.I,
)

TRACK_SLUG = {
    "Start here": "start",
    "SIP and media": "sip",
    "CUCM and CUBE": "cucm-cube",
    "Webex Calling and Teams Phone": "cloud-calling",
    "Contact center — UCCE and PCCE": "ucce",
    "CCaaS and UCaaS platforms": "ccaas",
    "Emergency calling": "e911",
    "Voice network and QoS": "qos",
    "Migrations": "migrations",
    "Troubleshooting": "troubleshooting",
    "Evidence habits": "evidence",
    "Design notes": "design",
    "Practice": "practice",
    "Reference": "reference",
}

JOURNEYS = [
    {
        "id": "cisco-voice",
        "name": "Cisco Voice Core",
        "kicker": "CUCM · CUBE · SIP · QoS",
        "blurb": "Call control, the border, dial plan, emergency calling, and the proof habit underneath every other path.",
        "accent": 2,
    },
    {
        "id": "webex",
        "name": "Webex Calling",
        "kicker": "Calling Plan · Local Gateway · WxCC",
        "blurb": "Cloud PSTN choices, the local gateway, and the cutover evidence a Webex Calling deployment has to keep.",
        "accent": 1,
    },
    {
        "id": "teams",
        "name": "Teams Phone",
        "kicker": "Direct Routing · Operator Connect",
        "blurb": "Teams Phone paths, SBC pairing, and the acceptance tests that separate a trunk from a guess.",
        "accent": 3,
    },
    {
        "id": "contact-center",
        "name": "Contact Center Engineer",
        "kicker": "UCCE · PCCE · CCaaS",
        "blurb": "Ingress, script, queue, agent desktop, and the platforms you still meet in production.",
        "accent": 4,
    },
]


def js_json(value: object) -> str:
    text = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return (
        text.replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
        .replace("</", "<\\/")
    )


def parse_array(html: str, key: str) -> list:
    i = html.index(key) + len(key)
    decoder = json.JSONDecoder()
    value, _end = decoder.raw_decode(html[i:])
    if not isinstance(value, list):
        raise SystemExit(f"{key} did not parse as a list")
    return value


def parse_sections(html: str) -> list[dict]:
    sections = parse_array(html, "window.SECTIONS = ")
    marker = "var additions = "
    if marker not in html:
        return sections
    additions, _end = json.JSONDecoder().raw_decode(html[html.index(marker) + len(marker) :])
    by_id = {item["id"]: item for item in sections}
    for sid, extra in additions.items():
        if sid not in by_id:
            raise SystemExit(f"addition for unknown section {sid}")
        by_id[sid]["body"] += extra
    return sections


def strip_text(html: str) -> str:
    text = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def classify(section: dict) -> str:
    blob = f"{section['id']} {section['title']} {section.get('sub', '')}"
    group = section["group"]
    if group in CC_GROUPS or (group in KEYWORD_GROUPS and CC_RE.search(blob)):
        return "contact-center"
    if group == MIXED_GROUP or group in KEYWORD_GROUPS:
        teams = bool(TEAMS_RE.search(blob))
        webex = bool(WEBEX_RE.search(blob))
        if teams and not webex:
            return "teams"
        if webex and not teams:
            return "webex"
        if teams and webex:
            title = section["title"].lower()
            ti = title.find("team")
            wi = title.find("webex")
            if ti >= 0 and (wi < 0 or ti < wi):
                return "teams"
            return "webex"
    return "cisco-voice"


def load_flows() -> tuple[list[dict], dict[str, str]]:
    text = FLOW_PATH.read_text(encoding="utf-8")
    flows = parse_array(text, "window.UC_FLOW_CATALOG = ")
    marker = "window.UC_SECTION_FLOW = "
    mapping, _end = json.JSONDecoder().raw_decode(text[text.index(marker) + len(marker) :])
    return flows, mapping


def illustration_count(flows: list[dict]) -> int:
    seen: set[str] = set()
    for flow in flows:
        art = flow.get("art") or {}
        for key in ("topology", "mockup", "capture"):
            if art.get(key):
                seen.add(key + ":" + json.dumps(art[key], sort_keys=True))
    return len(seen)


def main() -> int:
    html = HTML_PATH.read_text(encoding="utf-8")
    if "window.SECTIONS = " not in html:
        print("HTML no longer embeds window.SECTIONS; modules are already split.", file=sys.stderr)
        return 1
    sections = parse_sections(html)
    flows, section_flow = load_flows()
    by_section: dict[str, list[dict]] = defaultdict(list)
    walks: list[dict] = []
    for flow in flows:
        if str(flow.get("id", "")).startswith("walk-"):
            walks.append(flow)
            continue
        sid = flow.get("sectionId")
        if not sid:
            raise SystemExit(f"flow {flow.get('id')} has no sectionId")
        by_section[sid].append(flow)

    for sid, pack in by_section.items():
        pack.sort(key=lambda item: (0 if str(item["id"]).startswith("sec-") else 1, item["id"]))

    missing = [s["id"] for s in sections if s["id"] not in by_section]
    if missing:
        raise SystemExit(f"{len(missing)} sections have no flow, first {missing[:5]}")

    SECTION_DIR.mkdir(parents=True, exist_ok=True)
    stale = {path.stem for path in SECTION_DIR.glob("*.js")}
    keep = {s["id"] for s in sections}
    for stem in stale - keep:
        (SECTION_DIR / f"{stem}.js").unlink()

    catalog = []
    journey_counts: Counter[str] = Counter()
    q_details = 0
    details = 0
    q_numbers = 0
    for section in sections:
        journey = classify(section)
        journey_counts[journey] += 1
        body = section.get("body") or ""
        q_details += body.count('<details class="q"')
        details += body.count("<details")
        q_numbers += len(re.findall(r"\bQ\d+\.", body))
        pack = by_section[section["id"]]
        walk_ids = []
        for flow in pack:
            for scenario in flow.get("scenarios") or []:
                if str(scenario).startswith("walk-") and scenario not in walk_ids:
                    walk_ids.append(scenario)
        record = {
            "id": section["id"],
            "num": section.get("num") or "",
            "group": section.get("group") or "Other",
            "title": section.get("title") or section["id"],
            "sub": section.get("sub") or "",
            "kind": section.get("kind") or "",
            "journey": journey,
            "track": TRACK_SLUG.get(section.get("group") or "", "other"),
            "flow": section_flow.get(section["id"], pack[0]["id"]),
            "walks": walk_ids,
            "blurb": strip_text(body)[:180],
            "cards": body.count("<details"),
        }
        catalog.append(record)
        payload = "UC.pack(" + js_json(section) + "," + js_json(pack) + ");\n"
        (SECTION_DIR / f"{section['id']}.js").write_text(payload, encoding="utf-8")

    walks_payload = "UC.walks(" + js_json(walks) + ");\n"
    (OUT / "walks.js").write_text(walks_payload, encoding="utf-8")

    chart_types = []
    chart_marker = "window.UC_CHART_TYPES = "
    if chart_marker in FLOW_PATH.read_text(encoding="utf-8"):
        raw = FLOW_PATH.read_text(encoding="utf-8")
        chart_types, _end = json.JSONDecoder().raw_decode(raw[raw.index(chart_marker) + len(chart_marker) :])

    walkthroughs = sum(1 for flow in flows if flow.get("walkthrough") or flow.get("layout") == "walk")
    faults = sum(1 for s in sections if s["id"].startswith(("sev2", "trick", "sev-")))
    drills = sum(1 for s in sections if s["id"].startswith("drill-"))
    groups = []
    seen_groups: set[str] = set()
    for section in sections:
        if section["group"] not in seen_groups:
            seen_groups.add(section["group"])
            groups.append(
                {
                    "name": section["group"],
                    "slug": TRACK_SLUG.get(section["group"], "other"),
                    "count": sum(1 for item in sections if item["group"] == section["group"]),
                }
            )

    stats = {
        "version": "v21",
        "sections": len(sections),
        "flows": len(flows),
        "walkthroughs": walkthroughs,
        "charts": len(chart_types),
        "illustrations": illustration_count(flows),
        "audioClips": 35,
        "trackHubs": 14,
        "groups": len(groups),
        "details": details,
        "selfChecks": q_details,
        "numberedQuestions": q_numbers,
        "faults": faults,
        "drills": drills,
        "journeys": {item["id"]: journey_counts[item["id"]] for item in JOURNEYS},
    }
    manifest = {
        "version": "v21",
        "built": "2026-10-14",
        "stats": stats,
        "journeys": JOURNEYS,
        "groups": groups,
        "chartTypes": chart_types,
        "sections": catalog,
    }
    (OUT / "manifest.js").write_text("UC.manifest(" + js_json(manifest) + ");\n", encoding="utf-8")
    (OUT / "integrity.json").write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(stats, indent=2))
    print("wrote", SECTION_DIR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
