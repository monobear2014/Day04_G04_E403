from __future__ import annotations

import os
import requests
from typing import Any


def github_search(query: str = "", sort: str = "best match") -> dict[str, Any]:
    """
    Search GitHub repositories for code, release notes, or trending projects related to a research topic.
    """
    try:
        if not query or not isinstance(query, str) or not query.strip():
            return {"error": "Tham số 'query' không được để trống."}

        cleaned_query = query.strip()
        sort_clean = (sort or "best match").strip().lower()

        url = "https://api.github.com/search/repositories"
        params: dict[str, Any] = {
            "q": cleaned_query,
            "per_page": 10,
        }

        if sort_clean in ["stars", "forks", "updated"]:
            params["sort"] = sort_clean
            params["order"] = "desc"

        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AI-Agent-GitHub-Search/1.0",
        }
        token = os.getenv("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"token {token}"

        response = requests.get(url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        res_data = response.json()

        items: list[dict[str, Any]] = []
        for repo in res_data.get("items", []):
            owner_info = repo.get("owner")
            items.append({
                "name": repo.get("name"),
                "full_name": repo.get("full_name"),
                "html_url": repo.get("html_url"),
                "description": repo.get("description"),
                "stargazers_count": repo.get("stargazers_count"),
                "forks_count": repo.get("forks_count"),
                "language": repo.get("language"),
                "updated_at": repo.get("updated_at"),
                "owner": owner_info.get("login") if isinstance(owner_info, dict) else None,
            })

        return {
            "error": None,
            "data": {
                "total_count": res_data.get("total_count", 0),
                "items": items,
            },
        }
    except Exception as exc:
        return {"error": f"github_search failed: {str(exc)}"}
