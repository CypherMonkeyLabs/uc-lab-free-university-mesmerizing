#!/usr/bin/env python3
"""Report off-origin loads in HTML, CSS, and JS. Anchor citations are not loads.

Exit 1 when a script, stylesheet, image, font, fetch, or CSS url() points off origin.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PATTERNS = [
    (r'<(?:script|img|iframe|source|video|audio)[^>]+\bsrc="(https?://[^"]+)"', "html src"),
    (r'<link[^>]+href="(https?://[^"]+)"', "html link"),
    (r'url\(\s*["\']?(https?://[^)"\']+)', "css url()"),
    (r'@import\s+["\'](https?://[^"\']+)', "css @import"),
    (r'\bimport\s*(?:\(|[^;]*from\s*)["\'](https?://[^"\']+)', "js import"),
    (r'\bfetch\(\s*["\'`](https?://[^"\'`]+)', "js fetch"),
    (r'new (?:Worker|WebSocket|EventSource)\(\s*["\'`](https?://[^"\'`]+)', "js net"),
]
SKIP = {".git", "node_modules", "releases", "flagship", "campus"}
fail = []
files = []
for path in ROOT.rglob("*"):
    if any(part in SKIP for part in path.parts):
        continue
    if path.suffix.lower() not in {".html", ".css", ".js", ".mjs"}:
        continue
    if not path.is_file():
        continue
    files.append(path)

for path in files:
    text = path.read_text(errors="replace")
    for pattern, kind in PATTERNS:
        for match in re.finditer(pattern, text):
            fail.append(f"{path.relative_to(ROOT)}: off-origin {kind}: {match.group(1)}")

for item in fail:
    print("FAIL", item)
print("csp_check:", len(fail), "off-origin loads in", len(files), "files")
sys.exit(1 if fail else 0)
