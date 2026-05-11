import json
import logging
from typing import Any

from redis.asyncio import Redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


class CacheService:
    def __init__(self, redis_client: Redis | None) -> None:
        self.redis_client = redis_client

    async def get_json(self, key: str) -> Any | None:
        if not self.redis_client:
            return None
        try:
            payload = await self.redis_client.get(key)
            return json.loads(payload) if payload else None
        except (RedisError, json.JSONDecodeError):
            logger.exception("Redis read failed for key=%s", key)
            return None

    async def set_json(self, key: str, value: Any, ttl_seconds: int) -> None:
        if not self.redis_client:
            return
        try:
            await self.redis_client.set(key, json.dumps(value, default=str), ex=ttl_seconds)
        except RedisError:
            logger.exception("Redis write failed for key=%s", key)
