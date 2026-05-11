from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import get_redis_client
from app.db.session import get_db_session
from app.services.cache_service import CacheService
from app.services.post_service import PostService
from app.services.search_service import SearchService
from app.services.trending_service import TrendingService
from app.services.upload_service import UploadService
from app.services.user_service import UserService


async def get_session(session: AsyncSession = Depends(get_db_session)) -> AsyncSession:
    return session


def get_cache_service() -> CacheService:
    return CacheService(get_redis_client())


def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    return UserService(session)


def get_post_service(session: AsyncSession = Depends(get_session)) -> PostService:
    return PostService(session)


def get_trending_service(
    session: AsyncSession = Depends(get_session),
) -> TrendingService:
    return TrendingService(session, get_cache_service())


def get_search_service(session: AsyncSession = Depends(get_session)) -> SearchService:
    return SearchService(session)


def get_upload_service() -> UploadService:
    return UploadService()
