"""
search.py — Web search tool.

Uses DuckDuckGo Instant Answer API (free, no key needed) by default.
If SERPAPI_API_KEY is set, switches to SerpAPI for richer results.
"""

import json
import httpx
from src.tools.base import tool
from config.settings import settings


# ── DuckDuckGo (free) ─────────────────────────────────────────────────────────

def _duckduckgo_search(query: str, max_results: int = 5) -> list[dict]:
    """
    Uses DuckDuckGo Instant Answer API.
    Returns a list of {title, snippet, url} dicts.
    """
    url = "https://api.duckduckgo.com/"
    params = {
        "q": query,
        "format": "json",
        "no_html": "1",
        "skip_disambig": "1",
    }
    try:
        response = httpx.get(url, params=params, timeout=10.0, follow_redirects=True)
        response.raise_for_status()
        data = response.json()
    except Exception as exc:
        return [{"title": "Search error", "snippet": str(exc), "url": ""}]

    results: list[dict] = []

    # Abstract (top summary)
    if data.get("AbstractText"):
        results.append({
            "title": data.get("Heading", query),
            "snippet": data["AbstractText"][:300],
            "url": data.get("AbstractURL", ""),
        })

    # Related topics
    for topic in data.get("RelatedTopics", []):
        if len(results) >= max_results:
            break
        if isinstance(topic, dict) and topic.get("Text"):
            results.append({
                "title": topic.get("Text", "")[:80],
                "snippet": topic.get("Text", "")[:300],
                "url": topic.get("FirstURL", ""),
            })

    if not results:
        results.append({
            "title": "No instant results",
            "snippet": (
                f"DuckDuckGo had no instant answers for '{query}'. "
                "Try rephrasing or use a more specific query."
            ),
            "url": f"https://duckduckgo.com/?q={query.replace(' ', '+')}",
        })

    return results[:max_results]


# ── SerpAPI (optional, richer) ────────────────────────────────────────────────

def _serpapi_search(query: str, max_results: int = 5) -> list[dict]:
    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "api_key": settings.serpapi_api_key,
        "engine": "google",
        "num": max_results,
    }
    try:
        response = httpx.get(url, params=params, timeout=15.0)
        response.raise_for_status()
        data = response.json()
    except Exception as exc:
        return [{"title": "SerpAPI error", "snippet": str(exc), "url": ""}]

    results = []
    for r in data.get("organic_results", [])[:max_results]:
        results.append({
            "title": r.get("title", ""),
            "snippet": r.get("snippet", ""),
            "url": r.get("link", ""),
        })
    return results


# ── Format helper ─────────────────────────────────────────────────────────────

def _format_results(results: list[dict]) -> str:
    if not results:
        return "No search results found."
    lines = []
    for i, r in enumerate(results, 1):
        lines.append(f"{i}. {r['title']}")
        if r.get("snippet"):
            lines.append(f"   {r['snippet']}")
        if r.get("url"):
            lines.append(f"   URL: {r['url']}")
    return "\n".join(lines)


# ── Tool function ─────────────────────────────────────────────────────────────

@tool(
    name="search",
    description=(
        "Searches the web for current information and returns top results. "
        "Use this for factual questions, recent events, people, places, "
        "definitions, or anything that requires up-to-date information. "
        "Returns titles, snippets, and URLs."
    ),
    param_descriptions={
        "query": "The search query string, e.g. 'latest Python version' or 'Eiffel Tower height'"
    },
)
def search(query: str) -> str:
    """Search the web and return formatted results."""
    max_results = 5

    if settings.serpapi_api_key:
        results = _serpapi_search(query, max_results)
    else:
        results = _duckduckgo_search(query, max_results)

    return _format_results(results)