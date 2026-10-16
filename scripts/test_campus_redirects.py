#!/usr/bin/env python3
"""Redirect coverage for campus/index.html, plus the restored lab contract.

The modular counts (580 sections, 1,197 flows, 15,972 details) must not move.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAMPUS = ROOT / "campus"
TEACHING_ROUTES = (
    "simulator",
    "dial-plan",
    "ivr",
    "sipdec",
    "codec",
    "jitter",
    "route",
    "webex",
    "ucce",
    "finesse",
    "e911",
    "qos",
    "srtp",
    "erlang-c",
    "fault",
    "dialpeer",
    "nat",
    "record",
    "quiz",
    "cards",
    "boss",
)
RESTORED_LADDERS = (
    "hold",
    "blind",
    "consult",
    "hunt",
    "mra",
    "ivr-agent",
    "e911",
    "teams-dr",
    "wxcc",
)


def parse_js_value(text: str, marker: str):
    i = text.index(marker) + len(marker)
    value, _end = json.JSONDecoder().raw_decode(text[i:])
    return value


def collect_errors(root: Path | None = None) -> list[str]:
    root = root or ROOT
    errors: list[str] = []
    campus_index = root / "campus" / "index.html"
    root_index = root / "index.html"
    target = root / "campus" / "uc-lab-free-university.html"
    if not campus_index.is_file():
        errors.append("campus/index.html is missing")
        return errors
    html = campus_index.read_text(encoding="utf-8")
    if not re.search(r'http-equiv="refresh"\s+content="0;\s*url=uc-lab-free-university\.html"', html):
        errors.append("campus/index.html does not refresh immediately to uc-lab-free-university.html")
    if 'rel="canonical" href="uc-lab-free-university.html"' not in html:
        errors.append("campus/index.html canonical href is not uc-lab-free-university.html")
    if 'href="uc-lab-free-university.html"' not in html:
        errors.append("campus/index.html has no same-directory fallback link")
    if re.search(r"https?:|javascript:", html, re.I):
        errors.append("campus/index.html points outside the campus directory")
    if "<script" in html.lower():
        errors.append("campus/index.html should redirect without a script")
    if not target.is_file():
        errors.append("campus/index.html target uc-lab-free-university.html is missing")
    if root_index.is_file():
        root_html = root_index.read_text(encoding="utf-8")
        if 'http-equiv="refresh"' in root_html:
            errors.append("repo index.html must be the university front door, not a refresh")
        for label in ("Home", "Learn", "Diagrams", "Flows", "Play", "Downloads", "Ecosystem"):
            if label not in root_html:
                errors.append(f"repo index.html menu is missing {label}")
        if "hero-diagram" not in root_html and 'id="hero3d"' not in root_html:
            errors.append("repo index.html is missing the teaching hero")
        for href in (
            "https://cyphermonkeylabs.com",
            "https://github.com/CypherMonkeyLabs",
            "https://linktr.ee/cypherMonkey",
        ):
            if href not in root_html:
                errors.append(f"repo index.html is missing {href}")
        if 'href="campus/uc-lab-free-university.html"' not in root_html:
            errors.append("repo index.html does not keep the deep campus link")
        if not (root / "flagship" / "index.html").is_file():
            errors.append("flagship/index.html is missing")
        if not (root / "campus" / "uc-lab-free-university.html").is_file():
            errors.append("repo index.html campus target is missing")
    else:
        errors.append("repo index.html is missing")

    shell = target.read_text(encoding="utf-8") if target.is_file() else ""
    for banned in ("app-drills.js", "labs.js", "restored-walks.js", "app-labs.js", "labs.css"):
        if banned in shell:
            errors.append(f"campus shell eagerly loads {banned}")

    sw = (root / "campus" / "sw.js").read_text(encoding="utf-8")
    if "./assets/labs/restored-walks.js" not in sw:
        errors.append("sw.js does not name the restored walk data")
    if "cache.put" not in sw:
        errors.append("sw.js does not lazily cache responses")
    if "var LAZY" not in sw or "function lazyAsset" not in sw:
        errors.append("sw.js lazy-cache list is missing")
    for rel in (
        "./assets/labs/restored-walks.js",
        "./assets/labs.js",
        "./assets/app-drills.js",
        "./assets/curriculum/walks.js",
    ):
        if rel not in sw:
            errors.append(f"sw.js lazy list omits {rel}")

    app = (root / "campus" / "assets" / "app.js").read_text(encoding="utf-8")
    labs = (root / "campus" / "assets" / "labs.js").read_text(encoding="utf-8")
    if len(TEACHING_ROUTES) != 21:
        errors.append("teaching route list is not 21 labs")
    for route in TEACHING_ROUTES:
        if f'["{route}",' not in app:
            errors.append(f"app.js is missing teaching lab {route}")
        if f"{route}:" not in labs and f'"{route}":' not in labs:
            errors.append(f"labs.js is missing route {route}")
    if "uc_app_quiz" not in labs or "uc_app_cards" not in labs:
        errors.append("quiz progress keys are not the local storage keys")
    if "0.8" not in labs:
        errors.append("boss exam pass line is missing")

    drills_path = root / "campus" / "assets" / "app-drills.js"
    try:
        drills = parse_js_value(drills_path.read_text(encoding="utf-8"), "window.UC_DRILLS = ")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"quiz bank did not parse: {exc}")
        drills = {}
    questions = drills.get("questions") or []
    cards = drills.get("cards") or []
    boss = drills.get("boss") or []
    if len(questions) != 2913:
        errors.append(f"quiz bank has {len(questions)} questions")
    if len(cards) != 2018:
        errors.append(f"flashcards are {len(cards)}")
    if len(boss) != 24:
        errors.append(f"boss exam has {len(boss)} questions")
    counts: dict[str, int] = {}
    for item in questions:
        counts[item.get("track") or ""] = counts.get(item.get("track") or "", 0) + 1
    if len(counts) != 14 or any(n < 150 for n in counts.values()):
        errors.append(f"per-track quiz counts are {counts}")

    walks_path = root / "campus" / "assets" / "labs" / "restored-walks.js"
    try:
        ladders = parse_js_value(walks_path.read_text(encoding="utf-8"), "window.UC_RESTORED_WALKS = ")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"restored walks did not parse: {exc}")
        ladders = []
    by_id = {item.get("id"): item for item in ladders}
    if len(ladders) != 24:
        errors.append(f"call-flow player has {len(ladders)} ladders")
    for name in RESTORED_LADDERS:
        row = by_id.get(name)
        if not row or not row.get("restored"):
            errors.append(f"restored ladder {name} is missing")
            continue
        if not row.get("actors") or not row.get("steps"):
            errors.append(f"restored ladder {name} has no steps")
    curriculum_path = root / "campus" / "assets" / "curriculum" / "walks.js"
    try:
        curriculum = parse_js_value(curriculum_path.read_text(encoding="utf-8"), "UC.walks(")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"curriculum walks did not parse: {exc}")
        curriculum = []
    if len(curriculum) != 37:
        errors.append(f"curriculum walk count moved to {len(curriculum)}")
    return errors


class CampusRedirectTests(unittest.TestCase):
    def test_index_and_restored_labs(self) -> None:
        self.assertEqual(collect_errors(), [])


if __name__ == "__main__":
    unittest.main()
