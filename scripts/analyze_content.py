#!/usr/bin/env python3
"""
analyze_content.py

Reads:
    research/youtube-transcripts/**/*.md
    research/linkedin-posts/**/*.md

Produces:
    research/analysis.json
    research/analysis.md

Purpose:
    Build a simple corpus summary for each expert:
      - word count
      - most common keywords
      - longest documents
      - common phrases (2-grams & 3-grams)
      - overall corpus statistics

No external AI APIs required.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

YT_DIR = ROOT / "research" / "youtube-transcripts"
LI_DIR = ROOT / "research" / "linkedin-posts"

OUT_JSON = ROOT / "research" / "analysis.json"
OUT_MD = ROOT / "research" / "analysis.md"

STOPWORDS = {
    "the","and","for","that","this","with","from","have","will","your",
    "you're","their","they","them","about","there","which","would",
    "could","should","what","when","where","while","been","into","than",
    "then","also","just","more","most","very","much","many","some","such",
    "each","every","only","other","because","being","make","made","using",
    "used","over","under","after","before","through","between","within",
    "here","into","onto","our","ours","his","hers","its","it's","you",
    "youre","yourself","my","mine","me","we","us","i","im","is","are",
    "was","were","be","to","of","on","in","at","by","or","an","a","it",
    "if","as","do","did","does","can","may","how","why","who","all",
    "not","no","yes","so","up","out","off","again","still","than"
}


def tokenize(text: str):
    words = re.findall(r"[A-Za-z']+", text.lower())
    return [w for w in words if len(w) > 2 and w not in STOPWORDS]


def ngrams(words, n):
    return [
        " ".join(words[i:i+n])
        for i in range(len(words)-n+1)
    ]


def read_documents(base):
    docs = []

    if not base.exists():
        return docs

    for file in base.rglob("*.md"):
        try:
            docs.append(
                {
                    "path": file,
                    "text": file.read_text(
                        encoding="utf-8",
                        errors="ignore"
                    ),
                }
            )
        except Exception:
            pass

    return docs


def analyze_author(author_dir):
    docs = []

    for file in author_dir.glob("*.md"):
        try:
            docs.append(
                (
                    file.name,
                    file.read_text(
                        encoding="utf-8",
                        errors="ignore"
                    ),
                )
            )
        except Exception:
            pass

    words = []
    lengths = []

    for name, text in docs:
        tokens = tokenize(text)
        words.extend(tokens)
        lengths.append(
            {
                "file": name,
                "words": len(tokens)
            }
        )

    counter = Counter(words)

    bigrams = Counter(ngrams(words,2))
    trigrams = Counter(ngrams(words,3))

    return {
        "documents": len(docs),
        "total_words": len(words),
        "top_keywords": counter.most_common(30),
        "top_bigrams": bigrams.most_common(20),
        "top_trigrams": trigrams.most_common(20),
        "documents_by_size": sorted(
            lengths,
            key=lambda x:x["words"],
            reverse=True
        ),
    }


def analyze_linkedin():
    results = {}

    if not LI_DIR.exists():
        return results

    for file in LI_DIR.glob("*.md"):
        author = file.stem

        text = file.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        words = tokenize(text)

        results[author] = {
            "words": len(words),
            "top_keywords": Counter(words).most_common(20)
        }

    return results


def main():
    output = {
        "youtube": {},
        "linkedin": {},
        "summary": {}
    }

    total_docs = 0
    total_words = 0

    if YT_DIR.exists():
        for author in sorted(YT_DIR.iterdir()):
            if not author.is_dir():
                continue

            result = analyze_author(author)

            output["youtube"][author.name] = result

            total_docs += result["documents"]
            total_words += result["total_words"]

    output["linkedin"] = analyze_linkedin()

    output["summary"] = {
        "youtube_authors": len(output["youtube"]),
        "linkedin_authors": len(output["linkedin"]),
        "youtube_documents": total_docs,
        "youtube_words": total_words,
    }

    OUT_JSON.write_text(
        json.dumps(output, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    lines = [
        "# Content Analysis",
        "",
        f"- YouTube Authors: {output['summary']['youtube_authors']}",
        f"- LinkedIn Authors: {output['summary']['linkedin_authors']}",
        f"- YouTube Documents: {output['summary']['youtube_documents']}",
        f"- Total Words: {output['summary']['youtube_words']}",
        "",
    ]

    for author, data in output["youtube"].items():
        lines.append(f"## {author}")
        lines.append("")
        lines.append(f"Documents: {data['documents']}")
        lines.append(f"Words: {data['total_words']}")
        lines.append("")
        lines.append("### Top Keywords")

        for word, count in data["top_keywords"][:20]:
            lines.append(f"- {word}: {count}")

        lines.append("")
        lines.append("### Top Bigrams")

        for phrase, count in data["top_bigrams"][:10]:
            lines.append(f"- {phrase}: {count}")

        lines.append("")
        lines.append("### Top Trigrams")

        for phrase, count in data["top_trigrams"][:10]:
            lines.append(f"- {phrase}: {count}")

        lines.append("")
        lines.append("---")
        lines.append("")

    OUT_MD.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    print(f"Saved {OUT_JSON}")
    print(f"Saved {OUT_MD}")


if __name__ == "__main__":
    main()