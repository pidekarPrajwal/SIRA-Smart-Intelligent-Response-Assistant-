"""
tools/web_search.py

Handles ONLY performing a web search and returning concise results.
Uses DuckDuckGo's HTML endpoint so no API key is required for this
minimal first implementation. Never touches the LLM.
"""

from typing import Dict, Any, List

import requests

from config import WEB_SEARCH_MAX_RESULTS

SEARCH_URL = "https://html.duckduckgo.com/html/"


def search_web(query: str) -> Dict[str, Any]:
    """
    Perform a basic web search and return a small structured result set.
    Never raises - callers get a dict either way.
    """
    if not query or not query.strip():
        return {"error": "No search query was provided."}

    try:
        response = requests.post(
            SEARCH_URL,
            data={"q": query},
            headers={"User-Agent": "Mozilla/5.0 (SIRA local assistant)"},
            timeout=10,
        )
    except requests.exceptions.RequestException as exc:
        return {"error": f"Could not reach the search service: {exc}"}

    if response.status_code != 200:
        return {"error": f"Search service returned status {response.status_code}."}

    results = _parse_results(response.text)

    if not results:
        return {"query": query, "results": []}

    return {"query": query, "results": results}


def _parse_results(html: str) -> List[Dict[str, str]]:
    """Very small, dependency-free extraction of result titles/snippets."""
    import re

    results: List[Dict[str, str]] = []

    # DuckDuckGo HTML result titles are in <a class="result__a">TEXT</a>
    titles = re.findall(r'class="result__a"[^>]*>(.*?)</a>', html, re.DOTALL)
    snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)

    def clean(text: str) -> str:
        return re.sub(r"<[^>]+>", "", text).strip()

    for title, snippet in zip(titles, snippets):
        results.append({"title": clean(title), "snippet": clean(snippet)})
        if len(results) >= WEB_SEARCH_MAX_RESULTS:
            break

    return results