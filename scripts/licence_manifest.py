#!/usr/bin/env python3
"""Check THIRD_PARTY_MANIFEST.json hashes and notices.

  python3 scripts/licence_manifest.py
  python3 scripts/licence_manifest.py --write
"""
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
MAN = ROOT / "THIRD_PARTY_MANIFEST.json"
SCAN = [
    "vendor",
    "assets/fonts",
    "flagship/assets/vendor",
    "campus/assets/vendor",
]


def sha(path):
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def main():
    data = json.loads(MAN.read_text())
    files = {item["path"]: item for comp in data["components"] for item in comp["files"]}
    problems = []
    if "--write" in sys.argv:
        for path, item in files.items():
            item["sha256"] = sha(ROOT / path)
        MAN.write_text(json.dumps(data, indent=2) + "\n")
        print("rewrote", MAN)
        return 0
    for path, item in files.items():
        target = ROOT / path
        if not target.is_file():
            problems.append(f"listed but missing: {path}")
        elif sha(target) != item["sha256"]:
            problems.append(f"hash mismatch: {path}")
    known = set(files)
    for folder in SCAN:
        base = ROOT / folder
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if path.is_file() and path.relative_to(ROOT).as_posix() not in known:
                problems.append(f"vendored file not in manifest: {path.relative_to(ROOT)}")
    for comp in data["components"]:
        for key in ("name", "version", "licence", "url", "licence_file"):
            if not comp.get(key):
                problems.append(f"{comp.get('name')}: missing {key}")
        licence_file = comp.get("licence_file") or ""
        if licence_file and not licence_file.startswith("(") and not (ROOT / licence_file).is_file():
            problems.append(f"{comp['name']}: licence file missing {licence_file}")
    notices = (ROOT / "THIRD_PARTY_NOTICES.md").read_text()
    if re.search(r"\bverify\b", notices, re.I):
        problems.append("THIRD_PARTY_NOTICES.md still contains an unresolved verify note")
    for problem in problems:
        print("FAIL", problem)
    print("manifest:", len(files), "files,", len(data["components"]), "components,", len(problems), "problems")
    return 1 if problems else 0


sys.exit(main())
