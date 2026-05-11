from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.core.constants import BitrateStatus


class PostCreate(BaseModel):
    user_id: UUID
    caption: str = Field(min_length=1, max_length=2200)
    media_url: HttpUrl
    bitrate_status: BitrateStatus = BitrateStatus.PENDING


class PostRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    caption: str
    media_url: HttpUrl
    bitrate_status: BitrateStatus
    hashtags: list[str]
    created_at: datetime


class PostListResponse(BaseModel):
    items: list[PostRead]
    next_cursor: str | None = None
