#!/usr/bin/env python3
"""
linkedin_posts.py

Reads:
    research/sources.md

Downloads:
    Latest LinkedIn posts for each expert (manual URL if available)

Outputs:
    research/linkedin-posts/<author>.md

Notes:
    LinkedIn does not provide a free public API for scraping personal posts.
    This script extracts LinkedIn profile URLs (if present) from sources.md
    and creates structured markdown files ready for manual collection.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SOURCES_FILE = ROOT / "research" / "sources.md"
OUTPUT_DIR = ROOT / "research" / "linkedin-posts"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def safe_filename(name: str) ->str:
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


import json

RANKED_FILE = ROOT / "research" / "ranked_candidates.json"

def parse_sources():
    with open(RANKED_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    experts = {}

    for item in data[:10]:
        experts[item["name"]] = {
            "linkedin": item.get("url", "")
        }

    return experts


def create_markdown(author, profile):
    outfile = OUTPUT_DIR / f"{safe_filename(author)}.md"

    lines = [
        f"# {author}",
        "",
        "## LinkedIn Profile",
        profile if profile else "_No LinkedIn profile URL found._",
        "",
        "## Recent Posts",
        "",
        "> Paste the latest LinkedIn posts here.",
        "",
        "---",
        "",
        "### Post 1",
        "",
        "**Date:**",
        "",
        "**URL:**",
        "",
        "**Content:**",
        "",
        "---",
        "",
        "### Post 2",
        "",
        "**Date:**",
        "",
        "**URL:**",
        "",
        "**Content:**",
        "",
        "---",
        "",
        "### Post 3",
        "",
        "**Date:**",
        "",
        "**URL:**",
        "",
        "**Content:**",
        "",
    ]

    outfile.write_text("\n".join(lines), encoding="utf-8")
    return outfile


def main():
    experts = parse_sources()

    for author, data in experts.items():
        path = create_markdown(author, data["linkedin"])
        print(f"[OK] {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()