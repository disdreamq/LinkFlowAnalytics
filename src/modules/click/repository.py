import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.exceptions_catcher import (
    exceptions_and_no_result_catcher,
    exceptions_catcher,
)
from src.modules.click.models import Click
from src.modules.link.models import Link

logger = logging.getLogger(__name__)


class ClickRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @exceptions_catcher
    async def create_clicks(self, clicks: list[Click]) -> list[Click]:
        for click in clicks:
            self.session.add(click)
        await self.session.flush()
        return clicks

    @exceptions_and_no_result_catcher
    async def get_click(self, click_id: int) -> Click:
        stmt = select(Click).where(Click.id == click_id)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    @exceptions_and_no_result_catcher
    async def get_click_with_link(self, click_id: int) -> Click:
        stmt = (
            select(Click).where(Click.id == click_id).options(selectinload(Link.clicks))
        )
        result = await self.session.execute(stmt)
        click = result.scalar_one()
        return click
