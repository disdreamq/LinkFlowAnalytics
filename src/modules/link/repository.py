import logging
from typing import Literal

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, NoResultFound, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.core.exception_factory import exception_factory
from src.modules.link.models import Link

logger = logging.getLogger(__name__)


class LinkRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_link(self, user_id: int, base_url: str, short_url: str) -> Link:
        try:
            link_to_create = Link(user_id=user_id, base_url=base_url, url=short_url)
            self.session.add(link_to_create)
            await self.session.flush()
            return link_to_create

        except IntegrityError as e:
            logger.error(f"Integrity error while adding link: {e}")
            raise exception_factory.business_error(
                "Bad data error",
            ) from None

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding link: {e}")
            raise exception_factory.database_error(user_id) from None

        except Exception as e:
            logger.critical(f"Unexpected error while adding link: {e}")
            raise exception_factory.unexpected_error({"user_id": user_id}) from None

    async def get_link_by_url(self, url: str) -> Link:
        try:
            stmt = select(Link).filter(Link.url == url)
            result = await self.session.execute(stmt)
            return result.scalar_one()

        except NoResultFound:
            logger.warning(f"Link with id {url} does not exists")
            raise exception_factory.not_found(resource="link", identifier=url) from None

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding link: {e}")
            raise exception_factory.database_error(url) from None

        except Exception as e:
            logger.critical(f"Unexpected error while adding link: {e}")
            raise exception_factory.unexpected_error({"link_url": url}) from None

    async def get_link_by_id(self, link_id: int) -> Link:
        try:
            stmt = select(Link).filter(Link.id == link_id)
            result = await self.session.execute(stmt)
            return result.scalar_one()

        except NoResultFound:
            logger.warning(f"Link with id {link_id} does not exists")
            raise exception_factory.not_found(
                resource="link", identifier=link_id
            ) from None

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding link: {e}")
            raise exception_factory.database_error(link_id) from None

        except Exception as e:
            logger.critical(f"Unexpected error while adding link: {e}")
            raise exception_factory.unexpected_error({"link_id": link_id}) from None

    async def get_link_with_user(self, link_id: int) -> Link:
        try:
            stmt = (
                select(Link).filter(Link.id == link_id).options(joinedload(Link.user))
            )
            result = await self.session.execute(stmt)
            return result.scalar_one()

        except NoResultFound:
            logger.warning(f"Link with id {link_id} does not exists")
            raise exception_factory.not_found(
                resource="link", identifier=link_id
            ) from None

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding: {e}")
            raise exception_factory.database_error(link_id) from None

        except Exception as e:
            logger.critical(f"Unexpected error while adding link: {e}")
            raise exception_factory.unexpected_error({"link_id": link_id}) from None

    async def get_link_with_clicks(self, link_url: str) -> Link:
        try:
            stmt = (
                select(Link)
                .where(Link.url == link_url)
                .options(selectinload(Link.clicks))
            )
            result = await self.session.execute(stmt)
            return result.scalar_one()

        except NoResultFound:
            logger.warning(f"Link with id {link_url} does not exists")
            raise exception_factory.not_found(
                resource="link", identifier=link_url
            ) from None

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding link: {e}")
            raise exception_factory.database_error(link_url) from None

        except Exception as e:
            logger.critical(f"Unexpected error while adding link: {e}")
            raise exception_factory.unexpected_error({"link_url": link_url}) from None

    async def get_full_link(self, link_url: str) -> Link:
        try:
            stmt = (
                select(Link)
                .where(Link.url == link_url)
                .options(joinedload(Link.user), selectinload(Link.clicks))
            )
            result = await self.session.execute(stmt)
            return result.unique().scalar_one()

        except NoResultFound:
            logger.warning(f"Link with id {link_url} does not exists")
            raise exception_factory.not_found(
                resource="link", identifier=link_url
            ) from None

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding link: {e}")
            raise exception_factory.database_error(link_url) from None

        except Exception as e:
            logger.critical(f"Unexpected error while adding link: {e}")
            raise exception_factory.unexpected_error({"link_url": link_url}) from None

    async def get_multiple_links_by_urls(self, link_urls: list[str]) -> list[Link]:
        try:
            stmt = select(Link).filter(Link.url.in_(link_urls)).order_by(Link.id)
            result = await self.session.execute(stmt)
            return list(result.scalars().all())

        except NoResultFound:
            logger.warning(f"Link with id {link_urls} does not exists")
            raise exception_factory.not_found(
                resource="links", identifier=link_urls
            ) from None

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding links: {e}")
            raise exception_factory.database_error(link_urls) from None

        except Exception as e:
            logger.critical(f"Unexpected error while adding links: {e}")
            raise exception_factory.unexpected_error({"link_url": link_urls}) from None

    async def update_link(self, link_url: str, link_data: dict[str, str]) -> Link:
        link_to_update = await self.get_link_by_url(link_url)
        try:
            for key, value in link_data.items():
                if hasattr(link_to_update, key) and value:
                    setattr(link_to_update, key, value)

            self.session.add(link_to_update)
            await self.session.flush()
            return link_to_update

        except SQLAlchemyError as e:
            logger.error(f"Database error while updating link: {e}")
            raise exception_factory.database_error(link_to_update) from None

        except Exception as e:
            logger.critical(f"Unexpected error while updating link: {e}")
            raise exception_factory.unexpected_error({"link": link_to_update}) from None

    async def increment_click_counters(self, links_data: dict[str, int]) -> list[Link]:
        links = await self.get_multiple_links_by_urls(list(links_data.keys()))
        try:
            for link in links:
                link.click_counter += links_data[link.url]
                self.session.add(link)
            return links

        except SQLAlchemyError as e:
            logger.error(
                f"Database error while incrementing click_counter for links: {e}"
            )
            raise exception_factory.database_error(links_data) from None

        except Exception as e:
            logger.critical(f"Unexpected error while adding link: {e}")
            raise exception_factory.unexpected_error(
                {"links_data": links_data}
            ) from None

    async def delete_link(self, link_url: str) -> Literal[True]:
        try:
            link_to_delete = await self.get_link_by_url(link_url)
            await self.session.delete(link_to_delete)
            return True

        except SQLAlchemyError as e:
            logger.error(f"Database error while deleting link: {e}")
            raise exception_factory.database_error(link_url) from None

        except Exception as e:
            logger.critical(f"Unexpected error while deleting link: {e}")
            raise exception_factory.unexpected_error({"link_url": link_url}) from None
