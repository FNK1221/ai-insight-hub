#!/usr/bin/env python3
"""
Cache GitHub trending AI repos by category to data/github-repos.json.
Uses GitHub PAT for higher rate limits (30 req/min for Search API).
Called by GitHub Actions or manually.
"""
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone

GITHUB_PAT = os.environ.get("GITHUB_PAT") or os.environ.get("GITHUB_TOKEN") or ""

# Category definitions matching the frontend buttons
CATEGORIES = [
    {"id": "topic:ai+topic:llm",                  "label": "LLM 大模型"},
    {"id": "topic:ai+topic:agent",                "label": "AI Agent"},
    {"id": "topic:ai+topic:rag",                  "label": "RAG 检索增强"},
    {"id": "topic:ai+topic:computer-vision",      "label": "计算机视觉"},
    {"id": "topic:ai+topic:reinforcement-learning","label": "强化学习"},
    {"id": "topic:ai+topic:diffusion-model",       "label": "扩散模型"},
    {"id": "topic:ai+topic:mlops",                 "label": "MLOps"},
    {"id": "topic:ai+topic:robotics",              "label": "机器人"},
]

PER_PAGE = 30  # items per category


def build_headers():
    """Build request headers with optional PAT auth."""
    headers = {
        "User-Agent": "AI-Insight-Hub-Bot/1.0",
        "Accept": "application/vnd.github.v3+json",
    }
    if GITHUB_PAT:
        headers["Authorization"] = f"token {GITHUB_PAT}"
    return headers


def fetch_category(query, per_page=PER_PAGE):
    """Fetch repos for a single category query."""
    url = (
        f"https://api.github.com/search/repositories"
        f"?q={query}&sort=stars&order=desc&per_page={per_page}&page=1"
    )
    req = urllib.request.Request(url, headers=build_headers())

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            rate_remaining = resp.headers.get("X-RateLimit-Remaining", "?")
            raw = resp.read().decode("utf-8")
            data = json.loads(raw)
            print(f"  [OK] {query} -> {len(data.get('items', []))} repos (rate-remaining: {rate_remaining})")
            return data.get("items", [])
    except urllib.error.HTTPError as e:
        print(f"  [ERR] {query} -> HTTP {e.code} {e.reason}")
        return []
    except Exception as e:
        print(f"  [ERR] {query} -> {e}")
        return []


def normalize_item(item):
    """Normalize a GitHub API item to our compact format."""
    return {
        "full_name": item.get("full_name", ""),
        "name": item.get("name", ""),
        "html_url": item.get("html_url", ""),
        "description": (item.get("description") or "")[:200],
        "stargazers_count": item.get("stargazers_count", 0),
        "forks_count": item.get("forks_count", 0),
        "language": item.get("language") or "",
        "pushed_at": item.get("pushed_at", ""),
        "topics": item.get("topics", []),
    }


def main():
    output_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "github-repos.json")

    if not GITHUB_PAT:
        print("WARNING: No GITHUB_PAT set. Rate limit is 10 req/min (vs 30 with PAT).")

    print(f"Fetching {len(CATEGORIES)} categories, {PER_PAGE} repos each...")
    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "categories": {},
    }

    # 读取旧数据：某分类本次抓取失败时保留旧条目，避免空分类顶掉可用数据
    old_categories = {}
    if os.path.exists(output_path):
        try:
            with open(output_path, encoding="utf-8") as f:
                old_categories = json.load(f).get("categories", {})
        except Exception:
            pass

    for cat in CATEGORIES:
        items = fetch_category(cat["id"], PER_PAGE)
        normalized = [normalize_item(i) for i in items]
        if not normalized and cat["id"] in old_categories:
            old_items = old_categories[cat["id"]].get("items", [])
            if old_items:
                print(f"  keep old data for {cat['id']} ({len(old_items)} items)")
                normalized = old_items
        result["categories"][cat["id"]] = {
            "label": cat["label"],
            "items": normalized,
        }
        time.sleep(2)  # Be gentle with rate limits

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    total = sum(len(c["items"]) for c in result["categories"].values())
    print(f"\nDone! {total} repos across {len(CATEGORIES)} categories -> {output_path}")


if __name__ == "__main__":
    main()
