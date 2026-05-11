from enum import StrEnum
from typing import Any


class BitrateStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


TRENDING_HASHTAGS = ("viral", "trending", "fyp")
TRENDING_CACHE_KEY = "feed:trending:top10"
ALLOWED_UPLOAD_EXTENSIONS = {".mp4", ".m3u8"}
MAX_TRENDING_RESULTS = 10


def success_response(message: str, data: Any) -> dict[str, Any]:
    return {"success": True, "message": message, "data": data}


def error_response(message: str) -> dict[str, Any]:
    return {"success": False, "message": message}
