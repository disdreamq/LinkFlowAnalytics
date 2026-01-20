import asyncio
from datetime import datetime, timedelta
from typing import Any

from src.cache.local_memory.repositories.abstract_repository import (
    ILocalMemoryRepository,
)


class LocalMemoryRepository(ILocalMemoryRepository):
    def __init__(self, cleanup_interval: int = 60):
        self._storage: dict[str, tuple[Any, timedelta, datetime]] = {}
        self._cleanup_interval = timedelta(0, cleanup_interval)
        self._last_cleanup = datetime.now()
        self._lock = asyncio.Lock()

    async def set_(self, key: str, value: Any, expire: int = 10) -> bool:
        async with self._lock:
            await self._cleanup_expired()
            self._storage[key] = (value, timedelta(0, expire), datetime.now())
            return True
        return False

    async def get(self, key: str) -> str | None:
        async with self._lock:
            await self._cleanup_expired()
            return str(self._storage.get(key, None))

    async def delete(self, key: str) -> int:
        async with self._lock:
            if await self.exists(key):
                del self._storage[key]
                return 1
        return 0

    async def exists(self, key: str) -> bool:
        async with self._lock:
            return bool(self._storage.get(key, None))

    async def add_to_arr(self, key: str, *args_to_add: Any) -> int:
        async with self._lock:
            await self._cleanup_expired()
            data_in_cache = (
                self._storage[key][0].split(",") if await self.exists(key) else []
            )
            data_in_cache.append(*args_to_add)
            self._storage[key] = (
                ",".join(data_in_cache),
                timedelta(1),
                datetime.now(),
            )
            return len(args_to_add)
        return 0

    async def get_arr(self, key: str) -> list[Any]:
        async with self._lock:
            await self._cleanup_expired()
            return self._storage[key][0]
        return []

    async def _cleanup_expired(self) -> None:
        current_time = datetime.now()
        if current_time - self._last_cleanup < self._cleanup_interval:
            return

        for key, (_, expire_time, created_at) in self._storage.items():
            if current_time - created_at > expire_time:
                del self._storage[key]

        self._last_cleanup = datetime.now()

in_memory_cache = LocalMemoryRepository()