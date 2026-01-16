import logging
from typing import Literal

from src.core.exceptions.exceptions import AlreadyExistsException
from src.core.security import get_password_hash
from src.db.deco_for_SQLAlchemy_servicies import handle_service_exceptions
from src.modules.user.repositories.abstract_repositories import IORMUserRepository
from src.modules.user.schemas import (
    SUserCreate,
    SUserInDB,
    SUserResponse,
    SUserUpdate,
    SUserWithLinks,
)

logger = logging.getLogger(__name__)


class UserService:
    """User service. Doing whole business logic, handling exceptions
    with decorator.
    Raises:
        NotFoundException when user not found in db
        ValidationException when handling wrong data
        DataBaseException when cant connect to db.
    """

    def __init__(self, repo: IORMUserRepository):
        self.repo = repo

    @handle_service_exceptions
    async def create(self, user_to_create: SUserCreate) -> SUserResponse:
        if not await self.repo.exists_by_email(user_to_create.email):
            logger.error(
                f"Unique email error while adding user with email {user_to_create.email}"
            )
            raise AlreadyExistsException(user_to_create.email) from None
        user_to_create.password = get_password_hash(user_to_create.password)
        new_user = await self.repo.create(**user_to_create.model_dump())
        logger.info(f"Service created user {user_to_create}")
        return SUserResponse.model_validate(new_user)

    @handle_service_exceptions
    async def get_by_id(self, user_id: int) -> SUserInDB:
        user = await self.repo.get_by_id(user_id)
        logger.info(f"Service returned user with {user_id=}")
        return SUserInDB.model_validate(user)

    @handle_service_exceptions
    async def get_by_email(self, email: str) -> SUserInDB:
        user = await self.repo.get_by_email(email)
        logger.info(f"Service returned user with {email=}")
        return SUserInDB.model_validate(user)

    @handle_service_exceptions
    async def get_with_all_links(self, user_id: int) -> SUserWithLinks:
        """Func for get user with all links  due to eager load.

        Args:
            user_id

        Returns:
            SUserWithLinks
        """
        user = await self.repo.get_with_links(user_id)
        logger.info(f"Service returned user with {user_id=}")
        return SUserWithLinks.model_validate(user)

    @handle_service_exceptions
    async def update(self, user_to_update: SUserUpdate) -> SUserResponse:
        user_data = user_to_update.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )
        updated_user = await self.repo.update(user_data)
        logger.info(f"Service updated user {user_to_update}")
        return SUserResponse.model_validate(updated_user)

    @handle_service_exceptions
    async def delete(self, user_id) -> Literal[True]:
        logger.info(f"Service deleted user with {user_id=}")
        return await self.repo.delete(user_id)
