from __future__ import annotations

from typing import Any
import requests


def hn_search(query: str = "", limit: int = 5) -> dict[str, Any]:
    """
    Search posts and developer / AI discussions on Hacker News via Algolia API.
    """
    try:
        if not query or not isinstance(query, str) or not query.strip():
            return {"error": "Tham số 'query' không được để trống."}

        cleaned_query = query.strip()
        num_limit = max(1, min(int(limit or 5), 50))

        url = "https://hn.algolia.com/api/v1/search"
        params = {
            "query": cleaned_query,
            "hitsPerPage": num_limit,
        }

        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        res_data = response.json()

        hits: list[dict[str, Any]] = []
        for hit in res_data.get("hits", []):
            object_id = hit.get("objectID")
            hits.append({
                "title": hit.get("title") or hit.get("story_title"),
                "url": hit.get("url") or hit.get("story_url"),
                "author": hit.get("author"),
                "points": hit.get("points"),
                "num_comments": hit.get("num_comments"),
                "created_at": hit.get("created_at"),
                "hn_url": f"https://news.ycombinator.com/item?id={object_id}" if object_id else None,
                "story_text": hit.get("story_text"),
            })

        return {
            "error": None,
            "data": {
                "count": len(hits),
                "items": hits,
            },
        }
    except Exception as exc:
        return {"error": f"hn_search failed: {str(exc)}"}
