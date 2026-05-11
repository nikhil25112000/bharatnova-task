import logging
import uuid
from pathlib import Path
from urllib.parse import quote

from app.core.config import get_settings
from app.schemas.upload_schema import PresignedUrlRequest, PresignedUrlResponse

logger = logging.getLogger(__name__)


class UploadService:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def generate_presigned_url(self, payload: PresignedUrlRequest) -> PresignedUrlResponse:
        extension = Path(payload.filename).suffix.lower()
        object_key = f"uploads/{uuid.uuid4()}{extension}"
        base_url = self.settings.upload_base_url.rstrip("/")
        upload_url = f"{base_url}/{quote(object_key)}?content_type={quote(payload.content_type)}"
        file_url = f"{base_url}/{quote(object_key)}"
        logger.info("Generated local upload metadata for key=%s", object_key)

        return PresignedUrlResponse(
            upload_url=upload_url,
            file_url=file_url,
            expires_in=self.settings.upload_url_expiry_seconds,
        )
