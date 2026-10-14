#!/usr/bin/env python3
"""Fail if the public campus drifts: section count, CDN tags, or personal links."""

from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = ROOT / "campus" / "uc-lab-free-university.html"
DECK = ROOT / "downloads" / "Enterprise-Voice-with-Cisco-Technologies-CC-Cloud-Migration.pptx"
ZIP = ROOT / "releases" / "uc-lab-free-university.html.zip"
TEXT_SUFFIXES = {".md", ".html", ".cff", ".py", ".yml", ".yaml", ".txt"}
ALLOWED_EMAILS = {"user@contoso.com", "user@domain.com"}
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?<![\w.])(?:\+\d{1,3}[\s.\-]?)?\(?\d{3}\)?[\s.\-]\d{3}[\s.\-]\d{4}(?!\d)")


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


CURRICULUM = ROOT / "campus" / "assets" / "curriculum"
EXPECT = {
    "sections": 476,
    "flows": 978,
    "walkthroughs": 27,
    "charts": 32,
    "illustrations": 2772,
    "details": 13334,
    "selfChecks": 1585,
    "numberedQuestions": 13175,
    "faults": 110,
    "drills": 4,
}


def parse_js_value(text: str, marker: str):
    i = text.index(marker) + len(marker)
    value, _end = json.JSONDecoder().raw_decode(text[i:])
    return value


def parse_pack(text: str) -> tuple[dict, list]:
    marker = "UC.pack("
    i = text.index(marker) + len(marker)
    section, end = json.JSONDecoder().raw_decode(text[i:])
    rest = text[i + end :].lstrip()
    if rest.startswith(","):
        rest = rest[1:]
    flows, _end = json.JSONDecoder().raw_decode(rest)
    return section, flows


