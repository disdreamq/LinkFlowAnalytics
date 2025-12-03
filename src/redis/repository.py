from abc import ABC, abstractmethod
import logging
from typing import Any, Optional
from redis import RedisError

from src.redis.connection import RedisConnectionManager

logger = logging.getLogger(__name__)


class AbstractRedisRepository(ABC):
    @abstractmethod
    async def get(self, key: str):
        raise NotImplementedError

    @abstractmethod
    async def set(self, key: str, value: str, expire: Optional[int] = None):
        raise NotImplementedError

    @abstractmethod
    async def delete(self, key: str):
        raise NotImplementedError

    @abstractmethod
    async def exists(self, key: str):
        raise NotImplementedError

    @abstractmethod
    async def add_to_arr(self, key: str, *args: Any):
        raise NotImplementedError


class RedisRepository(AbstractRedisRepository):
    def __init__(self, connection_manager: RedisConnectionManager):
        self.connection_manager = connection_manager

    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        try:
            async with self.connection_manager.get_connection() as conn:
                return await conn.set(key, value, ex=expire)
        except RedisError as e:
            logger.exception(f"Redis set error: {e}")
            return False

    async def get(self, key: str) -> Optional[str]:
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

    async def get_arr(self, key: str) -> list:
        try:
            async with self.connection_manager.get_connection() as conn:
                return await conn.lrange(key, 0, -1)  # type: ignore
        except RedisError as e:
            logger.exception(f"Redis add error: {e}")
            return []


redis = RedisRepository(RedisConnectionManager())
