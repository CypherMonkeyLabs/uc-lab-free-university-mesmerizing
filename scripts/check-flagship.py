#!/usr/bin/env python3
"""Fail the flagship build when Round 3 minimums are missed."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FLAG = ROOT / "flagship"
MENU = ("Diagrams", "Flows", "Charts", "Cheat Codes", "Play", "Ecosystem", "Downloads", "Careers")
VENDORS = (
    "three.module.js",
    "three.core.js",
    "anime.esm.min.js",
    "rough.esm.js",
    "d3.min.js",
    "markmap-view.js",
    "mermaid.min.js",
    "confetti.browser.js",
)


def main() -> int:
    errors = []
    root_html = (ROOT / "index.html").read_text(encoding="utf-8")
    home = (FLAG / "index.html").read_text(encoding="utf-8")
    if 'http-equiv="refresh"' in root_html:
        errors.append("root index is a refresh")
    if 'id="hero3d"' not in root_html:
        errors.append("root index has no hero")
    for label in MENU:
        if label not in root_html:
            errors.append(f"root menu missing {label}")
    if 'href="campus/uc-lab-free-university.html"' not in root_html:
        errors.append("root index missing campus link")
    if "mascot" not in root_html:
        errors.append("root index missing mascots")
    svgs = list((FLAG / "diagrams").glob("*.svg"))
    animated = [path for path in svgs if 'data-animated="true"' in path.read_text(encoding="utf-8", errors="ignore")]
    atlas = (FLAG / "diagrams" / "index.html").read_text(encoding="utf-8")
    surfaced = sum(1 for path in svgs if path.name in atlas)
    charts = home.count("data-chart=") + (FLAG / "charts" / "index.html").read_text(encoding="utf-8").count("data-chart=")
    # Charts live on the charts page. Count unique chart ids there.
    chart_page = (FLAG / "charts" / "index.html").read_text(encoding="utf-8")
    chart_ids = chart_page.count('data-chart="')
    pdfs = list((FLAG / "cheats").glob("*.pdf"))
    tracks = list((FLAG / "tracks").glob("*.html"))
    track_missing = []
    for path in tracks:
        text = path.read_text(encoding="utf-8")
        if "data-mini3d" not in text and path.name != "index.html":
            track_missing.append(path.name)
        if path.name != "index.html" and "data-parallax" not in text:
            track_missing.append(path.name + " parallax")
    for name in VENDORS:
        if not (FLAG / "assets" / "vendor" / name).is_file():
            errors.append(f"missing vendor {name}")
    if len(svgs) < 25:
        errors.append(f"diagrams {len(svgs)} < 25")
    if len(animated) < 12:
        errors.append(f"animated diagrams {len(animated)} < 12")
    if surfaced < 25:
        errors.append(f"atlas surfaces {surfaced} < 25")
    if chart_ids < 6:
        errors.append(f"charts {chart_ids} < 6")
    if len(pdfs) < 10:
        errors.append(f"cheat pdfs {len(pdfs)} < 10")
    if "cyphermonkeylabs.com" not in (FLAG / "cheats" / "ports.html").read_text(encoding="utf-8"):
        errors.append("cheat sheet missing studio footer")
    if track_missing:
        errors.append("track chrome missing: " + ", ".join(track_missing[:8]))
    if 'id="siteSearch"' not in home or "Breadcrumb" not in home:
        errors.append("search or breadcrumbs missing on home")
    footer_js = ROOT / "shared" / "brand-footer.js"
    footer_css = ROOT / "shared" / "brand-footer.css"
    if not footer_js.is_file() or not footer_css.is_file():
        errors.append("shared brand footer files are missing")
    else:
        footer = footer_js.read_text(encoding="utf-8")
        for needle in (
            "https://github.com/cipher0x9",
            "https://github.com/CypherMonkeyLabs",
            "https://cyphermonkeylabs.com",
            "https://x.com/Cypher0x9",
            "https://www.linkedin.com/in/luckylakshmanucwebex",
            "https://huggingface.co/Cypher0x9",
            "© 2026 CypherMonkeyLabs",
            "Educational independent study project by a student.",
        ):
            if needle not in footer:
                errors.append(f"brand footer missing {needle}")
        for banned in ("linktr.ee", "mailto:", "instagram.com", "kaggle.com"):
            if banned in footer:
                errors.append(f"brand footer includes {banned}")
    shell = (FLAG / "assets" / "site.js").read_text(encoding="utf-8")
    if "shared/brand-footer.js" not in shell:
        errors.append("flagship shell does not load the brand footer")
    campus_shell = (ROOT / "campus" / "assets" / "app.js").read_text(encoding="utf-8")
    if "shared/brand-footer.js" not in campus_shell:
        errors.append("campus shell does not load the brand footer")
    bare = [
        path.relative_to(ROOT).as_posix()
        for path in list(FLAG.rglob("*.html")) + [ROOT / "index.html"]
        if "site.js" not in path.read_text(encoding="utf-8")
    ]
    if bare:
        errors.append("pages missing site.js shell: " + ", ".join(bare[:8]))
    print(
        f"counts diagrams={len(svgs)} animated={len(animated)} surfaced={surfaced} "
        f"charts={chart_ids} pdfs={len(pdfs)} tracks={len(tracks)} vendors={len(VENDORS)}"
    )
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
