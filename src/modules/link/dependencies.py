from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.cache.redis.repositories.repository import redis
from src.modules.dependencies import get_session
from src.modules.link.repositories.repository import LinkRepository
from src.modules.link.service.service import LinkService
from src.modules.link.service.url_generator import url_generator


async def get_link_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> LinkService:
    """DI for link service.
    """
    return LinkService(LinkRepository(session), redis, url_generator)
