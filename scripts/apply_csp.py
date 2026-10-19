#!/usr/bin/env python3
"""Add the lab CSP meta tag and move inline scripts into external files.

Idempotent. Leaves visible text, JSON data blocks, and off-origin anchors alone.
"""

from __future__ import annotations

import base64
import hashlib
import os
import re
import sys
from pathlib import Path

from csp_policy import CSP_CONTENT, CSP_META

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".git", "node_modules"}
SCRIPT_RE = re.compile(r"<script\b([^>]*)>(.*?)</script>", re.I | re.S)
CHARSET_RE = re.compile(r"<meta\s+charset\s*=\s*[\"']utf-8[\"']\s*/?>", re.I)
HEAD_RE = re.compile(r"<head[^>]*>", re.I)
TYPE_RE = re.compile(r"""\btype\s*=\s*(["'])([^"']+)\1""", re.I)
SRC_RE = re.compile(r"\bsrc\s*=", re.I)
HANDLER_RE = re.compile(
    r"""(?P<prefix>\s)(?P<name>on[a-zA-Z]+)(?P<eq>\s*=\s*)(?P<quote>["'])(?P<code>.*?)(?P=quote)""",
    re.S,
)
JS_TYPES = {"", "module", "text/javascript", "application/javascript", "text/ecmascript"}
PASSIVE_TYPES = {
    "application/json",
    "application/ld+json",
    "text/plain",
    "text/markdown",
    "speculationrules",
}


def script_type(attrs: str) -> str:
    match = TYPE_RE.search(attrs)
    if not match:
        return ""
    return match.group(2).strip().lower()


def is_inline_js(attrs: str, body: str) -> bool:
    if SRC_RE.search(attrs):
        return False
    if not body.strip():
        return False
    kind = script_type(attrs)
    if kind in PASSIVE_TYPES:
        return False
    return kind in JS_TYPES


def destination(body: str) -> Path:
    # These four bodies are unique to the UC lab. Other labs keep a hashed name
    # so two different theme boots never share one file.
    if 'getItem("canon-theme")' in body and 'if(t!=="aurora")t="bloom"' in body and "canon-ink" in body:
        return Path("assets/js/canon-theme.js")
    if 'localStorage.getItem("uc_flagship_theme")' in body:
        return Path("flagship/assets/flagship-theme.js")
    if "uc_lab_settings_v21" in body and "window.STATS" in body:
        return Path("campus/assets/campus-boot.js")
    if "markmap.Markmap.create" in body and '"content": "UC Lab"' in body:
        return Path("flagship/ecosystem/mindmap-init.js")
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]
    return Path("assets/csp") / f"inline-{digest}.js"


def relative_src(html_path: Path, js_path: Path) -> str:
    rel = os.path.relpath(js_path, html_path.parent)
    return rel.replace(os.sep, "/")


def script_src_directive(hashes: list[str]) -> str:
    extra = "".join(f" '{item}'" for item in hashes)
    return f"script-src 'self'{extra}"


def csp_meta(hashes: list[str]) -> str:
    if not hashes:
        return CSP_META
    content = CSP_CONTENT.replace("script-src 'self'", script_src_directive(hashes), 1)
    return f'<meta http-equiv="Content-Security-Policy" content="{content}">'


def import_map_hashes(text: str) -> list[str]:
    hashes = []
    for match in SCRIPT_RE.finditer(text):
        if script_type(match.group(1)) != "importmap":
            continue
        if SRC_RE.search(match.group(1)):
            continue
        digest = base64.b64encode(hashlib.sha256(match.group(2).encode("utf-8")).digest()).decode("ascii")
        token = f"sha256-{digest}"
        if token not in hashes:
            hashes.append(token)
    return hashes


def insert_csp(text: str) -> str:
    hashes = import_map_hashes(text)
    meta = csp_meta(hashes)
    existing = re.search(r'<meta\s+http-equiv="Content-Security-Policy"[^>]*>', text)
    if existing:
        if existing.group(0) == meta:
            return text
        return text[: existing.start()] + meta + text[existing.end() :]
    match = CHARSET_RE.search(text)
    if match:
        return text[: match.end()] + "\n" + meta + text[match.end() :]
    head = HEAD_RE.search(text)
    if not head:
        raise RuntimeError("HTML file has no head")
    return text[: head.end()] + "\n" + meta + text[head.end() :]


def html_files() -> list[Path]:
    found = []
    for path in ROOT.rglob("*.html"):
        if any(part in SKIP for part in path.parts):
            continue
        if path.is_file():
            found.append(path)
    return found


def main() -> int:
    global ROOT
    if len(sys.argv) > 1:
        ROOT = Path(sys.argv[1]).resolve()
    files_written: dict[Path, str] = {}
    pages = 0
    moved = 0
    handlers = 0
    for path in html_files():
        text = path.read_text(encoding="utf-8")
        pieces: list[str] = []
        cursor = 0
        changed = False
        for match in SCRIPT_RE.finditer(text):
            attrs, body = match.group(1), match.group(2)
            if not is_inline_js(attrs, body):
                continue
            rel_js = destination(body)
            target = ROOT / rel_js
            normalized = body if body.endswith("\n") else body + "\n"
            previous = files_written.get(target)
            if previous is None and target.is_file():
                previous = target.read_text(encoding="utf-8")
            if previous is not None and previous != normalized:
                raise RuntimeError(f"conflicting inline script for {rel_js} from {path}")
            files_written[target] = normalized
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(normalized, encoding="utf-8")
            src = relative_src(path, target)
            kind = script_type(attrs)
            type_attr = f' type="{kind}"' if kind == "module" else ""
            pieces.append(text[cursor : match.start()])
            pieces.append(f'<script{type_attr} src="{src}"></script>')
            cursor = match.end()
            changed = True
            moved += 1
        if pieces:
            text = "".join(pieces) + text[cursor:]
        handler_count = len(HANDLER_RE.findall(text))
        if handler_count:
            handlers += handler_count
            print(f"HANDLER {path.relative_to(ROOT)} {handler_count}")
        updated = insert_csp(text)
        if updated != path.read_text(encoding="utf-8"):
            path.write_text(updated, encoding="utf-8")
            pages += 1
        elif changed:
            pages += 1
    for target, body in files_written.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
        print(f"script {target.relative_to(ROOT)} ({len(body)} bytes)")
    print(f"pages touched: {pages}")
    print(f"inline scripts moved: {moved}")
    print(f"inline handlers still in html: {handlers}")
    return 1 if handlers else 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
