#!/usr/bin/env python3
"""
Cache AI industry RSS news to data/rss-news.json.
Runs on GitHub Actions (server-side), so users in restricted networks
can read the static JSON from the same origin instead of calling
rss2json / feed origins directly from the browser.
"""
import json
import os
from datetime import datetime, timezone

import feedparser

FEEDS = [
    ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/"),
    ("MIT Tech Review", "https://www.technologyreview.com/feed/"),
    ("The Verge AI", "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"),
    ("VentureBeat AI", "https://venturebeat.com/category/ai/feed/"),
]


def entry_time(e):
    for key in ("published_parsed", "updated_parsed"):
        t = e.get(key)
        if t:
            return datetime(*t[:6], tzinfo=timezone.utc)
    return None


def fetch_all():
    items = []
    for source, url in FEEDS:
        try:
            feed = feedparser.parse(url)
            count = 0
            for e in feed.entries[:10]:
                ts = entry_time(e)
                thumb = ""
                media = e.get("media_thumbnail") or e.get("media_content") or []
                if media and isinstance(media, list):
                    thumb = media[0].get("url", "")
                if not thumb:
                    for link in e.get("links", []):
                        if str(link.get("type", "")).startswith("image"):
                            thumb = link.get("href", "")
                            break
                items.append({
                    "title": e.get("title", ""),
                    "link": e.get("link", ""),
                    "pubDate": ts.isoformat() if ts else "",
                    "thumbnail": thumb,
                    "source": source,
                })
                count += 1
            print(f"{source}: {count} items")
        except Exception as err:
            print(f"WARN: {source} failed: {err}")
    items.sort(key=lambda x: x["pubDate"] or "", reverse=True)
    return items[:24]


def main():
    output_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "rss-news.json")

    items = fetch_all()
    if not items:
        print("WARN: no RSS items fetched, keep old file if exists")
        if os.path.exists(output_path):
            return
    data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "count": len(items),
        "items": items,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(items)} RSS items to {output_path}")


if __name__ == "__main__":
    main()
