import json
from pathlib import Path

INPUT = Path("research/candidates.json")
OUTPUT = Path("research/ranked_candidates.json")

with open(INPUT, "r", encoding="utf-8") as f:
    candidates = json.load(f)

KEYWORDS = {
    "founder": 40,
    "co-founder": 40,
    "ceo": 35,
    "chief": 35,
    "vp": 30,
    "vice president": 30,
    "head": 28,
    "director": 25,
    "lead": 20,
    "manager": 15,

    "seo": 20,
    "technical seo": 25,
    "ai": 20,
    "artificial intelligence": 20,
    "saas": 20,
    "b2b": 20,
    "content": 15,
    "content marketing": 20,
    "growth": 15,
    "demand generation": 15,
    "organic": 10,
    "search": 10,
    "marketing": 10,
}

for candidate in candidates:

    score = candidate.get("score", 0)

    text = (
        candidate.get("name", "") + " " +
        candidate.get("snippet", "")
    ).lower()

    matched = []

    for keyword, points in KEYWORDS.items():

        if keyword in text:
            score += points
            matched.append(keyword)

    candidate["final_score"] = score
    candidate["matched_keywords"] = matched

ranked = sorted(
    candidates,
    key=lambda x: x["final_score"],
    reverse=True,
)

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(ranked, f, indent=4, ensure_ascii=False)

print("=" * 50)
print(f"Candidates : {len(ranked)}")
print(f"Saved      : {OUTPUT}")
print("=" * 50)

print("\nTop 20\n")

for i, c in enumerate(ranked[:20], start=1):
    print(
        f"{i:02d}. "
        f"{c['final_score']:3d} | "
        f"{c['name']}"
    )