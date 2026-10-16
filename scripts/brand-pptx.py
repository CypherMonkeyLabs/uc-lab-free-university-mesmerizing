#!/usr/bin/env python3
"""Add the Cypher Monkey Labs footer and closing slide to the briefing deck.

Safe to run more than once. Link rows come from scripts/lab_links.py.
Also writes the README badge art in docs/assets/badges/ and refreshes the
badge block between the cml-badges markers in README.md when those markers
are present.

GitHub, X, LinkedIn, Hugging Face, Instagram, Kaggle, and Google marks are
Simple Icons paths (CC0), recolored for the footer. The website globe and
the app mark are original.
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from lab_links import (
    APP_HREF,
    BASE_SLIDES,
    DISCLAIMER,
    EXPECTED_SLIDES,
    FOOTER_LINE,
    FOOTER_LINKS,
    readme_links,
)

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "downloads" / "Enterprise-Voice-with-Cisco-Technologies-CC-Cloud-Migration.pptx"
ICON_DIR = ROOT / "scripts" / "brand_icons"
BADGE_DIR = ROOT / "docs" / "assets" / "badges"
README = ROOT / "README.md"

A = "http://schemas.openxmlformats.org/drawingml/2006/main"
P = "http://schemas.openxmlformats.org/presentationml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PPTD = "urn:uc-lab:pptd"
SLIDE_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide"
IMAGE_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"
LINK_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink"
LAYOUT_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout"

EMU = 914400
SLIDE_W = 12_192_000
# Lowest existing shape on the briefing ends at 6,578,600. The band starts below it.
FOOTER_TOP = 6_670_000
MARGIN_X = 609_600
ICON = 210_000
DISC_PT = 10
COPY_PT = 12
LABEL_PT = 12
FOOTER_FONT = "Liberation Sans"
TITLE_FONT = "Liter"

BAR = "12161C"
RULE = "2DD4BF"
DISC_COLOR = "C5CED6"
COPY_COLOR = "F7F4EF"
LABEL_COLOR = "F7F4EF"
NAVY = "0B1220"
TEAL = "2DD4BF"
TEAL_DEEP = "0F766E"
BODY = "E6EDF2"
MUTED = "C5CED6"

OUR_URLS = {link.href for link in FOOTER_LINKS} | {APP_HREF}
CLOSE_MARK = "cml-close-mark"


def q(ns: str, tag: str) -> str:
    return f"{{{ns}}}{tag}"


def register_namespaces(xml: bytes) -> None:
    ET.register_namespace("a", A)
    ET.register_namespace("p", P)
    ET.register_namespace("r", R)
    ET.register_namespace("pptd", PPTD)
    for prefix, uri in re.findall(br'xmlns:([A-Za-z0-9]+)="([^"]+)"', xml):
        ET.register_namespace(prefix.decode(), uri.decode())


def serialize(root: ET.Element) -> bytes:
    body = ET.tostring(root, encoding="utf-8", xml_declaration=False)
    return b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + body


def el(ns: str, tag: str, attrib: dict[str, str] | None = None, text: str | None = None) -> ET.Element:
    node = ET.Element(q(ns, tag), attrib or {})
    if text is not None:
        node.text = text
    return node


def solid(color: str) -> ET.Element:
    node = el(A, "solidFill")
    node.append(el(A, "srgbClr", {"val": color}))
    return node


def xfrm(x: int, y: int, w: int, h: int) -> ET.Element:
    node = el(A, "xfrm")
    node.append(el(A, "off", {"x": str(x), "y": str(y)}))
    node.append(el(A, "ext", {"cx": str(w), "cy": str(h)}))
    return node


def run(text: str, size: int, color: str, font: str, bold: bool = False) -> ET.Element:
    node = el(A, "r")
    props: dict[str, str] = {"lang": "en-US", "sz": str(size), "u": "none", "dirty": "0", "noProof": "1"}
    if bold:
        props["b"] = "1"
    rpr = el(A, "rPr", props)
    rpr.append(solid(color))
    rpr.append(el(A, "latin", {"typeface": font}))
    rpr.append(el(A, "ea", {"typeface": font}))
    rpr.append(el(A, "cs", {"typeface": font}))
    node.append(rpr)
    node.append(el(A, "t", text=text))
    return node


def paragraph(runs: list[ET.Element], align: str, size: int) -> ET.Element:
    node = el(A, "p")
    node.append(el(A, "pPr", {"algn": align}))
    for item in runs:
        node.append(item)
    node.append(el(A, "endParaRPr", {"lang": "en-US", "sz": str(size), "u": "none"}))
    return node


def shape_name(node: ET.Element) -> str:
    for child in list(node):
        if child.tag.endswith("nvSpPr") or child.tag.endswith("nvPicPr") or child.tag.endswith("nvCxnSpPr"):
            for found in child.iter():
                if found.tag == q(P, "cNvPr"):
                    return found.get("name") or ""
    return ""


def max_shape_id(root: ET.Element) -> int:
    highest = 1
    for node in root.iter(q(P, "cNvPr")):
        raw = node.get("id")
        if raw and raw.isdigit():
            highest = max(highest, int(raw))
    return highest


def text_units(text: str) -> float:
    units = 0.0
    for char in text:
        if char == " ":
            units += 0.34
        elif char in "ijlI1'.,|":
            units += 0.32
        elif char in "mwMW@":
            units += 0.96
        elif char in "ftrJ":
            units += 0.42
        else:
            units += 0.60
    return units


def text_width(text: str, pt: int) -> int:
    return int(text_units(text) * pt * 12700)


class SlideRels:
    def __init__(self, text: str) -> None:
        self.rows: list[dict[str, str]] = []
        for match in re.finditer(r"<Relationship\b([^>]*)/>", text):
            attrs = dict(re.findall(r'([A-Za-z]+)="([^"]*)"', match.group(1)))
            target = attrs.get("Target", "")
            if "/media/cml-" in target or target.startswith("../media/cml-"):
                continue
            if target in OUR_URLS:
                continue
            self.rows.append(attrs)
        self._next = 1
        for row in self.rows:
            found = re.fullmatch(r"rId(\d+)", row.get("Id", ""))
            if found:
                self._next = max(self._next, int(found.group(1)) + 1)

    def add(self, rel_type: str, target: str, external: bool = False) -> str:
        for row in self.rows:
            if row.get("Type") == rel_type and row.get("Target") == target:
                return row["Id"]
        rid = f"rId{self._next}"
        self._next += 1
        row = {"Id": rid, "Type": rel_type, "Target": target}
        if external:
            row["TargetMode"] = "External"
        self.rows.append(row)
        return rid

    def xml(self) -> bytes:
        parts = []
        for row in self.rows:
            bits = [f'{key}="{row[key]}"' for key in ("Id", "Type", "Target", "TargetMode") if key in row]
            parts.append("<Relationship " + " ".join(bits) + "/>")
        body = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            + "".join(parts)
            + "</Relationships>"
        )
        return body.encode("utf-8")


def add_rect(
    tree: ET.Element,
    sid: int,
    name: str,
    x: int,
    y: int,
    w: int,
    h: int,
    fill: str | None,
    line: str | None = None,
    preset: str = "rect",
) -> int:
    sp = el(P, "sp")
    nv = el(P, "nvSpPr")
    nv.append(el(P, "cNvPr", {"id": str(sid), "name": name}))
    nv.append(el(P, "cNvSpPr"))
    nv.append(el(P, "nvPr"))
    sp.append(nv)
    sp_pr = el(P, "spPr")
    sp_pr.append(xfrm(x, y, w, h))
    geom = el(A, "prstGeom", {"prst": preset})
    geom.append(el(A, "avLst"))
    sp_pr.append(geom)
    if fill:
        sp_pr.append(solid(fill))
    else:
        sp_pr.append(el(A, "noFill"))
    ln = el(A, "ln")
    if line:
        ln.append(solid(line))
    else:
        ln.append(el(A, "noFill"))
    sp_pr.append(ln)
    sp.append(sp_pr)
    tx = el(P, "txBody")
    tx.append(el(A, "bodyPr"))
    tx.append(el(A, "lstStyle"))
    tx.append(el(A, "p"))
    sp.append(tx)
    tree.append(sp)
    return sid + 1


def add_textbox(
    tree: ET.Element,
    sid: int,
    name: str,
    x: int,
    y: int,
    w: int,
    h: int,
    paragraphs: list[tuple[str, int, str, str, bool]],
    align: str = "l",
    anchor: str = "ctr",
    wrap: str = "none",
    link_rid: str | None = None,
    tooltip: str = "",
    fill: str | None = None,
    preset: str = "rect",
) -> int:
    sp = el(P, "sp")
    nv = el(P, "nvSpPr")
    c_nv = el(P, "cNvPr", {"id": str(sid), "name": name, "descr": paragraphs[0][0][:80]})
    if link_rid:
        c_nv.append(el(A, "hlinkClick", {q(R, "id"): link_rid, "tooltip": tooltip}))
    nv.append(c_nv)
    nv.append(el(P, "cNvSpPr", {"txBox": "1"}))
    nv.append(el(P, "nvPr"))
    sp.append(nv)
    sp_pr = el(P, "spPr")
    sp_pr.append(xfrm(x, y, w, h))
    geom = el(A, "prstGeom", {"prst": preset})
    geom.append(el(A, "avLst"))
    sp_pr.append(geom)
    if fill:
        sp_pr.append(solid(fill))
    else:
        sp_pr.append(el(A, "noFill"))
    ln = el(A, "ln")
    ln.append(el(A, "noFill"))
    sp_pr.append(ln)
    sp.append(sp_pr)
    tx = el(P, "txBody")
    tx.append(
        el(
            A,
            "bodyPr",
            {"lIns": "80000", "rIns": "80000", "tIns": "20000", "bIns": "20000", "anchor": anchor, "wrap": wrap, "rtlCol": "0"},
        )
    )
    tx.append(el(A, "lstStyle"))
    for text, size, color, font, bold in paragraphs:
        tx.append(paragraph([run(text, size, color, font, bold)], align, size))
    sp.append(tx)
    tree.append(sp)
    return sid + 1


def add_pic(
    tree: ET.Element,
    sid: int,
    name: str,
    descr: str,
    x: int,
    y: int,
    w: int,
    h: int,
    embed: str,
    link_rid: str,
    tooltip: str,
) -> int:
    pic = el(P, "pic")
    nv = el(P, "nvPicPr")
    c_nv = el(P, "cNvPr", {"id": str(sid), "name": name, "descr": descr})
    c_nv.append(el(A, "hlinkClick", {q(R, "id"): link_rid, "tooltip": tooltip}))
    nv.append(c_nv)
    locks = el(P, "cNvPicPr")
    locks.append(el(A, "picLocks", {"noChangeAspect": "1"}))
    nv.append(locks)
    nv.append(el(P, "nvPr"))
    pic.append(nv)
    blip_fill = el(P, "blipFill")
    blip_fill.append(el(A, "blip", {q(R, "embed"): embed}))
    stretch = el(A, "stretch")
    stretch.append(el(A, "fillRect"))
    blip_fill.append(stretch)
    pic.append(blip_fill)
    sp_pr = el(P, "spPr")
    sp_pr.append(xfrm(x, y, w, h))
    geom = el(A, "prstGeom", {"prst": "rect"})
    geom.append(el(A, "avLst"))
    sp_pr.append(geom)
    pic.append(sp_pr)
    tree.append(pic)
    return sid + 1


def footer_height() -> int:
    top_pad = 36_000
    disc_h = 150_000
    copy_h = 170_000
    gap = 28_000
    bottom = 46_000
    return top_pad + disc_h + copy_h + gap + ICON + bottom


def slide_height() -> int:
    return FOOTER_TOP + footer_height()


def place_links() -> list[tuple[object, int, int]]:
    """Return (link, icon_x, label_x) left-aligned on the deck margin."""
    gap_icon = 70_000
    gap_item = 240_000
    widths = []
    for link in FOOTER_LINKS:
        label_w = text_width(link.label, LABEL_PT) + 50_000
        widths.append(label_w)
    total = sum(ICON + gap_icon + width for width in widths) + gap_item * (len(FOOTER_LINKS) - 1)
    inner = SLIDE_W - 2 * MARGIN_X
    while total > inner and gap_item > 80_000:
        gap_item -= 20_000
        total = sum(ICON + gap_icon + width for width in widths) + gap_item * (len(FOOTER_LINKS) - 1)
    if total > inner:
        raise SystemExit("footer link row does not fit the slide")
    cursor = MARGIN_X
    placed = []
    for link, label_w in zip(FOOTER_LINKS, widths):
        placed.append((link, cursor, cursor + ICON + gap_icon, label_w))
        cursor += ICON + gap_icon + label_w + gap_item
    return placed


def add_footer(tree: ET.Element, rels: SlideRels, pngs: dict[str, str], sid: int) -> int:
    band_h = footer_height()
    sid = add_rect(tree, sid, "cml-footer-bar", 0, FOOTER_TOP, SLIDE_W, band_h, BAR)
    sid = add_rect(tree, sid, "cml-footer-rule", 0, FOOTER_TOP, SLIDE_W, 19_050, RULE)
    inner_w = SLIDE_W - 2 * MARGIN_X
    top_pad = 28_000
    disc_y = FOOTER_TOP + top_pad
    disc_h = 150_000
    copy_y = disc_y + disc_h
    copy_h = 170_000
    icon_y = copy_y + copy_h + 20_000
    sid = add_textbox(
        tree,
        sid,
        "cml-footer-disclaimer",
        MARGIN_X - 80_000,
        disc_y,
        inner_w + 160_000,
        disc_h,
        [(DISCLAIMER, DISC_PT * 100, DISC_COLOR, FOOTER_FONT, False)],
        align="l",
        anchor="ctr",
        wrap="none",
    )
    sid = add_textbox(
        tree,
        sid,
        "cml-footer-copy",
        MARGIN_X - 80_000,
        copy_y,
        inner_w,
        copy_h,
        [(FOOTER_LINE, COPY_PT * 100, COPY_COLOR, FOOTER_FONT, True)],
        align="l",
        anchor="ctr",
        wrap="none",
    )
    image_rids: dict[str, str] = {}
    for link, icon_x, label_x, label_w in place_links():
        icon = link.icon
        if icon not in image_rids:
            image_rids[icon] = rels.add(IMAGE_REL, f"../media/{pngs[icon]}")
        link_rid = rels.add(LINK_REL, link.href, external=True)
        tip = f"{link.label} — {link.href}"
        sid = add_pic(
            tree,
            sid,
            f"cml-footer-icon-{link.key}",
            link.label,
            icon_x,
            icon_y,
            ICON,
            ICON,
            image_rids[icon],
            link_rid,
            tip,
        )
        sid = add_textbox(
            tree,
            sid,
            f"cml-footer-label-{link.key}",
            label_x - 80_000,
            icon_y,
            label_w + 80_000,
            ICON,
            [(link.label, LABEL_PT * 100, LABEL_COLOR, FOOTER_FONT, False)],
            align="l",
            anchor="ctr",
            wrap="none",
            link_rid=link_rid,
            tooltip=tip,
        )
    return sid


def strip_brand_shapes(root: ET.Element) -> None:
    tree = root.find(f".//{q(P, 'spTree')}")
    if tree is None:
        raise SystemExit("slide is missing a shape tree")
    for child in list(tree):
        if shape_name(child).startswith("cml-"):
            tree.remove(child)


def add_closing_body(tree: ET.Element, rels: SlideRels, sid: int) -> int:
    x = 720_000
    sid = add_rect(tree, sid, "cml-close-accent", 0, 0, 109_728, FOOTER_TOP, TEAL)
    sid = add_textbox(
        tree,
        sid,
        "cml-close-kicker",
        x,
        1_280_000,
        8_000_000,
        320_000,
        [("Independent student project", 1400, TEAL, FOOTER_FONT, True)],
        anchor="b",
    )
    sid = add_textbox(
        tree,
        sid,
        CLOSE_MARK,
        x,
        1_640_000,
        11_000_000,
        780_000,
        [("Cypher Monkey Labs", 4000, "FFFFFF", TITLE_FONT, False)],
        anchor="ctr",
    )
    sid = add_textbox(
        tree,
        sid,
        "cml-close-sub",
        x,
        2_480_000,
        10_800_000,
        620_000,
        [("Enterprise voice, contact center, and cloud migration, for independent study.", 1800, BODY, FOOTER_FONT, False)],
        anchor="t",
        wrap="square",
    )
    sid = add_rect(tree, sid, "cml-close-rule", x, 3_180_000, 2_200_000, 19_050, TEAL)
    facts = (
        (str(EXPECTED_SLIDES), "slides in this briefing"),
        ("580", "sections in the campus"),
        ("Offline", "open it in the browser"),
    )
    fact_w = 3_300_000
    for index, (value, caption) in enumerate(facts):
        sid = add_textbox(
            tree,
            sid,
            f"cml-close-fact-{index}",
            x + index * (fact_w + 180_000),
            3_420_000,
            fact_w,
            820_000,
            [
                (value, 2800, TEAL, TITLE_FONT, False),
                (caption, 1400, MUTED, FOOTER_FONT, False),
            ],
            align="l",
            anchor="ctr",
        )
    app_rid = rels.add(LINK_REL, APP_HREF, external=True)
    sid = add_textbox(
        tree,
        sid,
        "cml-close-app",
        x,
        4_500_000,
        3_200_000,
        560_000,
        [("Open the app", 1600, "FFFFFF", FOOTER_FONT, True)],
        align="ctr",
        anchor="ctr",
        link_rid=app_rid,
        tooltip=f"Open the app — {APP_HREF}",
        fill=TEAL_DEEP,
        preset="roundRect",
    )
    sid = add_textbox(
        tree,
        sid,
        "cml-close-note",
        x,
        5_200_000,
        10_400_000,
        700_000,
        [(
            "This deck is the briefing. The campus is the practice: call flows, cheat sheets, and drills you can check.",
            1600,
            BODY,
            FOOTER_FONT,
            False,
        )],
        anchor="t",
        wrap="square",
    )
    return sid


def prepare_pngs() -> dict[str, bytes]:
    """White PNGs keyed by icon stem."""
    stems = {link.icon for link in FOOTER_LINKS}
    pngs: dict[str, bytes] = {}
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp)
        for stem in sorted(stems):
            src = ICON_DIR / f"{stem}.svg"
            if not src.is_file():
                raise SystemExit(f"missing icon {src}. Add the svg, then the one FooterLink line.")
            white = white_svg(src.read_text(encoding="utf-8"))
            svg_path = folder / f"{stem}.svg"
            png_path = folder / f"{stem}.png"
            svg_path.write_text(white, encoding="utf-8")
            subprocess.check_call(
                ["rsvg-convert", "-w", "256", "-h", "256", "-o", str(png_path), str(svg_path)],
                stdout=subprocess.DEVNULL,
            )
            pngs[stem] = png_path.read_bytes()
    return pngs


def white_svg(src: str) -> str:
    if "stroke=" in src:
        text = src
        text = re.sub(r'stroke="[^"]*"', 'stroke="#FFFFFF"', text)
        return text
    text = re.sub(r"<path\b(?![^>]*\bfill=)", '<path fill="#FFFFFF"', src)
    return text


def load_parts(path: Path) -> tuple[list[str], dict[str, bytes]]:
    order: list[str] = []
    parts: dict[str, bytes] = {}
    with zipfile.ZipFile(path) as zf:
        for info in zf.infolist():
            order.append(info.filename)
            parts[info.filename] = zf.read(info.filename)
    return order, parts


def save_parts(path: Path, order: list[str], parts: dict[str, bytes]) -> None:
    tmp = path.with_suffix(".pptx.tmp")
    seen: set[str] = set()
    with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name in order:
            if name in parts and name not in seen:
                zf.writestr(name, parts[name])
                seen.add(name)
        for name, data in parts.items():
            if name not in seen:
                zf.writestr(name, data)
    tmp.replace(path)


def slide_number(name: str) -> int:
    found = re.search(r"slide(\d+)\.xml$", name)
    if not found:
        raise SystemExit(f"not a slide part: {name}")
    return int(found.group(1))


def drop_closing_slide(parts: dict[str, bytes]) -> None:
    closing = [
        name
        for name, data in parts.items()
        if re.fullmatch(r"ppt/slides/slide\d+\.xml", name) and CLOSE_MARK.encode() in data
    ]
    if not closing:
        return
    if len(closing) != 1:
        raise SystemExit(f"expected one closing slide, found {closing}")
    target = "slides/" + Path(closing[0]).name
    rels_name = "ppt/_rels/presentation.xml.rels"
    rels = parts[rels_name].decode("utf-8")
    match = re.search(
        rf'<Relationship Id="(rId\d+)" Type="{re.escape(SLIDE_REL)}" Target="{re.escape(target)}"/>',
        rels,
    )
    if not match:
        raise SystemExit(f"closing slide {target} has no presentation relationship")
    rid = match.group(1)
    rels = rels.replace(match.group(0), "")
    parts[rels_name] = rels.encode("utf-8")
    pres_name = "ppt/presentation.xml"
    pres = parts[pres_name].decode("utf-8")
    pres = re.sub(rf'<p:sldId\b[^>]*r:id="{rid}"[^>]*/>', "", pres, count=1)
    parts[pres_name] = pres.encode("utf-8")
    content = parts["[Content_Types].xml"].decode("utf-8")
    part_name = "/" + closing[0]
    content = re.sub(rf'<Override PartName="{re.escape(part_name)}" ContentType="[^"]+"/>', "", content, count=1)
    parts["[Content_Types].xml"] = content.encode("utf-8")
    del parts[closing[0]]
    rel_part = f"ppt/slides/_rels/{Path(closing[0]).name}.rels"
    parts.pop(rel_part, None)


def set_slide_size(parts: dict[str, bytes]) -> None:
    pres = parts["ppt/presentation.xml"].decode("utf-8")
    updated, count = re.subn(
        r'(<p:sldSz cx="12192000" cy=")\d+(")',
        rf"\g<1>{slide_height()}\2",
        pres,
        count=1,
    )
    if count != 1:
        raise SystemExit("could not set slide size")
    parts["ppt/presentation.xml"] = updated.encode("utf-8")
    app = parts["docProps/app.xml"].decode("utf-8")
    app, count = re.subn(r"<Slides>\d+</Slides>", f"<Slides>{EXPECTED_SLIDES}</Slides>", app, count=1)
    if count != 1:
        raise SystemExit("could not set slide count metadata")
    parts["docProps/app.xml"] = app.encode("utf-8")


def append_closing_relationship(parts: dict[str, bytes], filename: str) -> None:
    rels_name = "ppt/_rels/presentation.xml.rels"
    rels = parts[rels_name].decode("utf-8")
    ids = [int(n) for n in re.findall(r'Id="rId(\d+)"', rels)]
    rid = f"rId{max(ids) + 1}"
    pres = parts["ppt/presentation.xml"].decode("utf-8")
    sld_ids = [int(n) for n in re.findall(r'<p:sldId id="(\d+)"', pres)]
    sld_id = max(sld_ids) + 1
    rel = f'<Relationship Id="{rid}" Type="{SLIDE_REL}" Target="slides/{filename}"/>'
    if "</Relationships>" not in rels:
        raise SystemExit("presentation rels are missing a close tag")
    parts[rels_name] = rels.replace("</Relationships>", rel + "</Relationships>").encode("utf-8")
    slide_tag = f'<p:sldId id="{sld_id}" r:id="{rid}"/>'
    parts["ppt/presentation.xml"] = pres.replace("</p:sldIdLst>", slide_tag + "</p:sldIdLst>").encode("utf-8")
    override = (
        f'<Override PartName="/ppt/slides/{filename}" '
        'ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
    )
    content = parts["[Content_Types].xml"].decode("utf-8")
    if f'/ppt/slides/{filename}"' not in content:
        parts["[Content_Types].xml"] = content.replace("</Types>", override + "</Types>").encode("utf-8")


def sp_tree(root: ET.Element) -> ET.Element:
    tree = root.find(f".//{q(P, 'spTree')}")
    if tree is None:
        raise SystemExit("slide is missing a shape tree")
    return tree


def bottoms(root: ET.Element) -> list[tuple[str, int]]:
    found = []
    for node in root.iter():
        if node.tag not in {q(P, "sp"), q(P, "pic"), q(P, "cxnSp"), q(P, "graphicFrame")}:
            continue
        off = None
        ext = None
        for child in node.iter():
            if child.tag == q(A, "off") and off is None:
                off = child
            elif child.tag == q(A, "ext") and ext is None:
                ext = child
        if off is None or ext is None:
            continue
        name = shape_name(node)
        bottom = int(off.get("y") or 0) + int(ext.get("cy") or 0)
        found.append((name, bottom))
    return found


def assert_no_overlap(parts: dict[str, bytes]) -> None:
    slides = sorted(
        (name for name in parts if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)),
        key=slide_number,
    )
    if len(slides) != EXPECTED_SLIDES:
        raise SystemExit(f"expected {EXPECTED_SLIDES} slides, found {len(slides)}")
    limit = FOOTER_TOP + 2000
    for name in slides:
        root = ET.fromstring(parts[name])
        for shape, bottom in bottoms(root):
            if shape.startswith("cml-footer-"):
                continue
            if bottom > limit:
                raise SystemExit(f"{name} shape {shape} ends at {bottom}, inside the footer band")
        blob = parts[name].decode("utf-8")
        if DISCLAIMER not in blob or FOOTER_LINE not in blob:
            raise SystemExit(f"{name} is missing the footer copy")
        for link in FOOTER_LINKS:
            if link.href not in parts[f"ppt/slides/_rels/{Path(name).name}.rels"].decode("utf-8"):
                raise SystemExit(f"{name} is missing {link.href}")


def brand_deck() -> None:
    pngs = prepare_pngs()
    media_names = {stem: f"cml-{stem}.png" for stem in pngs}
    order, parts = load_parts(DECK)
    drop_closing_slide(parts)
    register_namespaces(parts["ppt/slides/slide1.xml"])
    content_slides = sorted(
        (name for name in parts if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)),
        key=slide_number,
    )
    if len(content_slides) != BASE_SLIDES:
        raise SystemExit(f"expected {BASE_SLIDES} content slides, found {len(content_slides)}")
    for name in content_slides:
        root = ET.fromstring(parts[name])
        strip_brand_shapes(root)
        rel_name = f"ppt/slides/_rels/{Path(name).name}.rels"
        rels = SlideRels(parts[rel_name].decode("utf-8"))
        add_footer(sp_tree(root), rels, media_names, max_shape_id(root) + 1)
        parts[name] = serialize(root)
        parts[rel_name] = rels.xml()
    template = parts["ppt/slides/slide3.xml"]
    root = ET.fromstring(template)
    srgb = root.find(f".//{q(P, 'bg')}//{q(A, 'srgbClr')}")
    if srgb is None:
        raise SystemExit("section slide has no background color")
    srgb.set("val", NAVY)
    tree = sp_tree(root)
    for child in list(tree):
        if not child.tag.endswith("nvGrpSpPr") and not child.tag.endswith("grpSpPr"):
            tree.remove(child)
    rels = SlideRels(
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        f'<Relationship Id="rId1" Type="{LAYOUT_REL}" Target="../slideLayouts/slideLayout1.xml"/>'
        "</Relationships>"
    )
    sid = add_closing_body(tree, rels, 2)
    add_footer(tree, rels, media_names, sid)
    filename = f"slide{EXPECTED_SLIDES}.xml"
    parts[f"ppt/slides/{filename}"] = serialize(root)
    parts[f"ppt/slides/_rels/{filename}.rels"] = rels.xml()
    append_closing_relationship(parts, filename)
    set_slide_size(parts)
    for stem, blob in pngs.items():
        parts[f"ppt/media/{media_names[stem]}"] = blob
    assert_no_overlap(parts)
    save_parts(DECK, order, parts)
    print(f"branded {DECK.name}: {EXPECTED_SLIDES} slides, footer on each, close at {filename}")


def badge_inner(stem: str) -> str:
    src = (ICON_DIR / f"{stem}.svg").read_text(encoding="utf-8")
    if "stroke=" in src:
        inner = re.search(r"<svg[^>]*>(.*)</svg>", src, re.S)
        if inner is None:
            raise SystemExit(f"{stem}.svg has no body")
        body = re.sub(r"<title>.*?</title>", "", inner.group(1), flags=re.S)
        return re.sub(r'stroke="[^"]*"', 'stroke="#F4F7FB"', body)
    paths = re.findall(r'\bd="([^"]+)"', src)
    if not paths:
        raise SystemExit(f"{stem}.svg has no path")
    return "".join(f'<path fill="#F4F7FB" d="{d}"/>' for d in paths)


def write_badges() -> str:
    BADGE_DIR.mkdir(parents=True, exist_ok=True)
    height = 56
    links = []
    for link in readme_links():
        label = link.cta
        text_px = int(text_units(label) * 18) + 8
        width = 16 + 22 + 12 + text_px + 18
        fill = TEAL_DEEP if link.key == "app" else NAVY
        stroke = "5EEAD4" if link.key == "app" else TEAL
        icon = badge_inner(link.icon)
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-label="{label}">'
            f'<rect width="{width}" height="{height}" rx="10" fill="#{fill}"/>'
            f'<rect x="1.5" y="1.5" width="{width - 3}" height="{height - 3}" rx="8.5" fill="none" '
            f'stroke="#{stroke}" stroke-width="2"/>'
            f'<g transform="translate(16,17) scale(0.9167)">{icon}</g>'
            f'<text x="50" y="35" fill="#F4F7FB" font-family="Segoe UI, Helvetica, Arial, sans-serif" '
            f'font-size="18" font-weight="700">{label}</text></svg>'
        )
        (BADGE_DIR / f"{link.key}.svg").write_text(svg, encoding="utf-8")
        links.append(
            f'<a href="{link.href}"><img src="./docs/assets/badges/{link.key}.svg" alt="{label}" height="56"/></a>'
        )
    block = "<!-- cml-badges:start -->\n" + "\n&nbsp;\n".join(links) + "\n<!-- cml-badges:end -->"
    if README.is_file():
        text = README.read_text(encoding="utf-8")
        updated, count = re.subn(
            r"<!-- cml-badges:start -->.*?<!-- cml-badges:end -->",
            block,
            text,
            count=1,
            flags=re.S,
        )
        if count == 1 and updated != text:
            README.write_text(updated, encoding="utf-8")
            print("refreshed README badge block")
    return block


def main() -> int:
    if not DECK.is_file():
        print(f"missing deck: {DECK}", file=sys.stderr)
        return 1
    write_badges()
    brand_deck()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
