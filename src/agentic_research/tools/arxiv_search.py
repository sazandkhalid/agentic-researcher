from __future__ import annotations
import httpx, datetime, json
from typing import List, Dict

ARXIV_API = "http://export.arxiv.org/api/query"

def search(query: str, max_results: int = 10) -> List[Dict]:
    # basic arXiv Atom API call
    params = {
        "search_query": query.replace(" ", "+"),
        "start": 0,
        "max_results": max_results,
        "sortBy": "lastUpdatedDate",
        "sortOrder": "descending",
    }
    r = httpx.get(ARXIV_API, params=params, timeout=30.0)
    r.raise_for_status()
    # very light parsing via regex to avoid heavy deps; replace with feedparser if preferred
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(r.text, "lxml")
    out = []
    for entry in soup.find_all("entry"):
        title = entry.title.get_text(strip=True)
        summary = entry.summary.get_text(strip=True) if entry.summary else ""
        link = entry.id.get_text(strip=True)
        updated = entry.updated.get_text(strip=True) if entry.updated else ""
        authors = [a.get_text(strip=True) for a in entry.find_all("name")]
        out.append({
            "title": title,
            "abstract": summary,
            "url": link,
            "updated": updated,
            "authors": authors,
        })
    return out

def dump_json(papers: List[Dict]) -> str:
    return json.dumps(papers, ensure_ascii=False)
