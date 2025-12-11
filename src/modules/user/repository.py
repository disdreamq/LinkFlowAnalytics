import logging
from typing import Literal

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, NoResultFound, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.exception_factory import exception_factory
from src.modules.user.models import User

logger = logging.getLogger(__name__)


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, email: str, password: str) -> User:
        try:
            user_to_create = User(email=email, password=password)
            self.session.add(user_to_create)
            await self.session.flush()
            return user_to_create

        except IntegrityError as e:
            logger.error(f"Integrity error while adding user: {e}")
            raise exception_factory.business_error(
                "Bad data error",
            ) from None

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding: {e}")
            raise exception_factory.database_error(email) from None

        except Exception as e:
            logger.critical(f"Unexpected error while adding: {e}")
            raise exception_factory.unexpected_error({"email": email}) from None

    async def get_user_by_id(self, user_id: int) -> User:
        try:
            stmt = select(User).filter(User.id == user_id)
            result = await self.session.execute(stmt)
            user = result.scalar_one()
            return user

        except NoResultFound:
            logger.warning(f"User with id {user_id} does not exists")
            raise exception_factory.not_found(
                resource="user", identifier=user_id
            ) from None

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding: {e}")
            raise exception_factory.database_error(user_id) from None

        except Exception as e:
            logger.critical(f"Unexpected error while adding: {e}")
            raise exception_factory.unexpected_error({"user_id": user_id}) from None

    async def get_user_by_email(self, email: str) -> User | None:
        try:
            stmt = select(User).filter(User.email == email)
            result = await self.session.execute(stmt)
            user = result.scalar_one_or_none()
            if not user:
                return None
            return user

        except NoResultFound:
            logger.warning(f"User with email {email} does not exists")
            raise exception_factory.not_found(
                resource="user", identifier=email
            ) from None

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding: {e}")
            raise exception_factory.database_error(email) from None

        except Exception as e:
            logger.critical(f"Unexpected error while adding: {e}")
            raise exception_factory.unexpected_error(email=email) from None

    async def update_user(self, user_id: int, user_data: dict[str, str]) -> User:
        user = await self.get_user_by_id(user_id)
        try:
            for key, value in user_data.items():
                if hasattr(user, key) and value:
                    setattr(user, key, value)
            self.session.add(user)
            await self.session.refresh(user, attribute_names=["updated_at"])
            return user

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding: {e}")
            raise exception_factory.database_error(user_id) from None

        except Exception as e:
            logger.critical(f"Unexpected error while adding: {e}")
            raise exception_factory.unexpected_error({"id": user_id}) from None

    async def delete_user(self, user_id: int) -> Literal[True]:
        user_to_delete = await self.get_user_by_id(user_id)
        try:

            await self.session.delete(user_to_delete)
            return True

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding: {e}")
            raise exception_factory.database_error(user_id) from None

        except Exception as e:
            logger.critical(f"Unexpected error while adding: {e}")
            raise exception_factory.unexpected_error({"id": user_id}) from None

    async def get_user_with_all_links_by_user_id(
        self, user_id: int
    ) -> User:
        try:
            stmt = (
                select(User).where(User.id == user_id).options(selectinload(User.links))
            )
            result = await self.session.execute(stmt)
            user = result.scalar_one()
            return user

        except NoResultFound:
            logger.warning(f"User with id {user_id} does not exists")
            raise exception_factory.not_found(
                resource="user", identifier=user_id
            ) from None

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding: {e}")
            raise exception_factory.database_error(user_id) from None

        except Exception as e:
            logger.critical(f"Unexpected error while adding: {e}")
            raise exception_factory.unexpected_error({"user_id": user_id}) from None
