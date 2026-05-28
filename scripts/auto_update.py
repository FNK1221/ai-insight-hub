#!/usr/bin/env python3
"""
AI Insight Hub - 自动更新脚本
每周从国际权威信源抓取最新 AI 资讯，更新 index.html 内容

数据源：
1. GitHub Trending API - 热门 AI 项目
2. Hugging Face Blog - 最新模型动态
3. arXiv - 前沿论文
4. IMF/OECD 公开数据 - 宏观经济
"""

import re
import json
import requests
from datetime import datetime
from html.parser import HTMLParser

# ====== 配置 ======
INDEX_FILE = "index.html"
CURRENT_DATE = datetime.now().strftime("%Y年%-m月%d日")
CURRENT_DATE_EN = datetime.now().strftime("%B %d, %Y")

# 语言颜色映射（GitHub 风格）
LANG_COLORS = {
    "Python": "#3572A5", "JavaScript": "#f1e05a", "TypeScript": "#3178c6",
    "Rust": "#dea584", "C++": "#f34b7d", "Go": "#00ADD8", "Java": "#b07219",
    "Jupyter Notebook": "#DA5B0B", "Shell": "#89e051", "Swift": "#F05138",
}

def fetch_github_trending_ai():
    """从 GitHub Search API 获取热门 AI 项目"""
    try:
        repos = []
        # 获取多个类别
        queries = [
            "topic:llm+topic:ai",
            "topic:ai-agent",
            "topic:diffusion-model",
        ]
        seen = set()
        for q in queries:
            url = f"https://api.github.com/search/repositories?q={q}&sort=stars&order=desc&per_page=5"
            headers = {"Accept": "application/vnd.github.v3+json"}
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                for repo in data.get("items", []):
                    full_name = repo["full_name"]
                    if full_name not in seen:
                        seen.add(full_name)
                        repos.append({
                            "name": repo["name"],
                            "full_name": full_name,
                            "url": repo["html_url"],
                            "desc": repo.get("description", "") or "暂无描述",
                            "stars": repo["stargazers_count"],
                            "forks": repo["forks_count"],
                            "lang": repo.get("language", "—"),
                            "topics": repo.get("topics", [])[:3],
                            "updated": repo["pushed_at"][:10],
                        })
        # 按 star 排序取前 15
        repos.sort(key=lambda x: x["stars"], reverse=True)
        return repos[:15]
    except Exception as e:
        print(f"GitHub API error: {e}")
        return []

def fetch_arxiv_ai_highlights():
    """从 arXiv 获取最新 AI 论文标题"""
    try:
        url = "http://export.arxiv.org/api/query?search_query=cat:cs.AI+OR+cat:cs.LG&start=0&max_results=5&sortBy=submittedDate&sortOrder=descending"
        resp = requests.get(url, timeout=15)
        titles = []
        # 简单正则提取标题
        for match in re.finditer(r'<title>(.*?)</title>', resp.text, re.DOTALL):
            title = match.group(1).strip()
            if not title.startswith("ArXiv") and not title.startswith("arXiv"):
                titles.append(title[:80])
        return titles[:5]
    except Exception as e:
        print(f"arXiv error: {e}")
        return []

def fetch_hf_trending():
    """从 Hugging Face 获取趋势模型"""
    try:
        url = "https://huggingface.co/api/trending"
        headers = {"Accept": "application/json"}
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            models = []
            for item in data.get("recentlyTrending", [])[:5]:
                if item.get("type") == "model":
                    models.append({
                        "id": item["id"],
                        "likes": item.get("likes", 0),
                    })
            return models
        return []
    except Exception as e:
        print(f"HF API error: {e}")
        return []

