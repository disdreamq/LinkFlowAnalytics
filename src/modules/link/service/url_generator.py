from string import ascii_letters, digits
from typing import Annotated

from fastapi import Depends

from src.cache.redis.repositories.abstract_repository import IRedisRepository
from src.cache.redis.repositories.repository import get_redis
from src.core.abstract_repositories.key_value_repository import IKeyValueRepository


class URLGenerator:
    """Generating short urls for links.
    self.alphabet are responsible for char pool,
    self.ready is False for first start, will call(async) self.initialize to get
    current state(self.current) from cache, uses generator for generate urls.
    """

    def __init__(self, cache: IKeyValueRepository):
        self.cache = cache
        self.alphabet = ascii_letters + digits
        self.current = [0, 0, 0, 0, 0]
        self.ready = False

    def _generate_url(self):
        for i in range(4, -1, -1):
            if self.current[i] == len(self.alphabet):
                self.current[i] = 0
                self.current[i - 1] += 1

        url: str = "".join([self.alphabet[index] for index in self.current])
        self.current[-1] += 1

        yield url

    async def _initialize(self):
        if cached_current:= await self.cache.get("current"):
            self.current = [int(elem) for elem in cached_current.split(",")]
            self.current[4] += 1
        else:
            self.current = [0, 0, 0, 0, 0]
        self.generator = self._generate_url
        self.ready = True

    async def get_url(self):
        if not self.ready:
            await self._initialize()

        await self.cache.set_("current", ",".join([str(elem) for elem in self.current]))
        return next(self.generator())

    async def del_cache(self):
        await self.cache.delete("current")
        self.ready = False


async def get_url_generator(
    cache: Annotated[IRedisRepository, Depends(get_redis)],
) -> URLGenerator:
    return URLGenerator(cache)
