from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.dependencies import get_session
from src.modules.link.repository import LinkRepository


async def get_link_repository(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> LinkRepository:
    return LinkRepository(session)