def main() -> int:
    errors: list[str] = []
    if not HTML_PATH.is_file():
        print("missing campus html", file=sys.stderr)
        return 1
    html = HTML_PATH.read_text(encoding="utf-8")
    def local_asset(url: str) -> bool:
        value = url.strip()
        if value in {"manifest.webmanifest", "sw.js"}:
            return True
        if "://" in value or value.startswith("//") or value.startswith("/") or ".." in value:
            return False
        return value.startswith("assets/")

    for match in re.finditer(r"<script\b([^>]*)>", html, re.I):
        src = re.search(r"""src\s*=\s*['"]([^'"]+)['"]""", match.group(1), re.I)
        if src and not local_asset(src.group(1)):
            fail(errors, f"campus script src is not a local asset: {src.group(1)}")
    for match in re.finditer(r"<link\b([^>]*)>", html, re.I):
        href = re.search(r"""href\s*=\s*['"]([^'"]+)['"]""", match.group(1), re.I)
        if not href:
            continue
        target = href.group(1)
        if target.lower().startswith("data:"):
            continue
        if not local_asset(target):
            fail(errors, f"campus link href is not a local asset: {target}")
    for host in ("cdn.jsdelivr", "unpkg.com", "cdnjs.", "fonts.googleapis", "ajax.googleapis"):
        if host in html.lower():
            fail(errors, f"campus references {host}")
    if "window.SECTIONS = " in html:
        fail(errors, "HTML still embeds window.SECTIONS; serve curriculum modules instead")
    if HTML_PATH.stat().st_size > 250_000:
        fail(errors, f"HTML is {HTML_PATH.stat().st_size} bytes; keep the shell under 250000")
    manifest_path = CURRICULUM / "manifest.js"
    try:
        manifest = parse_js_value(manifest_path.read_text(encoding="utf-8"), "UC.manifest(")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        fail(errors, f"manifest did not parse: {exc}")
        manifest = {}
    catalog = manifest.get("sections") or []
    stats_meta = manifest.get("stats") or {}
    if len(catalog) != EXPECT["sections"]:
        fail(errors, f"manifest lists {len(catalog)} sections")
    for key, expected in EXPECT.items():
        if stats_meta.get(key) != expected:
            fail(errors, f"manifest stats {key}={stats_meta.get(key)} expected {expected}")
    ids = [item.get("id") for item in catalog]
    if len(ids) != len(set(ids)):
        fail(errors, "duplicate section ids")
    details = 0
    self_checks = 0
    numbered = 0
    flow_count = 0
    home = ""
    teams_extra = False
    for sid in ids:
        path = CURRICULUM / "sections" / f"{sid}.js"
        if not path.is_file():
            fail(errors, f"missing section module {sid}")
            continue
        try:
            section, flows = parse_pack(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            fail(errors, f"{sid} did not parse: {exc}")
            continue
        if section.get("id") != sid:
            fail(errors, f"{sid} pack id is {section.get('id')}")
        body = section.get("body") or ""
        details += body.count("<details")
        self_checks += body.count('<details class="q"')
        numbered += len(re.findall(r"\bQ\d+\.", body))
        flow_count += len(flows)
        if sid == "home":
            home = body
        if sid == "ms-teams-phone-pstn" and "V20 FIELD CHECKLIST" in body:
            teams_extra = True
    walks_path = CURRICULUM / "walks.js"
    try:
        walks = parse_js_value(walks_path.read_text(encoding="utf-8"), "UC.walks(")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        fail(errors, f"walks did not parse: {exc}")
        walks = []
    flow_count += len(walks)
    if flow_count != EXPECT["flows"]:
        fail(errors, f"flow modules total {flow_count}")
    if details != EXPECT["details"] or self_checks != EXPECT["selfChecks"] or numbered != EXPECT["numberedQuestions"]:
        fail(errors, f"content counts details={details} selfChecks={self_checks} questions={numbered}")
    if "data-v21" not in home or "Study sequence" not in home:
        fail(errors, "home section is missing the v21 study sequence")
    if not teams_extra:
        fail(errors, "Teams Phone PSTN checklist addition is missing")
    sections = catalog
    stats = re.search(r"window\.STATS = (\{.*?\});", html)
    if not stats:
        fail(errors, "window.STATS missing")
    else:
        meta = json.loads(stats.group(1))
        if meta.get("sections") != EXPECT["sections"]:
            fail(errors, f"STATS.sections={meta.get('sections')}")
        if meta.get("version") != "v21":
            fail(errors, f"unexpected version {meta.get('version')}")

    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {"LICENSE", "NOTICE"}:
            continue
        rel = str(path.relative_to(ROOT))
        if rel == "scripts/check-campus.py":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        if "linktr.ee" in text or "cyphermonkey" in text:
            fail(errors, f"personal hub link in {rel}")
        if path.suffix.lower() in {".md", ".html", ".cff"}:
            for email in EMAIL_RE.findall(path.read_text(encoding="utf-8", errors="ignore")):
                if email not in ALLOWED_EMAILS:
                    fail(errors, f"unexpected email {email} in {rel}")
            for phone in PHONE_RE.findall(path.read_text(encoding="utf-8", errors="ignore")):
                fail(errors, f"phone-like string {phone} in {rel}")

    if DECK.is_file():
        with zipfile.ZipFile(DECK) as zf:
            blob = "\n".join(
                zf.read(name).decode("utf-8", "ignore")
                for name in zf.namelist()
                if name.endswith((".xml", ".rels"))
            )
        low = blob.lower()
        for needle in ("moonshot", "linktr.ee", "cyphermonkey", "kimi-design", "msh.team"):
            if needle in low:
                fail(errors, f"deck still contains {needle}")
        if "<dc:creator>CYPHER0X9</dc:creator>" not in blob:
            fail(errors, "deck creator is not CYPHER0X9")
        if blob.count("<p:sldId ") != 62:
            fail(errors, "deck is no longer 62 slides")
    else:
        fail(errors, "briefing deck missing")

    if ZIP.is_file() and HTML_PATH.is_file():
        with zipfile.ZipFile(ZIP) as zf:
            names = zf.namelist()
            if "uc-lab-free-university.html" not in names:
                fail(errors, "zip is missing uc-lab-free-university.html")
            elif zf.read("uc-lab-free-university.html") != HTML_PATH.read_bytes():
                fail(errors, "zip member does not match campus/uc-lab-free-university.html")
            for extra_name in ("sw.js", "manifest.webmanifest"):
                extra_path = ROOT / "campus" / extra_name
                if extra_name not in names:
                    fail(errors, f"zip is missing {extra_name}")
                elif extra_path.is_file() and zf.read(extra_name) != extra_path.read_bytes():
                    fail(errors, f"zip member does not match campus/{extra_name}")
            asset_root = ROOT / "campus" / "assets"
            expected = {
                "assets/" + path.relative_to(asset_root).as_posix()
                for path in asset_root.rglob("*")
                if path.is_file()
            }
            zipped_assets = {name for name in names if name.startswith("assets/")}
            if zipped_assets != expected:
                fail(errors, f"zip assets {sorted(zipped_assets)} != campus/assets {sorted(expected)}")
            allowed_root = {"uc-lab-free-university.html", "sw.js", "manifest.webmanifest"}
            for name in names:
                if name not in allowed_root and not name.startswith("assets/"):
                    fail(errors, f"unexpected zip member {name}")
            for name in sorted(expected):
                disk = asset_root / name.removeprefix("assets/")
                if zf.read(name) != disk.read_bytes():
                    fail(errors, f"zip asset does not match {disk}")
    else:
        fail(errors, "campus zip missing")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"ok: {len(sections)} sections, zip matches, deck scrubbed, no personal hub links")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
