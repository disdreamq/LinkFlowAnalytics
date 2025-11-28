from abc import ABC, abstractmethod
import logging
from typing import Literal, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, NoResultFound
from sqlalchemy.orm import selectinload

from src.core.exceptions_factory import exception_factory
from src.entities.link.models import Link
from src.entities.user.models import User
from src.entities.user.schemas import SUserCreate, SUserUpdate

logger = logging.getLogger(__name__)


class AbstractRepository(ABC):
    @abstractmethod
    async def create_user():
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_id():
        raise NotImplementedError

    @abstractmethod
    async def update_user():
        raise NotImplementedError

    @abstractmethod
    async def delete_user():
        raise NotImplementedError


class UserRepository(AbstractRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user: SUserCreate) -> Optional[User]:
        try:
            if await self.get_user_by_email(user.email) is not None:
                logger.error(
                    f"Unique email error while adding user with email {user.email}"
                )
                raise exception_factory.already_exists(user.email)

            user_to_create = User(**user.model_dump())
            self.session.add(user_to_create)
            await self.session.flush()
            return user_to_create

        except IntegrityError as e:
            logger.error(f"Integrity error while adding user: {e}")
            raise exception_factory.business_error(
                "Bad data error",
            )

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding: {e}")
            raise exception_factory.database_error(user)

        except Exception as e:
            logger.critical(f"Unexpected error while adding: {e}")
            raise exception_factory.unexpected_error({"user": user})

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        try:
            stmt = select(User).filter(User.id == user_id)
            result = await self.session.execute(stmt)
            user = result.scalar_one_or_none()
            return user

        except NoResultFound:
            logger.warning(f"User with id {user_id} does not exists")
            raise exception_factory.not_found(resource="user", identifier=user_id)

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding: {e}")
            raise exception_factory.database_error(user_id)

        except Exception as e:
            logger.critical(f"Unexpected error while adding: {e}")
            raise exception_factory.unexpected_error({"user_id": user_id})

    async def get_user_by_email(self, email: str) -> Optional[User]:
        try:
            stmt = select(User).filter(User.email == email)
            result = await self.session.execute(stmt)
            user = result.scalar_one_or_none()
            return user

        except NoResultFound:
            logger.warning(f"User with email {email} does not exists")
            raise exception_factory.not_found(resource="user", identifier=email)

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding: {e}")
            raise exception_factory.database_error(email)

        except Exception as e:
            logger.critical(f"Unexpected error while adding: {e}")
            raise exception_factory.unexpected_error(email=email)

    async def update_user(
        self, user_to_update: SUserUpdate, user_id: int
    ) -> Literal[True]:
        try:
            user = self.get_user_by_id(user_id)

            for key, value in user_to_update.model_dump(
                exclude_unset=True,
                exclude_none=True,
            ).items():
                if hasattr(user, key):
                    setattr(user, key, value)

            self.session.add(user)
            await self.session.flush()
            return True

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding: {e}")
            raise exception_factory.database_error(user_id)

        except Exception as e:
            logger.critical(f"Unexpected error while adding: {e}")
            raise exception_factory.unexpected_error({"id": user_id})

    async def delete_user(self, user_id: int) -> Literal[True]:
        try:
            user_to_delete = self.get_user_by_id(user_id)

            await self.session.delete(user_to_delete)
            return True

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding: {e}")
            raise exception_factory.database_error(user_id)

        except Exception as e:
            logger.critical(f"Unexpected error while adding: {e}")
            raise exception_factory.unexpected_error({"id": user_id})

    async def get_all_links_by_user_id(self, user_id: int) -> Optional[list[User]]:
        try:
            stmt = (
                select(User)
                .where(User.id == user_id)
                .options(selectinload(Link.clicks))
            )
            result = await self.session.execute(stmt)
            return list(result.scalars().all())

        except NoResultFound:
            logger.warning(f"User with id {user_id} does not exists")
            raise exception_factory.not_found(resource="user", identifier=user_id)

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding: {e}")
            raise exception_factory.database_error(user_id)

        except Exception as e:
            logger.critical(f"Unexpected error while adding: {e}")
            raise exception_factory.unexpected_error({"user_id": user_id})
