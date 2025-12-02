from abc import ABC, abstractmethod
import logging
from typing import Literal, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, NoResultFound
from sqlalchemy.orm import selectinload, joinedload

from src.core.exceptions_factory import exception_factory
from src.modules.link.models import Link
from src.modules.link.schemas import SLinkCreate, SLinkResponse
from modules.link.service import url_generator

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

    async def create_link(self, link: SLinkCreate) -> SLinkResponse:
        try:
            short_url = await url_generator.get_url()
            link_dict = link.model_dump()
            link_dict['base_url'] = str(link_dict['base_url'])
            link_to_create = Link(**link_dict, url=short_url)
            
            self.session.add(link_to_create)
            await self.session.flush()
            return SLinkResponse.model_validate(link_to_create)

        except IntegrityError as e:
            logger.error(f"Integrity error while adding link: {e}")
            raise exception_factory.business_error(
                "Bad data error",
            )

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding link: {e}")
            raise exception_factory.database_error(link)

        except Exception as e:
            logger.critical(f"Unexpected error while adding link: {e}")
            raise exception_factory.unexpected_error({"link": link})

    async def get_link_by_base_url(self, base_url: str) -> SLinkResponse:
        try:
            stmt = select(Link).filter(Link.url == base_url)
            result = await self.session.execute(stmt)
            return SLinkResponse.model_validate(result.scalar_one())

        except NoResultFound:
            logger.warning(f"Link with id {base_url} does not exists")
            raise exception_factory.not_found(resource="link", identifier=base_url)

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding link: {e}")
            raise exception_factory.database_error(base_url)

        except Exception as e:
            logger.critical(f"Unexpected error while adding link: {e}")
            raise exception_factory.unexpected_error({"link_url": base_url})

    async def get_link_by_id(self, link_id: int) -> Optional[SLinkResponse]:
        try:
            stmt = select(Link).filter(Link.id == link_id)
            result = await self.session.execute(stmt)
            return SLinkResponse.model_validate(result.scalar_one_or_none())

        except NoResultFound:
            logger.warning(f"Link with id {link_id} does not exists")
            raise exception_factory.not_found(resource="link", identifier=link_id)

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding link: {e}")
            raise exception_factory.database_error(link_id)

        except Exception as e:
            logger.critical(f"Unexpected error while adding link: {e}")
            raise exception_factory.unexpected_error({"link_id": link_id})

    async def get_link_with_user(self, link_id: int) -> SLinkResponse:
        try:
            stmt = (
                select(Link).filter(Link.id == link_id).options(joinedload(Link.user))
            )
            result = await self.session.execute(stmt)
            return SLinkResponse.model_validate(result.scalar_one())

        except NoResultFound:
            logger.warning(f"Link with id {link_id} does not exists")
            raise exception_factory.not_found(resource="link", identifier=link_id)

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding: {e}")
            raise exception_factory.database_error(link_id)

        except Exception as e:
            logger.critical(f"Unexpected error while adding link: {e}")
            raise exception_factory.unexpected_error({"link_id": link_id})

    async def get_link_with_clicks(self, link_id: int) -> SLinkResponse:
        try:
            stmt = (
                select(Link)
                .where(Link.id == link_id)
                .options(selectinload(Link.clicks))
            )
            result = await self.session.execute(stmt)
            return SLinkResponse.model_validate(result.scalar_one())

        except NoResultFound:
            logger.warning(f"Link with id {link_id} does not exists")
            raise exception_factory.not_found(resource="link", identifier=link_id)

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding link: {e}")
            raise exception_factory.database_error(link_id)

        except Exception as e:
            logger.critical(f"Unexpected error while adding link: {e}")
            raise exception_factory.unexpected_error({"link_id": link_id})

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
            raise exception_factory.not_found(resource="link", identifier=link_id)

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding link: {e}")
            raise exception_factory.database_error(link_id)

        except Exception as e:
            logger.critical(f"Unexpected error while adding link: {e}")
            raise exception_factory.unexpected_error({"link_id": link_id})

    async def delete_link(self, link_id: int) -> Literal[True]:
        try:
            link_to_delete = self.get_link_by_id(link_id)
            await self.session.delete(link_to_delete)
            return True

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding link: {e}")
            raise exception_factory.database_error(link_id)

        except Exception as e:
            logger.critical(f"Unexpected error while adding link: {e}")
            raise exception_factory.unexpected_error({"link_id": link_id})
