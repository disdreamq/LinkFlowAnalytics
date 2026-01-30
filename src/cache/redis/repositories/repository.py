import logging
from typing import Any

from redis import RedisError

from src.cache.redis.connection import RedisConnectionManager
from src.cache.redis.repositories.abstract_repository import IRedisRepository

logger = logging.getLogger(__name__)


class RedisRepository(IRedisRepository):
    def __init__(self, connection_manager: RedisConnectionManager):
        self.connection_manager = connection_manager

    async def set_(self, key: str, value: Any, expire: int = 10) -> bool:
        try:
            async with self.connection_manager.get_connection() as conn:
                return await conn.set(key, value, ex=expire)
        except RedisError as e:
            logger.exception(f"Redis set error: {e}")
            return False

    async def get(self, key: str) -> str | None:
        try:
            async with self.connection_manager.get_connection() as conn:
                return await conn.get(key)
        except RedisError as e:
            logger.exception(f"Redis get error: {e}")
            return None

    async def delete(self, key: str) -> int:
        try:
            async with self.connection_manager.get_connection() as conn:
                return await conn.delete(key)
        except RedisError as e:
            logger.exception(f"Redis delete error: {e}")
            return 0

    async def exists(self, key: str) -> bool:
        try:
            async with self.connection_manager.get_connection() as conn:
                return await conn.exists(key) > 0
        except RedisError as e:
            logger.exception(f"Redis exists error: {e}")
            return False

    async def add_to_arr(self, key: str, *args_to_add: Any) -> int:
        try:
            async with self.connection_manager.get_connection() as conn:
                return await conn.rpush(key, *args_to_add)  # type: ignore
        except RedisError as e:
            logger.exception(f"Redis add error: {e}")
            return 0

    async def get_arr(self, key: str) -> list[Any]:
        try:
            async with self.connection_manager.get_connection() as conn:
                return await conn.lrange(key, 0, -1)  # type: ignore
        except RedisError as e:
            logger.exception(f"Redis add error: {e}")
            return []

    async def flushdb(self):
        try:
            async with self.connection_manager.get_connection() as conn:
                return await conn.flushdb()
        except RedisError as e:
            logger.exception(f"Redis add error: {e}")


async def get_redis() -> RedisRepository:
    return RedisRepository(RedisConnectionManager(0))
