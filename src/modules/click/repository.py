import logging
from contextlib import asynccontextmanager
from typing import Literal

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.abstract_repositories.db_repository import ICRUDRepository
from src.modules.click.models import Click

logger = logging.getLogger(__name__)


class ClickRepository(ICRUDRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, clicks: list[Click]) -> list[Click]:
        async with self._handle_db_error(operation="Create", clicks=clicks):
            for click in clicks:
                self.session.add(click)
            await self.session.flush()
            return clicks

    async def get_by_id(self, click_id: int) -> Click:
        async with self._handle_db_error(operation="Get by id", click_id=click_id):
            stmt = select(Click).where(Click.id == click_id)
            result = await self.session.execute(stmt)
            return result.scalar_one()

    async def update(self, click_data: dict[str, str]) -> Click:
        async with self._handle_db_error(operation="Update", click_data=click_data):
            click = await self.get_by_id(int(click_data["id"]))
            for key, value in click_data.items():
                if hasattr(click, key) and value and key != "id":
                    setattr(click, key, value)
            self.session.add(click)
            await self.session.refresh(click, attribute_names=["updated_at"])
            return click

    async def delete(self, click_id: int) -> Literal[True]:
        async with self._handle_db_error(operation="Delete", click_id=click_id):
            user_to_delete = await self.get_by_id(click_id)
            await self.session.delete(user_to_delete)
            return True

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
