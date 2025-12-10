import logging
from fastapi import Depends
from typing import Annotated
from src.core.exception_factory import exception_factory
from src.modules.click.dependencies import get_click_repository
from src.modules.click.schemas import SClickCreate
from src.modules.link.dependencies import get_link_repository
from src.modules.link.repository import LinkRepository
from src.redis.repository import redis

from src.modules.click.repository import ClickRepository
from src.redis.service import get_increments_for_links

logger = logging.getLogger(__name__)


class ClickBuffer:
    def __init__(
        self,
        click_repo: Annotated[ClickRepository, Depends(get_click_repository)],
        link_repo: Annotated[LinkRepository, Depends(get_link_repository)],
        max_lenght: int = 10,
    ):
        self.redis = redis
        self.click_repo = click_repo
        self.link_repo = link_repo
        self.max_lenght = max_lenght
        self.counter = 0
        self.ready = False

    async def add_click(self, click: SClickCreate):
        if not self.ready:
            await self.initialize()
        res = await self.redis.add_to_arr("buffered_clicks", click.model_dump_json())

        if res == 0:
            raise exception_factory.business_error(
                message="Error while addint click to redis buffer",
                detail=f"Can not add click {click} to redis buffer. repo returned 0",
            )

        self.counter += 1
        await self.redis.set("buffer_counter", self.counter)
        logger.info(f"added click {click}")

        if self.counter >= 10:
            await self.write_buffer_to_bd()

    async def write_buffer_to_bd(self):
        # Добавляем клики в дб и обновляем ссылки
        data = await self.redis.get_arr("buffered_clicks")
        clicks = [SClickCreate.model_validate_json(click) for click in data]
        clicks_in_db = await self.click_repo.create_clicks(clicks)
        clicks_dict = get_increments_for_links(clicks_in_db)
        await self.link_repo.increment_click_counter(clicks_dict)
        self.counter = 0
        await self.redis.set("buffer_counter", self.counter)
        await self.redis.delete("buffered_clicks")

        logger.info(f"Clicks {clicks} added to database")

    async def initialize(self):
        counter_in_redis = await self.redis.get("buffer_counter")
        self.counter = int(counter_in_redis) if counter_in_redis else 0
        self.ready = True


async def get_buffer(
    click_repo: Annotated[ClickRepository, Depends(get_click_repository)],
    link_repo: Annotated[LinkRepository, Depends(get_link_repository)],
) -> ClickBuffer:
    return ClickBuffer(click_repo, link_repo)
