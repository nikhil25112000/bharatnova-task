import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import BitrateStatus
from app.db.base import Base


class Post(Base):
    __tablename__ = "posts"
    __table_args__ = (
        Index("ix_posts_hashtags_gin", "hashtags", postgresql_using="gin"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    caption: Mapped[str] = mapped_column(Text, nullable=False)
    media_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    bitrate_status: Mapped[str] = mapped_column(
        String(32), nullable=False, default=BitrateStatus.PENDING.value, server_default=BitrateStatus.PENDING.value
    )
    hashtags: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )

    user = relationship("User", back_populates="posts")
