from __future__ import annotations

import re
from typing import Any
from youtube_transcript_api import YouTubeTranscriptApi


def _extract_video_id(url_or_id: str) -> str:
    cleaned = (url_or_id or "").strip()
    if not cleaned:
        return ""
    if re.match(r"^[a-zA-Z0-9_-]{11}$", cleaned):
        return cleaned
    match = re.search(r"(?:v=|\/embed\/|\/v\/|youtu\.be\/|\/shorts\/)([a-zA-Z0-9_-]{11})", cleaned)
    if match:
        return match.group(1)
    return cleaned


def youtube_transcript(video_url_or_id: str = "", languages: list[str] | None = None) -> dict[str, Any]:
    """
    Extract transcript / subtitles from YouTube video using youtube-transcript-api.
    """
    try:
        if not video_url_or_id or not isinstance(video_url_or_id, str) or not video_url_or_id.strip():
            return {"error": "Tham số 'video_url_or_id' không được để trống."}

        video_id = _extract_video_id(video_url_or_id)
        if not video_id:
            return {"error": f"Không thể trích xuất YouTube Video ID từ '{video_url_or_id}'."}

        pref_languages = languages if (languages and isinstance(languages, list)) else ["vi", "en"]

        raw_transcript: list[Any] = []
        if hasattr(YouTubeTranscriptApi, "get_transcript"):
            raw_transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=pref_languages)
        else:
            ytt = YouTubeTranscriptApi()
            raw_transcript = ytt.fetch(video_id, languages=pref_languages)

        snippets: list[dict[str, Any]] = []
        text_parts: list[str] = []

        for item in raw_transcript:
            text = getattr(item, "text", None) if not isinstance(item, dict) else item.get("text")
            start = getattr(item, "start", None) if not isinstance(item, dict) else item.get("start")
            duration = getattr(item, "duration", None) if not isinstance(item, dict) else item.get("duration")

            if text:
                text_parts.append(text.strip())
                snippets.append({
                    "text": text.strip(),
                    "start": start,
                    "duration": duration,
                })

        return {
            "error": None,
            "data": {
                "video_id": video_id,
                "languages": pref_languages,
                "full_text": " ".join(text_parts),
                "transcript": snippets,
            },
        }
    except Exception as exc:
        return {"error": f"youtube_transcript failed: {str(exc)}"}
