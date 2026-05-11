from pathlib import Path

from fastapi import HTTPException, status

from app.core.config import get_settings
from app.core.constants import ALLOWED_UPLOAD_EXTENSIONS
from app.schemas.upload_schema import PresignedUrlRequest


def validate_upload_payload(payload: PresignedUrlRequest) -> None:
    settings = get_settings()
    if not payload.filename.strip():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Filename is required")

    extension = Path(payload.filename).suffix.lower()
    if extension not in ALLOWED_UPLOAD_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported file extension. Allowed: {', '.join(sorted(ALLOWED_UPLOAD_EXTENSIONS))}",
        )

    if payload.file_size > settings.upload_max_file_size_bytes:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="File exceeds 100MB limit")
