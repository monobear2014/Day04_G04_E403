from __future__ import annotations

from typing import Any
import requests
from huggingface_hub import HfApi


def huggingface_search(query: str = "", search_type: str = "models") -> dict[str, Any]:
    """
    Search Models, Datasets, or Papers on Hugging Face using huggingface_hub Python SDK.
    """
    try:
        if not query or not isinstance(query, str) or not query.strip():
            return {"error": "Tham số 'query' không được để trống."}

        cleaned_query = query.strip()
        st = (search_type or "models").strip().lower()
        if st not in ["models", "datasets", "papers"]:
            return {"error": f"Tham số search_type '{search_type}' không hợp lệ. Phải thuộc ['models', 'datasets', 'papers']."}

        api = HfApi()
        results: list[dict[str, Any]] = []

        if st == "models":
            models = api.list_models(search=cleaned_query, limit=10)
            for m in models:
                results.append({
                    "id": m.id,
                    "author": getattr(m, "author", None),
                    "downloads": getattr(m, "downloads", 0),
                    "likes": getattr(m, "likes", 0),
                    "pipeline_tag": getattr(m, "pipeline_tag", None),
                    "tags": getattr(m, "tags", []),
                    "last_modified": str(getattr(m, "last_modified", "")),
                    "url": f"https://huggingface.co/{m.id}",
                })
        elif st == "datasets":
            datasets = api.list_datasets(search=cleaned_query, limit=10)
            for d in datasets:
                results.append({
                    "id": d.id,
                    "author": getattr(d, "author", None),
                    "downloads": getattr(d, "downloads", 0),
                    "likes": getattr(d, "likes", 0),
                    "tags": getattr(d, "tags", []),
                    "last_modified": str(getattr(d, "last_modified", "")),
                    "url": f"https://huggingface.co/datasets/{d.id}",
                })
        elif st == "papers":
            try:
                papers = api.list_papers(query=cleaned_query, limit=10)
                for p in papers:
                    paper_id = getattr(p, "id", None) or getattr(p, "paper_id", None)
                    results.append({
                        "id": paper_id,
                        "title": getattr(p, "title", None),
                        "summary": getattr(p, "summary", None),
                        "authors": [getattr(a, "name", str(a)) for a in getattr(p, "authors", [])],
                        "published_at": str(getattr(p, "published_at", "")),
                        "url": f"https://huggingface.co/papers/{paper_id}" if paper_id else None,
                    })
            except Exception:
                resp = requests.get("https://huggingface.co/api/daily_papers", timeout=10)
                resp.raise_for_status()
                all_papers = resp.json()
                q_lower = cleaned_query.lower()
                filtered = [
                    p for p in all_papers
                    if q_lower in (p.get("paper", {}).get("title") or "").lower()
                    or q_lower in (p.get("paper", {}).get("summary") or "").lower()
                ]
                for p in filtered[:10]:
                    paper_info = p.get("paper", {})
                    p_id = paper_info.get("id")
                    results.append({
                        "id": p_id,
                        "title": paper_info.get("title"),
                        "summary": paper_info.get("summary"),
                        "authors": [a.get("name") for a in (paper_info.get("authors") or []) if isinstance(a, dict)],
                        "published_at": paper_info.get("publishedAt"),
                        "url": f"https://huggingface.co/papers/{p_id}" if p_id else None,
                    })

        return {
            "error": None,
            "data": {
                "search_type": st,
                "count": len(results),
                "items": results,
            },
        }
    except Exception as exc:
        return {"error": f"huggingface_search failed: {str(exc)}"}
