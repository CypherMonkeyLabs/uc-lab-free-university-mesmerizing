#!/usr/bin/env python3
"""Pack the current campus HTML into the public zip.

The zip member name matches the file learners open after unzip.
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "campus" / "uc-lab-free-university.html"
ZIP = ROOT / "releases" / "uc-lab-free-university.html.zip"
MEMBER = "uc-lab-free-university.html"


def main() -> int:
    if not HTML.is_file():
        print(f"missing campus: {HTML}", file=sys.stderr)
        return 1
    ZIP.parent.mkdir(parents=True, exist_ok=True)
    tmp = ZIP.with_suffix(".zip.tmp")
    with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        zf.write(HTML, arcname=MEMBER)
    tmp.replace(ZIP)
    with zipfile.ZipFile(ZIP) as zf:
        info = zf.getinfo(MEMBER)
        print(f"wrote {ZIP.relative_to(ROOT)} ({ZIP.stat().st_size} bytes, member {info.file_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
