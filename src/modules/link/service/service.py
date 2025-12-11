from typing import Literal

from src.modules.link.repository import LinkRepository
from src.modules.link.schemas.schemas import (
    SLinkCreateDTO,
    SLinkResponse,
    SLinkUpdate,
    SLinkWithClicksResponse,
)
from src.modules.link.service.url_generator import url_generator
from src.redis.repository import redis


class LinkService:
    def __init__(self, repo: LinkRepository):
        self.repo = repo
        self.redis = redis

    async def create_link(self, link_to_create: SLinkCreateDTO) -> SLinkResponse:
        short_url = await url_generator.get_url()
        new_link = await self.repo.create_link(
            **link_to_create.model_dump(), short_url=short_url
        )
        return SLinkResponse.model_validate(new_link)

    async def get_link(self, url: str) -> SLinkResponse:
        if await self.redis.exists(f"link_url_{url}"):
            link_from_redis = await self.redis.get(f"link_url_{url}")
            if not link_from_redis:
                raise
            link = SLinkResponse.model_validate_json(link_from_redis)
        else:
            link_in_db = await self.repo.get_link_by_url(url)
            link = SLinkResponse.model_validate(link_in_db)
            await self.redis.set_(f"link_url_{url}", link.model_dump_json())
        return link

    async def get_link_with_clicks(self, link_url: str) -> SLinkWithClicksResponse:
        link_wtih_clicks = await self.repo.get_link_with_clicks(link_url)
        return SLinkWithClicksResponse.model_validate(link_wtih_clicks)

    async def increment_click_counters(
        self, links_data: dict[str, int]
    ) -> list[SLinkResponse]:
        links_with_incemented_click_counter = await self.repo.increment_click_counters(
            links_data
        )
        return [
            SLinkResponse.model_validate(link)
            for link in links_with_incemented_click_counter
        ]

    async def update_user(self, link_to_update: SLinkUpdate) -> SLinkResponse:
        link_url = link_to_update.url
        link_data = link_to_update.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )
        updated_user = await self.repo.update_link(link_url, link_data)
        return SLinkResponse.model_validate(updated_user)

    async def delete_user(self, user_id) -> Literal[True]:
        return await self.repo.delete_link(user_id)
