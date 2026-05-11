import base64
import json
from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, status


def encode_cursor(created_at: datetime, post_id: UUID) -> str:
    payload = {"created_at": created_at.isoformat(), "id": str(post_id)}
    return base64.urlsafe_b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")


def decode_cursor(cursor: str) -> tuple[datetime, UUID]:
    try:
        decoded = base64.urlsafe_b64decode(cursor.encode("utf-8")).decode("utf-8")
        payload = json.loads(decoded)
        return datetime.fromisoformat(payload["created_at"]), UUID(payload["id"])
    except (ValueError, KeyError, json.JSONDecodeError, TypeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid pagination cursor",
        ) from exc
