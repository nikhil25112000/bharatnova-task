import logging

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.config import get_settings

logger = logging.getLogger(__name__)

redis_client: Redis | None = None


async def init_redis() -> Redis | None:
    global redis_client
    settings = get_settings()
    try:
        redis_client = Redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
        await redis_client.ping()
        logger.info("Redis connection established")
    except RedisError:
        logger.exception("Redis initialization failed")
        redis_client = None
    return redis_client


async def close_redis() -> None:
    global redis_client
    if redis_client is not None:
        await redis_client.close()
        redis_client = None


def get_redis_client() -> Redis | None:
    return redis_client
