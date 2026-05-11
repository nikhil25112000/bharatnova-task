import logging

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.constants import MAX_TRENDING_RESULTS, TRENDING_CACHE_KEY
from app.repositories.post_repository import PostRepository
from app.schemas.post_schema import PostRead
from app.services.cache_service import CacheService

logger = logging.getLogger(__name__)


class TrendingService:
    def __init__(self, session: AsyncSession, cache_service: CacheService) -> None:
        self.session = session
        self.post_repository = PostRepository(session)
        self.cache_service = cache_service
        self.settings = get_settings()

    async def get_trending_posts(self) -> list[dict]:
        cached_posts = await self.cache_service.get_json(TRENDING_CACHE_KEY)
        if cached_posts:
            return cached_posts

        try:
            posts = await self.post_repository.get_trending_posts(MAX_TRENDING_RESULTS)
        except SQLAlchemyError as exc:
            logger.exception("Trending query failed")
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable") from exc

        serialized = [PostRead.model_validate(post).model_dump(mode="json") for post in posts]
        await self.cache_service.set_json(
            TRENDING_CACHE_KEY,
            serialized,
            self.settings.redis_cache_ttl_seconds,
        )
        return serialized
