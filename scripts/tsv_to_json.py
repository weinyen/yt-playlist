#!/usr/bin/env python3
"""Regenerate data/playlist.json from data/playlist.tsv.

Each line of the TSV is `title<TAB>url`. A title of exactly "NA" is
treated as unknown/missing. The video id is extracted from the URL's
`v=` query parameter.

Usage: python3 scripts/tsv_to_json.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TSV_PATH = ROOT / "data" / "playlist.tsv"
JSON_PATH = ROOT / "data" / "playlist.json"

VIDEO_ID_RE = re.compile(r"[?&]v=([A-Za-z0-9_-]{6,})")


def main():
    items = []
    with TSV_PATH.open(encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n").rstrip("\r")
            if not line:
                continue
            title, url = line.split("\t", 1)
            match = VIDEO_ID_RE.search(url)
            items.append({
                "title": None if title == "NA" else title,
                "url": url,
                "id": match.group(1) if match else None,
            })

    with JSON_PATH.open("w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, separators=(",", ":"))

    print(f"wrote {len(items)} items to {JSON_PATH}")


if __name__ == "__main__":
    main()
