from abc import ABC, abstractmethod
import logging
from typing import Literal, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, NoResultFound
from sqlalchemy.orm import selectinload, joinedload

from src.core.exceptions_factory import exception_factory
from src.entities.link.models import Link
from src.entities.link.schemas import SLinkCreate

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

    async def create_link(self, link: SLinkCreate) -> Optional[Link]:
        try:
            link_to_create = Link(**link.model_dump())
            self.session.add(link_to_create)
            await self.session.commit()
            await self.session.refresh(link_to_create)
            return link_to_create

        except IntegrityError as e:
            logger.error(f"Integrity error while adding user: {e}")
            raise exception_factory.business_error(
                "Bad data error",
            )

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding: {e}")
            raise exception_factory.database_error(link)

        except Exception as e:
            logger.critical(f"Unexpected error while adding: {e}")
            raise exception_factory.unexpected_error({"link": link})

    async def get_link_by_id(self, link_id: int) -> Optional[Link]:
        try:
            stmt = select(Link).where(Link.id == link_id)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()

        except NoResultFound:
            logger.warning(f"Link with id {link_id} does not exists")
            raise exception_factory.not_found(resource="link", identifier=link_id)

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding: {e}")
            raise exception_factory.database_error(link_id)

        except Exception as e:
            logger.critical(f"Unexpected error while adding: {e}")
            raise exception_factory.unexpected_error({"link_id": link_id})

    async def get_link_with_user(self, link_id: int) -> Optional[Link]:
        try:
            stmt = select(Link).where(Link.id == link_id).options(joinedload(Link.user))
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()

        except NoResultFound:
            logger.warning(f"Link with id {link_id} does not exists")
            raise exception_factory.not_found(resource="link", identifier=link_id)

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding: {e}")
            raise exception_factory.database_error(link_id)

        except Exception as e:
            logger.critical(f"Unexpected error while adding: {e}")
            raise exception_factory.unexpected_error({"link_id": link_id})

    async def get_link_with_clicks(self, link_id: int) -> Optional[Link]:
        try:
            stmt = (
                select(Link)
                .where(Link.id == link_id)
                .options(selectinload(Link.clicks))
            )
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()

        except NoResultFound:
            logger.warning(f"Link with id {link_id} does not exists")
            raise exception_factory.not_found(resource="link", identifier=link_id)

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding: {e}")
            raise exception_factory.database_error(link_id)

        except Exception as e:
            logger.critical(f"Unexpected error while adding: {e}")
            raise exception_factory.unexpected_error({"link_id": link_id})

    async def get_full_link(self, link_id: int) -> Optional[Link]:
        try:
            stmt = (
                select(Link)
                .where(Link.id == link_id)
                .options(joinedload(Link.user), selectinload(Link.clicks))
            )
            result = await self.session.execute(stmt)
            return result.unique().scalar_one_or_none()

        except NoResultFound:
            logger.warning(f"Link with id {link_id} does not exists")
            raise exception_factory.not_found(resource="link", identifier=link_id)

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding: {e}")
            raise exception_factory.database_error(link_id)

        except Exception as e:
            logger.critical(f"Unexpected error while adding: {e}")
            raise exception_factory.unexpected_error({"link_id": link_id})

    async def delete_link(self, link_id: int) -> Literal[True]:
        try:
            link_to_delete = self.get_link_by_id(link_id)
            await self.session.delete(link_to_delete)
            await self.session.commit()
            return True

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding: {e}")
            raise exception_factory.database_error(link_id)

        except Exception as e:
            logger.critical(f"Unexpected error while adding: {e}")
            raise exception_factory.unexpected_error({"link_id": link_id})
