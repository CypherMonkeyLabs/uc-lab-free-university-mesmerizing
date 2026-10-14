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
# The last two are Cisco system-guide directory-URI examples, not personal mail.
ALLOWED_EMAILS = {
    "user@contoso.com",
    "user@domain.com",
    "alice@example.com",
    "joe%20smith%23@cisco.com",
}
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?<![\w.])(?:\+\d{1,3}[\s.\-]?)?\(?\d{3}\)?[\s.\-]\d{3}[\s.\-]\d{4}(?!\d)")


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def parse_sections(html: str) -> list[dict]:
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
                return json.loads(html[i : j + 1])
    raise ValueError("SECTIONS array did not close")


def main() -> int:
    errors: list[str] = []
    if not HTML_PATH.is_file():
        print("missing campus html", file=sys.stderr)
        return 1
    html = HTML_PATH.read_text(encoding="utf-8")
    def local_asset(url: str) -> bool:
        value = url.strip()
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
    try:
        sections = parse_sections(html)
    except (ValueError, json.JSONDecodeError) as exc:
        fail(errors, f"SECTIONS did not parse: {exc}")
        sections = []
    stats = re.search(r'window\.STATS = (\{.*?\});', html)
    if not stats:
        fail(errors, "window.STATS missing")
    else:
        meta = json.loads(stats.group(1))
        if meta.get("sections") != len(sections):
            fail(errors, f"STATS.sections={meta.get('sections')} but array has {len(sections)}")
        if meta.get("version") != "v21":
            fail(errors, f"unexpected version {meta.get('version')}")
    ids = [item.get("id") for item in sections]
    if len(ids) != len(set(ids)):
        fail(errors, "duplicate section ids")
    home = sections[0].get("body", "") if sections else ""
    if "data-v21" not in home or "Study sequence" not in home:
        fail(errors, "home section is missing the v21 study sequence")

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
            asset_root = ROOT / "campus" / "assets"
            expected = {
                "assets/" + path.relative_to(asset_root).as_posix()
                for path in asset_root.rglob("*")
                if path.is_file()
            }
            zipped_assets = {name for name in names if name.startswith("assets/")}
            if zipped_assets != expected:
                fail(errors, f"zip assets {sorted(zipped_assets)} != campus/assets {sorted(expected)}")
            for name in names:
                if name != "uc-lab-free-university.html" and not name.startswith("assets/"):
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