def generate_update_block(repos, papers, models):
    """生成更新内容 HTML 块"""
    html_parts = []

    if repos:
        repo_items = []
        for r in repos[:8]:
            topics_html = " · ".join([f"#{t}" for t in r["topics"]])
            stars_str = f"{r['stars']//1000}k" if r["stars"] >= 1000 else str(r["stars"])
            repo_items.append(
                f'<div style="margin-bottom:10px;"><a href="{r["url"]}" target="_blank" '
                f'style="color:#06b6d4;text-decoration:none;font-weight:600;">{r["full_name"]}</a> '
                f'<span style="color:#f59e0b;">★{stars_str}</span> '
                f'<span style="color:#94a3b8;font-size:12px;">{r["lang"]}</span> '
                f'<span style="color:#64748b;font-size:12px;">{topics_html}</span>'
                f'<div style="color:#94a3b8;font-size:13px;margin-top:2px;">{r["desc"][:100]}</div></div>'
            )
        html_parts.append(
            '<div class="card" data-keywords="GitHub 热门项目 趋势 trending 仓库 开源">\n'
            '  <div class="card-header">\n'
            '    <span class="card-badge badge-purple">热门</span>\n'
            '    <div class="card-title">🔥 本周 GitHub 热门 AI 项目</div>\n'
            '  </div>\n'
            '  <div class="card-preview">基于 GitHub Search API 实时拉取，按 Star 数排序的最新热门项目。</div>\n'
            '  <div class="card-detail">\n'
            + "".join(repo_items) +
            f'    <div class="source-tag">🌐 来源：GitHub Search API | 更新于 {CURRENT_DATE}</div>\n'
            '  </div>\n'
            '  <button class="card-toggle"><span class="arrow">&#9660;</span> 展开详情</button>\n'
            '</div>\n'
        )

    if papers:
        paper_items = []
        for i, title in enumerate(papers, 1):
            paper_items.append(f'<div style="margin-bottom:6px;">{i}. {title}</div>')
        html_parts.append(
            '<div class="card" data-keywords="arXiv 论文 最新 前沿 research paper">\n'
            '  <div class="card-header">\n'
            '    <span class="card-badge badge-blue">前沿</span>\n'
            '    <div class="card-title">📄 最新 arXiv AI 论文</div>\n'
            '  </div>\n'
            '  <div class="card-preview">来自 arXiv cs.AI / cs.LG 板块的最新提交论文。</div>\n'
            '  <div class="card-detail">\n'
            + "".join(paper_items) +
            f'    <div class="source-tag">🌐 来源：arXiv API | 更新于 {CURRENT_DATE}</div>\n'
            '  </div>\n'
            '  <button class="card-toggle"><span class="arrow">&#9660;</span> 展开详情</button>\n'
            '</div>\n'
        )

    if models:
        model_items = []
        for m in models:
            model_items.append(
                f'<div style="margin-bottom:6px;"><a href="https://huggingface.co/{m["id"]}" target="_blank" '
                f'style="color:#06b6d4;text-decoration:none;">{m["id"]}</a> '
                f'<span style="color:#f59e0b;">♥{m["likes"]}</span></div>'
            )
        html_parts.append(
            '<div class="card" data-keywords="Hugging Face 趋势模型 HF trending model">\n'
            '  <div class="card-header">\n'
            '    <span class="card-badge badge-cyan">趋势</span>\n'
            '    <div class="card-title">🤗 Hugging Face 趋势模型</div>\n'
            '  </div>\n'
            '  <div class="card-preview">Hugging Face 平台上近期热度上升最快的模型。</div>\n'
            '  <div class="card-detail">\n'
            + "".join(model_items) +
            f'    <div class="source-tag">🌐 来源：Hugging Face API | 更新于 {CURRENT_DATE}</div>\n'
            '  </div>\n'
            '  <button class="card-toggle"><span class="arrow">&#9660;</span> 展开详情</button>\n'
            '</div>\n'
        )

    return html_parts

def update_index_html(repos, papers, models):
    """更新 index.html 中的动态内容"""
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. 更新 Footer 的日期
    content = re.sub(
        r'最近更新：.*?</span>',
        f'最近更新：{CURRENT_DATE}</span>',
        content
    )

    # 2. 在高端前沿模块末尾插入动态更新卡片
    # 找到高端前沿 tab-content 的结束位置
    advanced_tab_end = content.find('</div>\n\n  </div>\n</section>', content.find('id="tab-advanced"'))
    if advanced_tab_end == -1:
        # 备用：在 AI Knowledge section 结尾插入
        advanced_tab_end = content.find('</section>', content.find('id="ai-knowledge"'))

    update_html = generate_update_block(repos, papers, models)
    if update_html:
        # 检查是否已有动态更新标记
        if "<!-- DYNAMIC_UPDATE_START -->" in content:
            # 替换已有内容
            pattern = r'<!-- DYNAMIC_UPDATE_START -->.*?<!-- DYNAMIC_UPDATE_END -->'
            replacement = "<!-- DYNAMIC_UPDATE_START -->\n" + "\n".join(update_html) + "\n<!-- DYNAMIC_UPDATE_END -->"
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        else:
            # 在高端前沿模块的 cards-grid 末尾插入
            insert_point = content.rfind("</div>", 0, content.find('id="global-economy"'))
            if insert_point > 0:
                insert_html = "\n<!-- DYNAMIC_UPDATE_START -->\n" + "\n".join(update_html) + "\n<!-- DYNAMIC_UPDATE_END -->\n"
                content = content[:insert_point] + insert_html + content[insert_point:]

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ 内容已更新 - {CURRENT_DATE}")
    if repos:
        print(f"   GitHub 项目：{len(repos)} 个")
    if papers:
        print(f"   arXiv 论文：{len(papers)} 篇")
    if models:
        print(f"   HF 趋势模型：{len(models)} 个")

def main():
    print(f"🚀 开始自动更新 - {CURRENT_DATE}")

    # 并行获取数据
    repos = fetch_github_trending_ai()
    papers = fetch_arxiv_ai_highlights()
    models = fetch_hf_trending()

    # 更新 HTML
    update_index_html(repos, papers, models)

    print("🎉 自动更新完成！")

if __name__ == "__main__":
    main()
