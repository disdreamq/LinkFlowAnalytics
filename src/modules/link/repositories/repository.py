import logging
from contextlib import asynccontextmanager
from typing import Literal

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.modules.link.models import Link
from src.modules.link.repositories.abstract_repositories import IORMLinkRepository

logger = logging.getLogger(__name__)


class LinkRepository(IORMLinkRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: int, base_url: str, short_url: str) -> Link:
        async with self._handle_db_error(
            operation="Create", user_id=user_id, base_url=base_url, short_url=short_url
        ):
            link_to_create = Link(user_id=user_id, base_url=base_url, url=short_url)
            self.session.add(link_to_create)
            await self.session.flush()
            return link_to_create

    async def get_by_id(self, link_id: int) -> Link:
        async with self._handle_db_error(operation="Get by id", link_id=link_id):
            stmt = select(Link).filter(Link.id == link_id)
            result = await self.session.execute(stmt)
            return result.scalar_one()

    async def get_by_url(self, url: str) -> Link:
        async with self._handle_db_error(operation="Get by url", url=url):
            stmt = select(Link).filter(Link.url == url)
            result = await self.session.execute(stmt)
            return result.scalar_one()

    async def get_with_clicks(self, url: str) -> Link:
        async with self._handle_db_error(operation="Get with clicks", url=url):
            stmt = (
                select(Link).where(Link.url == url).options(selectinload(Link.clicks))
            )
            result = await self.session.execute(stmt)
            return result.scalar_one()

    async def get_multiple_links_by_urls(self, urls: list[str]) -> list[Link]:
        async with self._handle_db_error(
            operation="Get multiple links by urls", urls=urls
        ):
            stmt = select(Link).filter(Link.url.in_(urls)).order_by(Link.id)
            result = await self.session.execute(stmt)
            return list(result.scalars().all())

    async def get_multiple_links_by_ids(self, link_ids: list[int]) -> list[Link]:
        async with self._handle_db_error(
            operation="Get multiple links by ids", link_ids=link_ids
        ):
            stmt = select(Link).filter(Link.id.in_(link_ids)).order_by(Link.id)
            result = await self.session.execute(stmt)
            return list(result.scalars().all())

    async def update(self, url: str, link_data: dict[str, str]) -> Link:
        async with self._handle_db_error(
            operation="Update", url=url, link_data=link_data
        ):
            link_to_update = await self.get_by_url(url)
            for key, value in link_data.items():
                if hasattr(link_to_update, key) and value:
                    setattr(link_to_update, key, value)

        self.session.add(link_to_update)
        await self.session.flush()
        return link_to_update

    async def increment_click_counters(self, links_data: dict[int, int]) -> list[Link]:
        async with self._handle_db_error(
            operation="Increment click counters", links_data=links_data
        ):
            links = await self.get_multiple_links_by_ids(list(links_data.keys()))
            for link in links:
                link.click_counter += links_data[link.id]
                self.session.add(link)
                await self.session.refresh(link, attribute_names=["updated_at"])
            return links

    async def delete(self, url: str) -> Literal[True]:
        async with self._handle_db_error(operation="Delete", url=url):
            link_to_delete = await self.get_by_url(url)
            await self.session.delete(link_to_delete)
            return True

    @asynccontextmanager
    async def _handle_db_error(self, operation: str, **context):
        try:
            yield
        except IntegrityError as e:
            logger.exception(
                f"Integrity error during {operation}",
                extra={**context, "error": str(e)},
            )
            raise

        except SQLAlchemyError as e:
            logger.exception(
                f"Database error during {operation}",
                extra={**context, "error": str(e)},
            )
            raise

        except Exception as e:
            logger.exception(
                f"Unexpected error during {operation}",
                extra={**context, "error": str(e)},
            )
            raise
