import logging
from typing import Literal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.core.exceptions_catcher import (
    exceptions_and_no_result_catcher,
    exceptions_catcher,
)
from src.modules.link.models import Link

logger = logging.getLogger(__name__)


class LinkRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @exceptions_catcher
    async def create_link(self, user_id: int, base_url: str, short_url: str) -> Link:
        link_to_create = Link(user_id=user_id, base_url=base_url, url=short_url)
        self.session.add(link_to_create)
        await self.session.flush()
        return link_to_create

    @exceptions_and_no_result_catcher
    async def get_link_by_url(self, url: str) -> Link:
        stmt = select(Link).filter(Link.url == url)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    @exceptions_and_no_result_catcher
    async def get_link_by_id(self, link_id: int) -> Link:
        stmt = select(Link).filter(Link.id == link_id)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    @exceptions_and_no_result_catcher
    async def get_link_with_user(self, link_id: int) -> Link:
        stmt = select(Link).filter(Link.id == link_id).options(joinedload(Link.user))
        result = await self.session.execute(stmt)
        return result.scalar_one()

    @exceptions_and_no_result_catcher
    async def get_link_with_clicks(self, link_url: str) -> Link:
        stmt = (
            select(Link).where(Link.url == link_url).options(selectinload(Link.clicks))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    @exceptions_and_no_result_catcher
    async def get_full_link(self, link_url: str) -> Link:
        stmt = (
            select(Link)
            .where(Link.url == link_url)
            .options(joinedload(Link.user), selectinload(Link.clicks))
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one()

    @exceptions_and_no_result_catcher
    async def get_multiple_links_by_urls(self, link_urls: list[str]) -> list[Link]:
        stmt = select(Link).filter(Link.url.in_(link_urls)).order_by(Link.id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    @exceptions_and_no_result_catcher
    async def get_multiple_links_by_ids(self, link_ids: list[int]) -> list[Link]:
        stmt = select(Link).filter(Link.id.in_(link_ids)).order_by(Link.id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    @exceptions_catcher
    async def update_link(self, link_url: str, link_data: dict[str, str]) -> Link:
        link_to_update = await self.get_link_by_url(link_url)
        for key, value in link_data.items():
            if hasattr(link_to_update, key) and value:
                setattr(link_to_update, key, value)

        self.session.add(link_to_update)
        await self.session.flush()
        return link_to_update

    @exceptions_catcher
    async def increment_click_counters(self, links_data: dict[int, int]) -> list[Link]:
        links = await self.get_multiple_links_by_ids(list(links_data.keys()))
        for link in links:
            link.click_counter += links_data[link.id]
            self.session.add(link)
            await self.session.refresh(link, attribute_names=["updated_at"])
        return links

    @exceptions_catcher
    async def delete_link(self, link_url: str) -> Literal[True]:
        link_to_delete = await self.get_link_by_url(link_url)
        await self.session.delete(link_to_delete)
        return True
