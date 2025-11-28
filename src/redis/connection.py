import logging
import redis.asyncio as redis
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from src.core.config import get_settings

logger = logging.getLogger(__name__)


class RedisConnectionManager:
    def __init__(self):
        self._pool: Optional[redis.Redis] = None

    async def create_pool(self):
        if self._pool is None:
            self._pool = await redis.from_url(
                get_settings().redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=10,
            )

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[redis.Redis, None]:
        if self._pool is None:
            await self.create_pool()

        try:
            if self._pool is None:
                logger.error("Redis error, pool is None")
                raise RuntimeError("Failed to create Redis connection pool")
            yield self._pool
        except Exception as e:
            print(f"Redis connection error: {e}")
            raise

    async def close_pool(self):
        if self._pool:
            await self._pool.close()
            self._pool = None
