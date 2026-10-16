#!/usr/bin/env python3
"""Strip generator identity from the Enterprise Voice briefing deck.

Keeps slide content. Drops the custom AIGC property, the orphaned provenance
part, the company field, and the generator hostname inside the pptd namespace.
Safe to run more than once.
"""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "downloads" / "Enterprise-Voice-with-Cisco-Technologies-CC-Cloud-Migration.pptx"

DROP_PARTS = {
    "customXml/provenance.xml",
    "docProps/custom.xml",
}
NAMESPACE_FROM = "https://kimi-design.msh.team/pptd/2026"
NAMESPACE_TO = "urn:uc-lab:pptd"
CONTENT_TYPE_OVERRIDE = (
    '<Override PartName="/docProps/custom.xml" '
    'ContentType="application/vnd.openxmlformats-officedocument.custom-properties+xml"/>'
)
CUSTOM_REL = re.compile(
    r'<Relationship\b[^>]*Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/custom-properties"[^>]*/>'
)


def transform(name: str, data: bytes) -> bytes | None:
    if name in DROP_PARTS:
        return None
    if not name.endswith((".xml", ".rels")):
        return data
    text = data.decode("utf-8")
    text = text.replace(NAMESPACE_FROM, NAMESPACE_TO)
    if name == "docProps/core.xml":
        text = re.sub(
            r"<dc:creator>[^<]*</dc:creator>",
            "<dc:creator>UC Lab</dc:creator>",
            text,
            count=1,
        )
    if name == "docProps/app.xml":
        text = re.sub(r"<Company>[^<]*</Company>", "", text)
        text = re.sub(r"<Application>[^<]*</Application>", "", text)
    if name == "[Content_Types].xml":
        text = text.replace(CONTENT_TYPE_OVERRIDE, "")
    if name == "_rels/.rels":
        text = CUSTOM_REL.sub("", text)
    return text.encode("utf-8")


def main() -> int:
    if not DECK.is_file():
        print(f"missing deck: {DECK}", file=sys.stderr)
        return 1
    original = DECK.read_bytes()
    tmp = DECK.with_suffix(".pptx.tmp")
    with zipfile.ZipFile(DECK, "r") as src, zipfile.ZipFile(
        tmp, "w", compression=zipfile.ZIP_DEFLATED
    ) as dst:
        for info in src.infolist():
            payload = transform(info.filename, src.read(info.filename))
            if payload is None:
                continue
            dst.writestr(info.filename, payload)
    tmp.replace(DECK)
    blob = zipfile.ZipFile(DECK).read("ppt/presentation.xml")
    slides = blob.decode("utf-8").count("<p:sldId ")
    if slides != 62:
        print(f"expected 62 slides, found {slides}", file=sys.stderr)
        return 1
    print(f"scrubbed {DECK.name}: {len(original)} -> {DECK.stat().st_size} bytes, {slides} slides")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
