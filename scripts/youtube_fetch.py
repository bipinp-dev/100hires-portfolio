#!/usr/bin/env python3
"""
youtube_fetch.py

Fetches YouTube channel information for a list of search queries.

Input:
    research/candidates.json (optional)

Output:
    research/youtube_results.json

Environment:
    <AIzaSyCb4TjmB74a2ea2QnSix426u_O3Xj_CV24>

Usage:
    python scripts/youtube_fetch.py
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = ROOT / "research" / "candidates.json"
OUTPUT_FILE = ROOT / "research" / "youtube_results.json"

API_KEY = "AIzaSyCb4TjmB74a2ea2QnSix426u_O3Xj_CV24"


def load_candidates():
    if not INPUT_FILE.exists():
        return []

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in ("results", "candidates", "experts"):
            if isinstance(data.get(key), list):
                return data[key]

    return []


def get_service():
    if not API_KEY:
        raise RuntimeError("Missing YOUTUBE_API_KEY environment variable.")

    return build(
        "youtube",
        "v3",
        developerKey=API_KEY,
        cache_discovery=False,
    )


def search_channel(service, query):
    response = (
        service.search()
        .list(
            part="snippet",
            q=query,
            type="channel",
            maxResults=1,
        )
        .execute()
    )

    items = response.get("items", [])

    if not items:
        return None

    item = items[0]

    return {
        "author": item["snippet"]["channelTitle"],
        "channel_id": item["snippet"]["channelId"],
        "description": item["snippet"].get("description", ""),
    }


def main():
    service = get_service()
    candidates = load_candidates()[:10]

    results = []
    MAX_EXPERTS = 10

    for candidate in candidates:
        if isinstance(candidate, dict):
            query = (
                candidate.get("author")
                or candidate.get("name")
                or candidate.get("query")
            )

            query = query.split(" - ")[0].strip()
        else:
            query = str(candidate)

        if not query:
            continue

        try:
            channel = search_channel(service, query)

            if channel:
                results.append(channel)
                print(f"[OK] {query}")

                if len(results) >= MAX_EXPERTS:
                    break

            else:
                print(f"[NOT FOUND] {query}")

        except HttpError as e:
            print(f"[API ERROR] {query}: {e}")

        except Exception as e:
            print(f"[ERROR] {query}: {e}")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(results)} channels to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()