from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.click.repository import ClickRepository
from src.modules.click.service.service import ClickService
from src.modules.dependencies import get_session


async def get_click_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ClickService:
    return ClickService(ClickRepository(session))
