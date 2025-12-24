import logging
from contextlib import asynccontextmanager
from typing import Literal

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.modules.user.models import User
from src.modules.user.repositories.abstract_repositories import IORMUserRepository

logger = logging.getLogger(__name__)


class SQLAlchemyUserRepository(IORMUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, email: str, password: str) -> User:
        async with self._handle_db_error(
            operation="Create", email=email, password=password
        ):
            user_to_create = User(email=email, password=password)
            self.session.add(user_to_create)
            await self.session.flush()
            return user_to_create

    async def get_by_id(self, user_id: int) -> User:
        async with self._handle_db_error(operation="Get by id", user_id=user_id):
            stmt = select(User).filter(User.id == user_id)
            result = await self.session.execute(stmt)
            user = result.scalar_one()
            return user

    async def get_by_email(self, email: str) -> User:
        async with self._handle_db_error(operation="Get be email", email=email):
            stmt = select(User).filter(User.email == email)
            result = await self.session.execute(stmt)
            user = result.scalar_one()
            return user

    async def update(self, user_data: dict[str, str]) -> User:
        async with self._handle_db_error(operation="Update", user_data=user_data):
            user = await self.get_by_id(int(user_data["id"]))
            for key, value in user_data.items():
                if hasattr(user, key) and value and key != "id":
                    setattr(user, key, value)
            self.session.add(user)
            await self.session.refresh(user, attribute_names=["updated_at"])
            return user

    async def delete(self, user_id: int) -> Literal[True]:
        async with self._handle_db_error(operation="Delete", user_id=user_id):
            user_to_delete = await self.get_by_id(user_id)
            await self.session.delete(user_to_delete)
            return True

    async def get_with_links(self, user_id: int) -> User:
        async with self._handle_db_error(operation="Get with links", user_id=user_id):
            stmt = (
                select(User).where(User.id == user_id).options(selectinload(User.links))
            )
            result = await self.session.execute(stmt)
            user = result.scalar_one()
            return user

    async def exists_by_email(self, email: str) -> bool:
        async with self._handle_db_error(operation="Exists by email", email=email):
            stmt = select(User).filter(User.email == email)
            result = await self.session.execute(stmt)
            user = result.scalar_one_or_none()
            return not user

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
