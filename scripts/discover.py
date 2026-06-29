import json
from pathlib import Path

import requests

# ============================================================
# CONFIGURATION
# ============================================================

SERPAPI_KEY = "9d71bb8e32bc7484c73140f930c4a37ee03443c1450e864f5c7e544ea4cd5f75"

QUERIES = [
    '("B2B SaaS" SEO expert) site:linkedin.com/in',
    '("B2B SaaS" content marketing) site:linkedin.com/in',
    '("AI SEO") site:linkedin.com/in',
    '("Technical SEO") SaaS site:linkedin.com/in',
    '(Founder OR Director OR Head OR VP) SEO SaaS site:linkedin.com/in',
    'site:linkedin.com/in Kevin Indig SEO',
    'site:linkedin.com/in Eli Schwartz SEO',
    'site:linkedin.com/in Ross Simmonds content marketing',
    'site:linkedin.com/in Bernard Huang SEO',
    'site:linkedin.com/in Tommy Walker content marketing'
]
OUTPUT = Path("research/candidates.json")
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

# ============================================================
# SEARCH
# ============================================================

all_candidates = {}
search_count = 0

for query in QUERIES:

    print(f"\nSearching: {query}")

    for start in [0, 10]:

        response = requests.get(
            "https://serpapi.com/search.json",
            params={
                "engine": "google",
                "q": query,
                "num": 10,
                "start": start,
                "api_key": SERPAPI_KEY,
            },
            timeout=60,
        )

        response.raise_for_status()

        data = response.json()

        results = data.get("organic_results", [])

        print(f"  Page {start//10+1}: {len(results)} results")

        search_count += len(results)

        for result in results:

            url = result.get("link", "").strip()

            if not url:
                continue

            if url in all_candidates:
                continue

            title = result.get("title", "")
            snippet = result.get("snippet", "")

            score = 0

            lower = (title + " " + snippet).lower()

            if "linkedin.com/in/" in url:
                score += 40

            if "seo" in lower:
                score += 20

            if "ai" in lower:
                score += 15

            if "saas" in lower:
                score += 15

            if "content" in lower:
                score += 10

            all_candidates[url] = {
                "name": title,
                "url": url,
                "snippet": snippet,
                "score": score,
                "verified": False,
            }

# ============================================================
# SORT
# ============================================================

candidates = sorted(
    all_candidates.values(),
    key=lambda x: x["score"],
    reverse=True,
)

# ============================================================
# SAVE
# ============================================================

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(candidates, f, indent=4, ensure_ascii=False)

print("\n====================================")
print(f"Raw Results      : {search_count}")
print(f"Unique Candidates: {len(candidates)}")
print(f"Saved            : {OUTPUT}")
print("====================================")