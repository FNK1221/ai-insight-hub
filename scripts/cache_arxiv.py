#!/usr/bin/env python3
"""
Cache arXiv papers to data/arxiv-papers.json.
Fetches latest papers from cs.AI, cs.CL, cs.CV, cs.LG categories.
"""
import json
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone


ARXIV_API_URL = (
    "https://export.arxiv.org/api/query?"
    "search_query=cat:cs.AI+OR+cat:cs.CL+OR+cat:cs.CV+OR+cat:cs.LG"
    "&sortBy=submittedDate&sortOrder=descending&max_results=20"
)


def fetch_papers():
    """Fetch papers from arXiv API and parse the Atom XML feed."""
    print("Fetching papers from arXiv API...")
    req = urllib.request.Request(
        ARXIV_API_URL,
        headers={"User-Agent": "AI-Insight-Hub-Bot/1.0"}
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        xml_text = resp.read().decode("utf-8")

    root = ET.fromstring(xml_text)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    entries = root.findall("atom:entry", ns)

    papers = []
    for entry in entries:
        title = (
            entry.find("atom:title", ns).text or ""
        ).replace("\n", " ").strip()
        authors = []
        for author in entry.findall("atom:author", ns)[:3]:
            name = author.find("atom:name", ns)
            if name is not None and name.text:
                authors.append(name.text.strip())
        author_str = ", ".join(authors)
        if len(entries) > 0 and len(authors) >= 3:
            author_str += " et al."
        summary = (
            entry.find("atom:summary", ns).text or ""
        ).replace("\n", " ").strip()[:200]
        published = entry.find("atom:published", ns).text or ""
        categories = [
            cat.get("term", "")
            for cat in entry.findall("atom:category", ns)
        ]
        link_elem = entry.find("atom:id", ns)
        link = link_elem.text if link_elem is not None else ""

        papers.append({
            "title": title,
            "authors": author_str,
            "summary": summary,
            "published": published,
            "categories": categories,
            "link": link,
        })

    print(f"Fetched {len(papers)} papers from arXiv")
    return papers


def main():
    output_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "arxiv-papers.json")

    papers = fetch_papers()

    data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "count": len(papers),
        "papers": papers,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(papers)} papers to {output_path}")


if __name__ == "__main__":
    main()
