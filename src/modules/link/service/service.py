import json
from typing import Literal

from src.core.exception_factory import exception_factory

from src.modules.link.repositories.repository import LinkRepository
from modules.link.schemas import (
    SLinkCreate,
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

    async def create_link(self, link_to_create: SLinkCreate) -> SLinkResponse:
        short_url = await url_generator.get_url()
        new_link = await self.repo.create(
            **link_to_create.model_dump(), short_url=short_url
        )
        return SLinkResponse.model_validate(new_link)

    async def get_link(self, user_id: int, link_url: str) -> SLinkResponse:
        await self._verify_id(user_id, link_url)
        link_in_db = await self.repo.get_by_url(link_url)
        link = SLinkResponse.model_validate(link_in_db)
        await self.redis.set_(f"link_url_{link_url}", link.model_dump_json(), expire=10)
        return link

    async def get_link_with_clicks(
        self, user_id: int, link_url: str
    ) -> SLinkWithClicksResponse:
        await self._verify_id(user_id, link_url)
        link_wtih_clicks = await self.repo.get_with_clicks(link_url)
        return SLinkWithClicksResponse.model_validate(link_wtih_clicks)

    async def update_link(
        self, user_id: int, link_to_update: SLinkUpdate
    ) -> SLinkResponse:
        await self._verify_id(user_id, link_to_update.url)
        link_url = link_to_update.url
        link_data = link_to_update.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )
        updated_user = await self.repo.update(link_url, link_data)
        return SLinkResponse.model_validate(updated_user)

    async def delete_link(self, user_id: int, link_url: str) -> Literal[True]:
        await self._verify_id(user_id, link_url)
        return await self.repo.delete(link_url)

    async def increment_click_counters(
        self, links_data: dict[int, int]
    ) -> list[SLinkResponse]:
        links_with_incemented_click_counter = await self.repo.increment_click_counters(
            links_data
        )
        return [
            SLinkResponse.model_validate(link)
            for link in links_with_incemented_click_counter
        ]

    async def get_link_for_redirect(
        self,
        link_url: str,
    ) -> SLinkResponse:
        if link_in_cache := await self.redis.get(f"link_url_{link_url}"):
            return SLinkResponse.model_validate(json.loads(link_in_cache))
        else:
            link_in_db = await self.repo.get_by_url(link_url)
            link = SLinkResponse.model_validate(link_in_db)
            await self.redis.set_(
                f"link_url_{link_url}", link.model_dump_json(), expire=10
            )
            return link

    async def _verify_id(self, current_user_id: int, link_url: str):
        link = await self.repo.get_by_url(link_url)
        if current_user_id != link.user_id:
            raise exception_factory.not_found("link id", "{link.id}")
