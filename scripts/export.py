import json
import csv
from pathlib import Path

INPUT = Path("research/ranked_candidates.json")

CSV_OUT = Path("research/top10_experts.csv")
README_OUT = Path("research/README.md")
METHOD_OUT = Path("research/methodology.md")

with open(INPUT, "r", encoding="utf-8") as f:
    experts = json.load(f)

TOP = experts[:10]

# ---------------- CSV ----------------

with open(CSV_OUT, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)

    writer.writerow([
        "Rank",
        "Name",
        "LinkedIn",
        "Score",
        "Keywords",
        "Snippet"
    ])

    for rank, e in enumerate(TOP, start=1):
        writer.writerow([
            rank,
            e.get("name", ""),
            e.get("url", ""),
            e.get("final_score", e.get("score", 0)),
            ", ".join(e.get("matched_keywords", [])),
            e.get("snippet", "")
        ])

# ---------------- README ----------------

with open(README_OUT, "w", encoding="utf-8") as f:

    f.write("# Top 10 Experts\n\n")
    f.write("Topic: AI-powered SEO Content Production for B2B SaaS\n\n")

    for rank, e in enumerate(TOP, start=1):
        f.write(
            f"{rank}. {e.get('name')} "
            f"(Score: {e.get('final_score', e.get('score',0))})\n"
        )

# ---------------- Methodology ----------------

with open(METHOD_OUT, "w", encoding="utf-8") as f:

    f.write("# Methodology\n\n")
    f.write("Discovery: Google + SerpAPI\n")
    f.write("Ranking: AI, SEO, B2B SaaS, Content Marketing, Seniority\n")
    f.write("Final Output: Top 10 ranked experts\n")

print("=" * 50)
print("DONE")
print("Top Experts:", len(TOP))
print(CSV_OUT)
print(README_OUT)
print(METHOD_OUT)
print("=" * 50)