import logging
from abc import ABC, abstractmethod
from typing import Literal

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, NoResultFound, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.core.exception_factory import exception_factory
from src.modules.link.models import Link
from src.modules.link.schemas.schemas import (
    SLinkCreateInDB,
    SLinkResponse,
    SLinkWithClicks,
)
from src.modules.link.service import url_generator

logger = logging.getLogger(__name__)


class AbstractRepository(ABC):
    @abstractmethod
    async def create_link():
        raise NotImplementedError

    @abstractmethod
    async def get_link_by_id():
        raise NotImplementedError

    @abstractmethod
    async def delete_link():
        raise NotImplementedError


class LinkRepository(AbstractRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_link(self, link: SLinkCreateInDB) -> SLinkResponse:
        try:
            short_url = await url_generator.get_url()
            link_dict = link.model_dump()
            link_dict["base_url"] = str(link_dict["base_url"])
            link_to_create = Link(**link_dict, url=short_url)

            self.session.add(link_to_create)
            await self.session.flush()
            return SLinkResponse.model_validate(link_to_create)

        except IntegrityError as e:
            logger.error(f"Integrity error while adding link: {e}")
            raise exception_factory.business_error(
                "Bad data error",
            ) from None

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding link: {e}")
            raise exception_factory.database_error(link) from None

        except Exception as e:
            logger.critical(f"Unexpected error while adding link: {e}")
            raise exception_factory.unexpected_error({"link": link}) from None

    async def get_link_by_url(self, url: str) -> SLinkResponse:
        try:
            stmt = select(Link).filter(Link.url == url)
            result = await self.session.execute(stmt)
            return SLinkResponse.model_validate(result.scalar_one())

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

    async def get_link_with_user(self, link_id: int) -> SLinkResponse:
        try:
            stmt = (
                select(Link).filter(Link.id == link_id).options(joinedload(Link.user))
            )
            result = await self.session.execute(stmt)
            return SLinkResponse.model_validate(result.scalar_one())

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

    async def get_link_with_clicks(self, link_id: int) -> SLinkWithClicks:
        try:
            stmt = (
                select(Link)
                .where(Link.id == link_id)
                .options(selectinload(Link.clicks))
            )
            result = await self.session.execute(stmt)
            return SLinkWithClicks.model_validate(result.scalar_one())

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

    async def get_full_link(self, link_id: int) -> SLinkResponse:
        try:
            stmt = (
                select(Link)
                .where(Link.id == link_id)
                .options(joinedload(Link.user), selectinload(Link.clicks))
            )
            result = await self.session.execute(stmt)
            return SLinkResponse.model_validate(result.unique().scalar_one())

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

    async def update_link(self, link_to_update: SLinkResponse) -> SLinkResponse:
        try:
            link_from_db = await self.get_link_by_id(link_to_update.id)
            for key, value in link_to_update.model_dump(
                exclude_unset=True,
                exclude_none=True,
            ).items():
                if hasattr(link_from_db, key):
                    setattr(link_from_db, key, value)

            self.session.add(link_from_db)
            await self.session.flush()
            return SLinkResponse.model_validate(link_from_db)

        except SQLAlchemyError as e:
            logger.error(f"Database error while updating link: {e}")
            raise exception_factory.database_error(link_to_update) from None

        except Exception as e:
            logger.critical(f"Unexpected error while updating link: {e}")
            raise exception_factory.unexpected_error({"link": link_to_update}) from None

    async def delete_link(self, link_url: str) -> Literal[True]:
        try:
            link_to_delete_id = (await self.get_link_by_url(link_url)).id
            link_to_delete = await self.get_link_by_id(link_to_delete_id)
            await self.session.delete(link_to_delete)
            return True

        except SQLAlchemyError as e:
            logger.error(f"Database error while deleting link: {e}")
            raise exception_factory.database_error(link_url) from None

        except Exception as e:
            logger.critical(f"Unexpected error while deleting link: {e}")
            raise exception_factory.unexpected_error({"link_url": link_url}) from None

    async def get_multiple_links_by_ids(self, link_ids: list[int]) -> list[Link]:
        try:
            stmt = select(Link).filter(Link.id.in_(link_ids)).order_by(Link.id)
            result = await self.session.execute(stmt)
            return list(result.scalars().all())

        except NoResultFound:
            logger.warning(f"Link with id {link_ids} does not exists")
            raise exception_factory.not_found(
                resource="links", identifier=link_ids
            ) from None

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding links: {e}")
            raise exception_factory.database_error(link_ids) from None

        except Exception as e:
            logger.critical(f"Unexpected error while adding links: {e}")
            raise exception_factory.unexpected_error({"link_id": link_ids}) from None

    async def increment_click_counter(
        self, links_data: dict[int, int]
    ) -> list[SLinkResponse]:
        try:
            links_from_db = await self.get_multiple_links_by_ids(
                list(links_data.keys())
            )

            for link in links_from_db:
                link.click_counter += links_data[link.id]
                self.session.add(link)

            return [SLinkResponse.model_validate(link) for link in links_from_db]

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
