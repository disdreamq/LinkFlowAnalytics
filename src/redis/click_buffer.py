from fastapi import Depends
from typing import Annotated
from src.core.exception_factory import exception_factory
from src.modules.click.dependencies import get_click_repository
from src.modules.click.schemas import SClickResponse
from src.modules.link.dependencies import get_link_repository
from src.modules.link.repository import LinkRepository
from src.redis.repository import redis

from src.modules.click.repository import ClickRepository
from src.redis.service import get_increments_for_links


class ClickBuffer:
    def __init__(
        self,
        max_lenght: int,
        click_repo: Annotated[ClickRepository, Depends(get_click_repository)],
        link_repo: Annotated[LinkRepository, Depends(get_link_repository)],
    ):
        self.redis = redis
        self.max_lenght = max_lenght
        self.click_repo = click_repo
        self.link_repo = link_repo
        self.counter = 0

    async def add_click(self, click: SClickResponse):
        res = await self.redis.add_to_arr("buffered_clicks", click.model_dump_json())

        if res == 0:
            raise exception_factory.business_error(
                message="Error while addint click to redis buffer",
                detail=f"Can not add click {click} to redis buffer. repo returned 0",
            )
            
        self.counter += 1
        
        if self.counter == 10:
            await self.write_buffer_to_bd()

    async def write_buffer_to_bd(self):
        data = await self.redis.get_arr("buffered_clicks")
        clicks = [SClickResponse.model_validate_json(click) for click in data]
        clicks_dict = get_increments_for_links(clicks)
        await self.link_repo.increment_click_counter(clicks_dict)
