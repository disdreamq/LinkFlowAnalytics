from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.dependencies import get_session
from src.modules.user.repositories.repository import SQLAlchemyUserRepository
from src.modules.user.service import UserService


async def get_user_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserService:
    """DI for user service.
    """
    return UserService(SQLAlchemyUserRepository(session))
