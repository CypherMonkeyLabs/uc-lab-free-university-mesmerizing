#!/usr/bin/env python3
"""Rewrite flagship chrome without rebuilding page bodies."""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    if spec is None or spec.loader is None:
        raise RuntimeError(filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


build_flagship = load("build_flagship", "build-flagship.py")
round2_pages = load("round2_pages", "round2_pages.py")
round3_pages = load("round3_pages", "round3_pages.py")
chrome = build_flagship.chrome
cheat_foot = round2_pages.cheat_foot
publish_root = round3_pages.publish_root

FLAG = ROOT / "flagship"
CHEAT_FOOT = cheat_foot().strip()


def extract(page: str) -> tuple[str, str, str]:
    title_match = re.search(r"<title>([^<]*?) · UC Lab Free University</title>", page)
    title = title_match.group(1) if title_match else "UC Lab"
    desc_match = re.search(r'<meta name="description" content="([^"]*)">', page)
    description = desc_match.group(1) if desc_match else title
    main_match = re.search(r'<main id="content" class="wrap">\s*(.*)\s*</main>', page, re.S)
    if not main_match:
        raise RuntimeError("main missing")
    body = main_match.group(1)
    body = re.sub(r'^<nav class="crumbs"[\s\S]*?</nav>\s*', "", body, count=1)
    body = re.sub(r'<footer class="cheat-print">[\s\S]*?</footer>', CHEAT_FOOT, body, count=1)
    body = lazy_mindmap(body)
    return title, body, description


def lazy_mindmap(body: str) -> str:
    if "markmap.Markmap.create" not in body:
        return body
    match = re.search(r"markmap\.Markmap\.create\(\"#mind\", \{\}, (\{.*?\})\);", body)
    if not match:
        return body
    data = match.group(1)
    replacement = (
        "<script>\n"
        "(function () {\n"
        "  var data = " + data + ";\n"
        "  var root = (document.body && document.body.getAttribute('data-root')) || '';\n"
        "  function load(src) {\n"
        "    return new Promise(function (resolve, reject) {\n"
        "      var script = document.createElement('script');\n"
        "      script.src = src;\n"
        "      script.onload = resolve;\n"
        "      script.onerror = reject;\n"
        "      document.body.appendChild(script);\n"
        "    });\n"
        "  }\n"
        "  function start() {\n"
        "    var host = document.querySelector('#mind');\n"
        "    if (!host) return;\n"
        "    var run = function () {\n"
        "      load(root + 'assets/vendor/d3.min.js').then(function () {\n"
        "        return load(root + 'assets/vendor/markmap-view.js');\n"
        "      }).then(function () {\n"
        "        if (window.markmap) markmap.Markmap.create('#mind', {}, data);\n"
        "      }).catch(function () {});\n"
        "    };\n"
        "    if ('IntersectionObserver' in window) {\n"
        "      var watch = new IntersectionObserver(function (entries) {\n"
        "        if (!entries.some(function (entry) { return entry.isIntersecting; })) return;\n"
        "        watch.disconnect();\n"
        "        run();\n"
        "      }, { rootMargin: '120px' });\n"
        "      watch.observe(host);\n"
        "    } else run();\n"
        "  }\n"
        "  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);\n"
        "  else start();\n"
        "})();\n"
        "</script>"
    )
    body = re.sub(r"<script src=\"[^\"]*d3\.min\.js\"></script>\s*", "", body)
    body = re.sub(r"<script src=\"[^\"]*markmap-view\.js\"></script>\s*", "", body)
    body = re.sub(r"<script>markmap\.Markmap\.create\(\"#mind\", \{\}, \{.*?\}\);</script>", replacement, body, count=1)
    return body


def main() -> int:
    pages = sorted(FLAG.rglob("*.html"))
    for path in pages:
        rel = path.relative_to(FLAG).as_posix()
        title, body, description = extract(path.read_text(encoding="utf-8"))
        path.write_text(chrome(rel, title, body, description), encoding="utf-8")
        print(rel)
    publish_root()
    print(f"restamped {len(pages)} pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
