import logging
from typing import Literal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.exceptions_catcher import (
    exceptions_and_no_result_catcher,
    exceptions_catcher,
)
from src.modules.user.models import User

logger = logging.getLogger(__name__)


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @exceptions_catcher
    async def create_user(self, email: str, password: str) -> User:
        user_to_create = User(email=email, password=password)
        self.session.add(user_to_create)
        await self.session.flush()
        return user_to_create

    @exceptions_and_no_result_catcher
    async def get_user_by_id(self, user_id: int) -> User:
        stmt = select(User).filter(User.id == user_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one()
        return user

    @exceptions_and_no_result_catcher
    async def get_user_by_email(self, email: str) -> User:
        stmt = select(User).filter(User.email == email)
        result = await self.session.execute(stmt)
        user = result.scalar_one()
        return user

    @exceptions_catcher
    async def update_user(self, user_id: int, user_data: dict[str, str]) -> User:
        user = await self.get_user_by_id(user_id)
        for key, value in user_data.items():
            if hasattr(user, key) and value:
                setattr(user, key, value)
        self.session.add(user)
        await self.session.refresh(user, attribute_names=["updated_at"])
        return user

    @exceptions_catcher
    async def delete_user(self, user_id: int) -> Literal[True]:
        user_to_delete = await self.get_user_by_id(user_id)
        await self.session.delete(user_to_delete)
        return True

    @exceptions_and_no_result_catcher
    async def get_user_with_all_links_by_user_id(self, user_id: int) -> User:
        stmt = select(User).where(User.id == user_id).options(selectinload(User.links))
        result = await self.session.execute(stmt)
        user = result.scalar_one()
        return user
