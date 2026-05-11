import logging

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import sanitize_search_query
from app.repositories.post_repository import PostRepository

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(self, session: AsyncSession) -> None:
        self.post_repository = PostRepository(session)

    async def search_posts(self, query: str, limit: int = 10):
        cleaned_query = sanitize_search_query(query)
        if not cleaned_query:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Search query cannot be empty")

        try:
            return await self.post_repository.search_posts(cleaned_query, limit)
        except SQLAlchemyError as exc:
            logger.exception("Search query failed")
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable") from exc
