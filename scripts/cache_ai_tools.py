#!/usr/bin/env python3
"""
Cache AI tools from GitHub to data/ai-tools.json.
Uses GitHub Search API to find popular AI-related repositories.
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone


GITHUB_API_URL = (
    "https://api.github.com/search/repositories?"
    "q=topic:ai-tool+OR+topic:llm-tool+OR+topic:ai-agent"
    "&sort=stars&order=desc&per_page=15"
)


def fetch_tools():
    """Fetch AI tools from GitHub Search API."""
    print("Fetching AI tools from GitHub API...")
    req = urllib.request.Request(
        GITHUB_API_URL,
        headers={
            "User-Agent": "AI-Insight-Hub-Bot/1.0",
            "Accept": "application/vnd.github.v3+json",
        }
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8")
    data = json.loads(raw)

    tools = []
    for item in data.get("items", []):
        tools.append({
            "name": item.get("name", ""),
            "full_name": item.get("full_name", ""),
            "description": item.get("description", ""),
            "stars": item.get("stargazers_count", 0),
            "forks": item.get("forks_count", 0),
            "language": item.get("language", ""),
            "pushed_at": item.get("pushed_at", ""),
            "html_url": item.get("html_url", ""),
            "topics": item.get("topics", []),
        })

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
