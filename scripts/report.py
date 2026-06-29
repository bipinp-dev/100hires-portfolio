#!/usr/bin/env python3
"""
report.py

Generates:
    research/report.md

Reads:
    research/sources.md
    research/analysis.json
    research/youtube-transcripts/
    research/linkedin-posts/

Usage:
    python scripts/report.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RESEARCH = ROOT / "research"

SOURCES = RESEARCH / "sources.md"
ANALYSIS = RESEARCH / "analysis.json"

YOUTUBE = RESEARCH / "youtube-transcripts"
LINKEDIN = RESEARCH / "linkedin-posts"

REPORT = RESEARCH / "report.md"


def count_files(folder: Path) -> int:
    if not folder.exists():
        return 0
    return len(list(folder.rglob("*.md")))


def load_analysis():
    if not ANALYSIS.exists():
        return {}

    with open(ANALYSIS, "r", encoding="utf-8") as f:
        return json.load(f)


def markdown_table(data):
    lines = [
        "| Expert | Documents | Words |",
        "|--------|----------:|------:|",
    ]

    for author, stats in sorted(data.items()):
        lines.append(
            f"| {author} | {stats.get('documents',0)} | {stats.get('total_words',0)} |"
        )

    return "\n".join(lines)


def top_keywords(author_data):
    text = []

    for word, count in author_data.get("top_keywords", [])[:10]:
        text.append(f"- **{word}** ({count})")

    return "\n".join(text)


def main():

    analysis = load_analysis()

    youtube = analysis.get("youtube", {})
    linkedin = analysis.get("linkedin", {})
    summary = analysis.get("summary", {})

    transcript_files = count_files(YOUTUBE)
    linkedin_files = count_files(LINKEDIN)

    report = []

    report.append("# Expert Research Report\n")

    report.append("## Project Summary\n")

    report.append(
        "This report summarizes the research corpus collected from "
        "YouTube transcripts and LinkedIn research.\n"
    )

    report.append("## Dataset Statistics\n")

    report.append(f"- YouTube Experts: **{summary.get('youtube_authors',0)}**")
    report.append(f"- LinkedIn Experts: **{summary.get('linkedin_authors',0)}**")
    report.append(f"- Transcript Files: **{transcript_files}**")
    report.append(f"- LinkedIn Files: **{linkedin_files}**")
    report.append(f"- Total Documents: **{summary.get('youtube_documents',0)}**")
    report.append(f"- Total Words: **{summary.get('youtube_words',0)}**\n")

    if youtube:
        report.append("## Expert Statistics\n")
        report.append(markdown_table(youtube))
        report.append("")

    for author, stats in sorted(youtube.items()):

        report.append(f"---\n")
        report.append(f"## {author}\n")

        report.append(f"- Documents: {stats.get('documents',0)}")
        report.append(f"- Words: {stats.get('total_words',0)}\n")

        report.append("### Top Keywords\n")
        report.append(top_keywords(stats))
        report.append("")

        report.append("### Top Bigrams\n")

        for phrase, count in stats.get("top_bigrams", [])[:5]:
            report.append(f"- {phrase} ({count})")

        report.append("")

        report.append("### Top Trigrams\n")

        for phrase, count in stats.get("top_trigrams", [])[:5]:
            report.append(f"- {phrase} ({count})")

        report.append("")

        docs = stats.get("documents_by_size", [])

        if docs:
            report.append("### Largest Documents\n")

            for doc in docs[:5]:
                report.append(
                    f"- {doc['file']} ({doc['words']} words)"
                )

            report.append("")

    report.append("---\n")

    report.append("## Project Outputs\n")

    report.append("- sources.md")
    report.append("- analysis.json")
    report.append("- analysis.md")
    report.append("- youtube-transcripts/")
    report.append("- linkedin-posts/")
    report.append("- report.md\n")

    report.append("## Conclusion\n")

    report.append(
        "The research pipeline successfully organized expert content, "
        "downloaded transcripts where available, generated structured "
        "research assets, and produced quantitative analysis for future "
        "knowledge extraction and AI-assisted research."
    )

    REPORT.write_text(
        "\n".join(report),
        encoding="utf-8",
    )

    print(f"Saved: {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()