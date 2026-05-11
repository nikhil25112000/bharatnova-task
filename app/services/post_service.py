import logging
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.repositories.post_repository import PostRepository
from app.repositories.user_repository import UserRepository
from app.schemas.post_schema import PostCreate
from app.utils.hashtag_parser import extract_hashtags
from app.utils.pagination import decode_cursor, encode_cursor

logger = logging.getLogger(__name__)


class PostService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.post_repository = PostRepository(session)
        self.user_repository = UserRepository(session)
        self.settings = get_settings()

    async def create_post(self, payload: PostCreate):
        caption = payload.caption.strip()
        if not caption:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Caption cannot be empty")

        try:
            user = await self.user_repository.get_by_id(payload.user_id)
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

            hashtags = extract_hashtags(caption)
            post = await self.post_repository.create(
                user_id=payload.user_id,
                caption=caption,
                media_url=str(payload.media_url),
                bitrate_status=payload.bitrate_status.value,
                hashtags=hashtags,
            )
            await self.session.commit()
            return post
        except HTTPException:
            raise
        except SQLAlchemyError as exc:
            await self.session.rollback()
            logger.exception("Post creation failed")
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable") from exc

    async def get_post(self, post_id: UUID):
        try:
            post = await self.post_repository.get_by_id(post_id)
        except SQLAlchemyError as exc:
            logger.exception("Post lookup failed")
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable") from exc
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
        return post

    async def delete_post(self, post_id: UUID) -> None:
        try:
            post = await self.post_repository.get_by_id(post_id)
            if not post:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
            await self.post_repository.delete(post)
            await self.session.commit()
        except HTTPException:
            raise
        except SQLAlchemyError as exc:
            await self.session.rollback()
            logger.exception("Post deletion failed")
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable") from exc

    async def list_posts(self, *, cursor: str | None, limit: int) -> dict[str, object]:
        if limit < 1 or limit > self.settings.max_page_limit:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Limit must be between 1 and {self.settings.max_page_limit}",
            )

        cursor_created_at = None
        cursor_post_id = None
        if cursor:
            cursor_created_at, cursor_post_id = decode_cursor(cursor)

        try:
            posts = await self.post_repository.list_posts(
                limit=limit,
                cursor_created_at=cursor_created_at,
                cursor_post_id=cursor_post_id,
            )
        except SQLAlchemyError as exc:
            logger.exception("Post listing failed")
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable") from exc

        next_cursor = None
        if len(posts) > limit:
            last_post = posts[limit - 1]
            next_cursor = encode_cursor(last_post.created_at, last_post.id)
            posts = posts[:limit]

        return {"items": posts, "next_cursor": next_cursor}
