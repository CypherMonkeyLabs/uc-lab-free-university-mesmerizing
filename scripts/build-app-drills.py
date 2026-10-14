#!/usr/bin/env python3
"""Build the offline quiz bank, flashcards, boss exam, and extra call flows.

Each fact becomes one scored question. A second question is added only when
the reason has a further sentence that is not a restatement of the definition
or of the first consequence. Reversed definition/term pairs are not emitted.
Scenario questions are real situations. Explanations must not repeat the
correct choice.
"""

from __future__ import annotations

import json
import random
import re
from pathlib import Path

from quiz_scenarios import QUIZ_SCENARIOS
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


def sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text.strip()) if part.strip()]


def tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def overlap(left: str, right: str) -> float:
    a, b = tokens(left), tokens(right)
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def repeats(explanation: str, choice: str) -> bool:
    reason = re.sub(r"\s+", " ", explanation.lower().strip())
    answer = re.sub(r"\s+", " ", choice.lower().strip())
    if not reason or not answer:
        return True
    if reason == answer or answer in reason or reason in answer:
        return True
    return overlap(reason, answer) >= 0.55


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


def consequence(fact: dict) -> tuple[str, str] | None:
    """Return (choice, explanation) when the reason adds a further sentence."""
    parts = sentences(fact["why"])
    if len(parts) < 2:
        return None
    if overlap(fact["def"], fact["why"]) >= 0.45:
        return None
    choice = parts[0]
    reason = " ".join(parts[1:])
    if repeats(choice, fact["def"]) or repeats(reason, choice) or repeats(reason, fact["def"]):
        return None
    return choice, reason


def build_questions(facts: list[dict]) -> list[dict]:
    by_track: dict[str, list[dict]] = {name: [] for name in TRACKS}
    for fact in facts:
        by_track[fact["track"]].append(fact)
    scenarios_by_track: dict[str, list[dict]] = {name: [] for name in TRACKS}
    for item in QUIZ_SCENARIOS:
        if item["track"] not in scenarios_by_track:
            raise SystemExit("scenario track is not a campus track: " + item["track"])
        scenarios_by_track[item["track"]].append(item)
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
        bucket: list[dict] = []
        for index, fact in enumerate(items):
            neighbors = [items[(index + step) % count] for step in range(1, count)]
            extra = consequence(fact)
            explanation = extra[1] if extra else fact["why"]
            if repeats(explanation, fact["def"]):
                raise SystemExit(f"explanation repeats the answer for {fact['term']}")
            def_choices, def_answer = slot_choices(
                fact["def"], [item["def"] for item in neighbors], index
            )
            bucket.append(
                {
                    "id": f"{track}|{fact['term']}|def",
                    "track": track,
                    "q": f"What does {fact['term']} mean?",
                    "choices": def_choices,
                    "answer": def_answer,
                    "why": explanation,
                }
            )
            if extra is None:
                continue
            choice, reason = extra
            distractors = []
            for item in neighbors:
                lead = sentences(item["why"])[0]
                if lead and lead not in distractors and not repeats(lead, choice):
                    distractors.append(lead)
                if len(distractors) == 3:
                    break
            open_choices, open_answer = slot_choices(choice, distractors, index + 1)
            bucket.append(
                {
                    "id": f"{track}|{fact['term']}|open",
                    "track": track,
                    "q": f"{fact['term']}. {fact['def']} Which consequence is still open?",
                    "choices": open_choices,
                    "answer": open_answer,
                    "why": reason,
                }
            )
        for index, item in enumerate(scenarios_by_track[track]):
            choices, answer = slot_choices(item["correct"], item["wrongs"], index + 3)
            if repeats(item["why"], item["correct"]):
                raise SystemExit("scenario explanation repeats the answer: " + item["q"][:80])
            bucket.append(
                {
                    "id": f"{track}|scenario|{index}",
                    "track": track,
                    "q": item["q"],
                    "choices": choices,
                    "answer": answer,
                    "why": item["why"],
                }
            )
        seen_q: set[str] = set()
        for item in bucket:
            if item["q"] in seen_q:
                raise SystemExit(f"duplicate question in {track}: {item['q'][:80]}")
            seen_q.add(item["q"])
            correct = item["choices"][item["answer"]]
            if repeats(item["why"], correct):
                raise SystemExit(f"explanation repeats the answer in {track}: {item['q'][:80]}")
            if len(set(item["choices"])) != 4:
                raise SystemExit(f"choices are not distinct in {track}: {item['q'][:80]}")
        random.Random(track).shuffle(bucket)
        questions.extend(bucket)
    return questions


def main() -> None:
    questions = build_questions(FACTS)
    counts: dict[str, int] = {}
    for item in questions:
        counts[item["track"]] = counts.get(item["track"], 0) + 1
    for track in TRACKS:
        if counts.get(track, 0) < 150:
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
