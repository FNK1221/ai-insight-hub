#!/usr/bin/env python3
"""
Cache AI tools from GitHub to data/ai-tools.json.
Uses GitHub Search API to find popular AI-related repositories.
"""
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone


# 注意：GitHub Search API 不支持 "topic:a OR topic:b"（OR 不能作用于限定符，会返回 422），
# 因此这里分 topic 逐个查询后合并去重
TOPIC_QUERIES = ["topic:ai-tool", "topic:llm-tool", "topic:ai-agent"]
API_TMPL = (
    "https://api.github.com/search/repositories?"
    "q={q}&sort=stars&order=desc&per_page=10"
)

# 认证 token：优先 GITHUB_PAT，其次 Actions 自带的 GITHUB_TOKEN
# 无认证时 Actions 共享 IP 调搜索 API 几乎必然 403 限流
TOKEN = os.environ.get("GITHUB_PAT") or os.environ.get("GITHUB_TOKEN") or ""


def http_get_json(url, headers):
    """GET a URL with retry, return parsed JSON."""
    last_err = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            last_err = e
            wait = 10 * (attempt + 1)
            print(f"Attempt {attempt + 1} failed: {e}, retrying in {wait}s...")
            time.sleep(wait)
    raise last_err


def fetch_tools():
    """Fetch AI tools from GitHub Search API (per-topic queries, merged & deduped)."""
    print("Fetching AI tools from GitHub API...")
    headers = {
        "User-Agent": "AI-Insight-Hub-Bot/1.0",
        "Accept": "application/vnd.github.v3+json",
    }
    if TOKEN:
        headers["Authorization"] = f"token {TOKEN}"
    else:
        print("WARN: no GITHUB_TOKEN/GITHUB_PAT set, unauthenticated request may hit rate limit")

    seen = set()
    tools = []
    for q in TOPIC_QUERIES:
        try:
            data = http_get_json(API_TMPL.format(q=q), headers)
        except Exception as e:
            print(f"WARN: query '{q}' failed: {e}")
            continue
        for item in data.get("items", []):
            full_name = item.get("full_name", "")
            if not full_name or full_name in seen:
                continue
            seen.add(full_name)
            tools.append({
                "name": item.get("name", ""),
                "full_name": full_name,
                "description": item.get("description", ""),
                "stars": item.get("stargazers_count", 0),
                "forks": item.get("forks_count", 0),
                "language": item.get("language", ""),
                "pushed_at": item.get("pushed_at", ""),
                "html_url": item.get("html_url", ""),
                "topics": item.get("topics", []),
            })
        time.sleep(3)  # Search API 限速：认证 30 次/分，匿名 10 次/分

    if not tools:
        raise RuntimeError("All topic queries failed, no tools fetched")

    tools.sort(key=lambda t: t["stars"], reverse=True)
    tools = tools[:18]
    print(f"Fetched {len(tools)} AI tools from GitHub")
    return tools


def main():
    output_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "ai-tools.json")

    tools = fetch_tools()

    data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "count": len(tools),
        "tools": tools,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(tools)} tools to {output_path}")


if __name__ == "__main__":
    main()
