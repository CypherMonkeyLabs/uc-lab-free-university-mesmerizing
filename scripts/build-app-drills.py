#!/usr/bin/env python3
"""Build the offline quiz bank, flashcards, boss exam, and extra call flows.

Facts are real UC statements. Each fact becomes three scored questions
(definition, reverse lookup, and why) plus one flashcard.
"""

from __future__ import annotations

import json
from pathlib import Path

from uc_facts import FACTS, BOSS, SCENARIOS

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "campus" / "assets" / "app-drills.js"
TRACKS = [
    "Start here",
    "SIP and media",
    "CUCM and CUBE",
    "Webex Calling and Teams Phone",
    "Contact center — UCCE and PCCE",
    "CCaaS and UCaaS platforms",
    "Emergency calling",
    "Voice network and QoS",
    "Migrations",
    "Troubleshooting",
    "Evidence habits",
    "Design notes",
    "Practice",
    "Reference",
]


def slot_choices(correct: str, others: list[str], salt: int) -> tuple[list[str], int]:
    picked: list[str] = []
    for text in others:
        if text and text != correct and text not in picked:
            picked.append(text)
        if len(picked) == 3:
            break
    if len(picked) < 3:
        raise SystemExit("not enough distractors")
    index = salt % 4
    choices: list[str] = []
    cursor = 0
    for i in range(4):
        if i == index:
            choices.append(correct)
        else:
            choices.append(picked[cursor])
            cursor += 1
    return choices, index


def build_questions(facts: list[dict]) -> list[dict]:
    by_track: dict[str, list[dict]] = {name: [] for name in TRACKS}
    for fact in facts:
        by_track[fact["track"]].append(fact)
    questions: list[dict] = []
    for track in TRACKS:
        items = by_track[track]
        count = len(items)
        if count < 100:
            raise SystemExit(f"{track} has {count} facts, need at least 100")
        terms = [item["term"] for item in items]
        defs = [item["def"] for item in items]
        whys = [item["why"] for item in items]
        if len(set(terms)) != count:
            raise SystemExit(f"duplicate term in {track}")
        if len(set(defs)) != count:
            raise SystemExit(f"duplicate definition in {track}")
        if len(set(whys)) != count:
            raise SystemExit(f"duplicate why in {track}")
        for index, fact in enumerate(items):
            neighbors = [items[(index + step) % count] for step in range(1, count)]
            def_choices, def_answer = slot_choices(
                fact["def"], [item["def"] for item in neighbors], index
            )
            term_choices, term_answer = slot_choices(
                fact["term"], [item["term"] for item in neighbors], index + 1
            )
            why_choices, why_answer = slot_choices(
                fact["why"], [item["why"] for item in neighbors], index + 2
            )
            base = f"{track}|{fact['term']}"
            questions.append(
                {
                    "id": base + "|def",
                    "track": track,
                    "q": f"What does {fact['term']} mean?",
                    "choices": def_choices,
                    "answer": def_answer,
                    "why": fact["why"] + " " + fact["def"],
                }
            )
            questions.append(
                {
                    "id": base + "|term",
                    "track": track,
                    "q": "Which term matches this statement? " + fact["def"],
                    "choices": term_choices,
                    "answer": term_answer,
                    "why": fact["term"] + " is the term. " + fact["why"],
                }
            )
            questions.append(
                {
                    "id": base + "|why",
                    "track": track,
                    "q": f"Why does {fact['term']} matter on a live system?",
                    "choices": why_choices,
                    "answer": why_answer,
                    "why": fact["why"],
                }
            )
    return questions


def main() -> None:
    questions = build_questions(FACTS)
    counts: dict[str, int] = {}
    for item in questions:
        counts[item["track"]] = counts.get(item["track"], 0) + 1
    for track in TRACKS:
        if counts.get(track, 0) < 300:
            raise SystemExit(f"{track} has {counts.get(track, 0)} questions")
    cards = [
        {"term": fact["term"], "def": fact["def"], "why": fact["why"], "track": fact["track"]}
        for fact in FACTS
    ]
    if len(cards) < 300:
        raise SystemExit("not enough flashcards")
    if len(BOSS) < 20:
        raise SystemExit("boss exam is short")
    if len(SCENARIOS) < 16:
        raise SystemExit("need at least 16 extra scenarios so the simulator reaches 20")
    for item in BOSS:
        if len(item["choices"]) != 4 or not (0 <= item["answer"] < 4) or not item["why"]:
            raise SystemExit("bad boss item " + item["q"][:40])
    payload = {
        "questions": questions,
        "cards": cards,
        "boss": BOSS,
        "counts": counts,
        "cardCount": len(cards),
        "bossCount": len(BOSS),
    }
    text = (
        "/* Generated by scripts/build-app-drills.py. Offline teaching bank. */\n"
        "window.UC_DRILLS = "
        + json.dumps(payload, ensure_ascii=True, separators=(",", ":"))
        + ";\nwindow.UC_EXTRA_SCENARIOS = "
        + json.dumps(SCENARIOS, ensure_ascii=True, separators=(",", ":"))
        + ";\n"
    )
    OUT.write_text(text, encoding="utf-8")
    print(f"questions {len(questions)} cards {len(cards)} boss {len(BOSS)} scenarios {len(SCENARIOS)}")
    for track in TRACKS:
        print(f"  {counts[track]:4}  {track}")


if __name__ == "__main__":
    main()
