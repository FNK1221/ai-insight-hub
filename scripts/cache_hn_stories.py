#!/usr/bin/env python3
"""
Cache Hacker News stories to data/hn-stories.json.
Uses the HN Algolia API to fetch AI-related top stories.
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone


HN_API_URL = (
    "https://hn.algolia.com/api/v1/search?"
    "query=AI+artificial+intelligence+LLM"
    "&tags=story&hitsPerPage=20&numericFilters=points>50"
)


def fetch_stories():
    """Fetch stories from HN Algolia API."""
    print("Fetching stories from Hacker News Algolia API...")
    req = urllib.request.Request(
        HN_API_URL,
        headers={"User-Agent": "AI-Insight-Hub-Bot/1.0"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8")
    data = json.loads(raw)

    stories = []
    for hit in data.get("hits", []):
        url = hit.get("url", "")
        if not url:
            url = f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"
        domain = ""
        if hit.get("url"):
            try:
                from urllib.parse import urlparse
                parsed = urlparse(hit["url"])
                domain = parsed.hostname.replace("www.", "") if parsed.hostname else ""
            except Exception:
                domain = "news.ycombinator.com"

        stories.append({
            "title": hit.get("title", ""),
            "url": url,
            "domain": domain,
            "points": hit.get("points", 0),
            "comments": hit.get("num_comments", 0),
            "time": hit.get("created_at", ""),
        })

    print(f"Fetched {len(stories)} stories from Hacker News")
    return stories


def main():
    output_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "hn-stories.json")

    stories = fetch_stories()

    data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "count": len(stories),
        "stories": stories,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(stories)} stories to {output_path}")


if __name__ == "__main__":
    main()
