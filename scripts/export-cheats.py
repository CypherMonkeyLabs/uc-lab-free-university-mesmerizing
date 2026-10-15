#!/usr/bin/env python3
"""Print each cheat-code HTML page to PDF and PNG, then refresh the offline zip."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
CHEATS = ROOT / "flagship" / "cheats"


def page_count(path: Path) -> int:
    data = path.read_bytes()
    return data.count(b"/Type /Page\n") + data.count(b"/Type /Page ")


def refresh_zip() -> None:
    spec = importlib.util.spec_from_file_location("build_flagship", ROOT / "scripts" / "build-flagship.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load build-flagship.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.write_zip()


def main() -> int:
    manifest = json.loads((CHEATS / "manifest.json").read_text(encoding="utf-8"))
    slugs = manifest["sheets"]
    missing = [slug for slug in slugs if not (CHEATS / f"{slug}.html").is_file()]
    if missing:
        print("missing html: " + ", ".join(missing), file=sys.stderr)
        return 1
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page(viewport={"width": 1100, "height": 1400})
        for slug in slugs:
            page.goto((CHEATS / f"{slug}.html").as_uri(), wait_until="load")
            page.emulate_media(media="print")
            pdf_path = CHEATS / f"{slug}.pdf"
            for scale in (1, 0.9, 0.8, 0.72):
                page.pdf(
                    path=str(pdf_path),
                    format="Letter",
                    print_background=True,
                    scale=scale,
                    margin={"top": "0.4in", "bottom": "0.4in", "left": "0.45in", "right": "0.45in"},
                )
                if page_count(pdf_path) <= 1:
                    break
            page.locator("article.cheat-sheet").screenshot(path=str(CHEATS / f"{slug}.png"))
            print(f"{slug} pages={page_count(CHEATS / f'{slug}.pdf')}")
        browser.close()
    refresh_zip()
    print("zip refreshed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
