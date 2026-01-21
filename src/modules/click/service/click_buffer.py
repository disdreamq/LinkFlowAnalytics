import logging
from typing import Annotated

from fastapi import Depends

from src.cache.redis.repositories.abstract_repository import IRedisRepository
from src.cache.redis.repositories.repository import RedisRepository, get_redis
from src.core.exceptions.exceptions import BusinessLogicException
from src.modules.click.dependencies import get_click_service
from src.modules.click.schemas import SClickCreate, SClickResponse
from src.modules.click.service.service import ClickService
from src.modules.link.dependencies import get_link_service
from src.modules.link.service.service import LinkService

logger = logging.getLogger(__name__)


class ClickBuffer:
    """Buffer for clicks to avoid large amount of requests to db.
    Every redirect adding this click to array in cache, when
    lenght of array >= self.max_lenght adding all clicks from cache to db.
    """
    def __init__(
        self,
        click_service: Annotated[ClickService, Depends(get_click_service)],
        link_service: Annotated[LinkService, Depends(get_link_service)],
        cache: IRedisRepository,
        max_lenght: int = 10,
    ):
        self.cache = cache
        self.click_service = click_service
        self.link_service = link_service
        self.max_lenght = max_lenght
        self.counter = 0
        self.ready = False

    async def add_click(self, click: SClickCreate):
        if not self.ready:
            await self.initialize()
        res = await self.cache.add_to_arr("buffered_clicks", click.model_dump_json())

        if res == 0:
            raise BusinessLogicException(
                message="Error while addint click to redis buffer",
                detail=f"Can not add click {click} to redis buffer. repo returned 0",
            )

        self.counter += 1
        await self.cache.set_("buffer_counter", self.counter)
        logger.info(f"added click {click}")

        if self.counter >= 10:
            await self.write_buffer_to_bd()

    async def write_buffer_to_bd(self):
        """Adding clicks to db and increment click counters for links
        """
        data = await self.cache.get_arr("buffered_clicks")
        clicks = [SClickCreate.model_validate_json(click) for click in data]
        clicks_in_db = await self.click_service.create_clicks(clicks)
        clicks_dict = _get_increments_for_links(clicks_in_db)
        await self.link_service.increment_click_counters(clicks_dict)
        self.counter = 0
        await self.cache.set_("buffer_counter", self.counter)
        await self.cache.delete("buffered_clicks")

        logger.info(f"Clicks {clicks} added to database")

    async def initialize(self):
        counter_in_redis = await self.cache.get("buffer_counter")
        self.counter = int(counter_in_redis) if counter_in_redis else 0
        self.ready = True


def _get_increments_for_links(clicks: list[SClickResponse]) -> dict[int, int]:
    link_ids = {}

    for click in clicks:
        link_ids[click.link_id] = link_ids.get(click.link_id, 0) + 1

    return link_ids


async def get_buffer(
    click_service: Annotated[ClickService, Depends(get_click_service)],
    link_service: Annotated[LinkService, Depends(get_link_service)],
    cache: Annotated[IRedisRepository, Depends(get_redis)],
) -> ClickBuffer:
    return ClickBuffer(click_service, link_service, cache)
