from string import ascii_letters, digits

from src.cache.redis.repositories.repository import redis


class URLGenerator:
    """Generating short urls for links.
    self.alphabet are responsible for char pool,
    self.ready is False for first start, will call(async) self.initialize to get
    current state(self.current) from cache, uses generator for generate urls.
    """

    def __init__(self):
        self.redis = redis
        self.alphabet = ascii_letters + digits
        self.current = [0, 0, 0, 0, 0]
        self.ready = False

    def _generate_url(self):
        for i in range(4, 0, -1):
            if self.current[i] == len(self.alphabet) - 1:
                self.current[i] = 0
                self.current[i - 1] += 1
        url: str = "".join([self.alphabet[index] for index in self.current])

        self.current[-1] += 1
        yield url

    async def initialize(self):
        cached_current = await self.redis.get("current")
        if cached_current:
            self.current = [int(elem) for elem in cached_current.split(",")]
        self.current[4] += 1
        self.generator = self._generate_url
        self.ready = True

    async def get_url(self):
        if not self.ready:
            await self.initialize()

        await self.redis.set_("current", ",".join([str(elem) for elem in self.current]))
        return next(self.generator())

    async def del_cache(self):
        return await self.redis.delete("current")


url_generator = URLGenerator()
