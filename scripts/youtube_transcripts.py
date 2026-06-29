#!/usr/bin/env python3
"""
youtube_transcripts.py

Reads:
    research/youtube_results.json

Downloads:
    - Latest 3 videos from each valid YouTube channel
    - Transcripts using youtube-transcript-api

Saves:
    research/youtube-transcripts/<author>/<video_title>.md

Updates:
    research/sources.md

Environment:
    YOUTUBE_API_KEY=<AIzaSyCb4TjmB74a2ea2QnSix426u_O3Xj_CV24>

Requirements:
    pip install google-api-python-client youtube-transcript-api
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)

# ---------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

RESULTS_FILE = ROOT / "research" / "youtube_results.json"
OUTPUT_DIR = ROOT / "research" / "youtube-transcripts"
SOURCES_MD = ROOT / "research" / "sources.md"

API_KEY = "AIzaSyCb4TjmB74a2ea2QnSix426u_O3Xj_CV24"

# ---------------------------------------------------------------------


def safe_filename(name: str) -> str:
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name[:180]


def load_results() -> List[Dict]:
    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in ("results", "authors", "channels", "experts"):
            if key in data and isinstance(data[key], list):
                return data[key]

    raise ValueError("Unsupported youtube_results.json format")


def get_service():
    if not API_KEY:
        raise RuntimeError(
            "Missing YOUTUBE_API_KEY environment variable."
        )

    return build(
        "youtube",
        "v3",
        developerKey=API_KEY,
        cache_discovery=False,
    )


def latest_videos(service, channel_id: str, limit: int = 3) -> List[Dict]:
    response = (
        service.search()
        .list(
            part="snippet",
            channelId=channel_id,
            order="date",
            type="video",
            maxResults=limit,
        )
        .execute()
    )

    videos = []

    for item in response.get("items", []):
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]

        videos.append(
            {
                "id": video_id,
                "title": title,
            }
        )

    return videos


def fetch_transcript(video_id: str) -> Optional[str]:
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)

        lines = [entry["text"] for entry in transcript]

        return "\n".join(lines)

    except (
        NoTranscriptFound,
        TranscriptsDisabled,
        VideoUnavailable,
    ):
        return None

    except Exception:
        return None


def write_markdown(author: str, title: str, video_id: str, transcript: str):
    author_dir = OUTPUT_DIR / safe_filename(author)
    author_dir.mkdir(parents=True, exist_ok=True)

    file_path = author_dir / f"{safe_filename(title)}.md"

    content = f"""# {title}

Video:
https://www.youtube.com/watch?v={video_id}

---

{transcript}
"""

    file_path.write_text(content, encoding="utf-8")

    return file_path


def append_sources(author: str, title: str, video_id: str, file_path: Path):
    SOURCES_MD.parent.mkdir(parents=True, exist_ok=True)

    if SOURCES_MD.exists():
        existing = SOURCES_MD.read_text(encoding="utf-8")
    else:
        existing = "# Research Sources\n\n"

    entry = (
        f"- **{author}** — {title}\n"
        f"  - Video: https://www.youtube.com/watch?v={video_id}\n"
        f"  - Transcript: {file_path.relative_to(ROOT).as_posix()}\n\n"
    )

    if entry not in existing:
        with open(SOURCES_MD, "a", encoding="utf-8") as f:
            f.write(entry)


def author_name(record: Dict) -> str:
    for key in (
        "author",
        "name",
        "expert",
        "channel_name",
        "title",
    ):
        if record.get(key):
            return str(record[key])

    return "Unknown"


def channel_id(record: Dict) -> str:
    for key in (
        "channel_id",
        "channelId",
        "youtube_channel_id",
    ):
        value = record.get(key)
        if value:
            return str(value).strip()

    return ""


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    records = load_results()[:10]

    service = get_service()

    for record in records:
        author = author_name(record)
        cid = channel_id(record)

        if not cid:
            print(f"[SKIP] {author} (no channel id)")
            continue

        try:
            videos = latest_videos(service, cid, limit=1)

        except HttpError as e:
            print(f"[API ERROR] {author}: {e}")
            continue

        except Exception as e:
            print(f"[ERROR] {author}: {e}")
            continue

        for video in videos:
            transcript = fetch_transcript(video["id"])

            if not transcript:
                print(
                    f"[NO TRANSCRIPT] {author} -> {video['title']}"
                )
                continue

            path = write_markdown(
                author,
                video["title"],
                video["id"],
                transcript,
            )

            append_sources(
                author,
                video["title"],
                video["id"],
                path,
            )

            print(f"[OK] {author} -> {video['title']}")


if __name__ == "__main__":
    main()