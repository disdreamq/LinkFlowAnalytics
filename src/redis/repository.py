from abc import ABC, abstractmethod
from typing import Any, Optional
from redis import RedisError

from src.redis.connection import RedisConnectionManager


class AbstractRedisRepository(ABC):
    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        raise NotImplementedError

    @abstractmethod
    async def set(self, key: str, value: str, expire: Optional[int] = None) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, key: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def exists(self, key: str) -> bool:
        raise NotImplementedError


class RedisRepository(AbstractRedisRepository):
    def __init__(self, connection_manager: RedisConnectionManager):
        self.connection_manager = connection_manager

    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        try:
            async with self.connection_manager.get_connection() as conn:
                return await conn.set(key, value, ex=expire)
        except RedisError as e:
            print(f"Redis set error: {e}")
            return False

    async def get(self, key: str) -> Optional[str]:
        try:
            async with self.connection_manager.get_connection() as conn:
                return await conn.get(key)
        except RedisError as e:
            print(f"Redis get error: {e}")
            return None

    async def delete(self, key: str) -> int:
        try:
            async with self.connection_manager.get_connection() as conn:
                return await conn.delete(key)
        except RedisError as e:
            print(f"Redis delete error: {e}")
            return 0

    async def exists(self, key: str) -> bool:
        try:
            async with self.connection_manager.get_connection() as conn:
                return await conn.exists(key) > 0
        except RedisError as e:
            print(f"Redis exists error: {e}")
            return False


redis = RedisRepository(RedisConnectionManager())
