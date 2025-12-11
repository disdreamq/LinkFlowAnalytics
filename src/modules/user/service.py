import logging
from typing import Literal

from core.exception_factory import exception_factory
from src.core.security import get_password_hash
from src.modules.user.repository import UserRepository
from src.modules.user.schemas.schemas import (
    SUserCreate,
    SUserInDB,
    SUserResponse,
    SUserUpdate,
)

logger = logging.getLogger(__name__)


class UserService:

    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def create_user(self, user_to_create: SUserCreate) -> SUserResponse:
        if await self.repo.get_user_by_email(user_to_create.email):
            logger.error(
                f"Unique email error while adding user with email {user_to_create.email}"
            )
            raise exception_factory.already_exists(user_to_create.email) from None
        user_to_create.password = get_password_hash(user_to_create.password)
        new_user = await self.repo.create_user(**user_to_create.model_dump())

        return SUserResponse.model_validate(new_user)

    async def get_user_by_id(self, user_id: int) -> SUserInDB:
        user = await self.repo.get_user_by_id(user_id)
        return SUserInDB.model_validate(user)

    async def get_user_by_email(self, user_email: str) -> SUserInDB:
        user = await self.repo.get_user_by_email(user_email)
        return SUserInDB.model_validate(user)

    async def update_user(self, user_to_update: SUserUpdate) -> SUserResponse:
        user_id = user_to_update.id
        user_data = user_to_update.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )
        del user_data["id"]
        updated_user = await self.repo.update_user(user_id, user_data)
        return SUserResponse.model_validate(updated_user)

    async def delete_user(self, user_id) -> Literal[True]:
        return await self.repo.delete_user(user_id)

    async def get_user_with_all_links(self, user_id: int) -> SUserResponse:
        user = await self.repo.get_user_with_all_links_by_user_id(user_id)
        return SUserResponse.model_validate(user)
