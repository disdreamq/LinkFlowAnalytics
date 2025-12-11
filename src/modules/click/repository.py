import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, NoResultFound, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.exception_factory import exception_factory
from src.modules.click.models import Click
from src.modules.link.models import Link

logger = logging.getLogger(__name__)


class ClickRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_clicks(self, clicks: list[Click]) -> list[Click]:
        try:
            for click in clicks:
                self.session.add(click)
            await self.session.flush()
            return clicks

        except IntegrityError as e:
            logger.error(f"Integrity error while adding user: {e}")
            raise exception_factory.business_error(
                "Bad data error",
            ) from None

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding: {e}")
            raise exception_factory.database_error(click) from None

        except Exception as e:
            logger.critical(f"Unexpected error while adding: {e}")
            raise exception_factory.unexpected_error({"click": click}) from None

    async def get_click(self, click_id: int) -> Click:
        try:
            stmt = select(Click).where(Click.id == click_id)
            result = await self.session.execute(stmt)
            return result.scalar_one()

        except NoResultFound:
            logger.warning(f"Click with id {click_id} does not exists")
            raise exception_factory.not_found(
                resource="click", identifier=click_id
            ) from None

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding: {e}")
            raise exception_factory.database_error(click_id) from None

        except Exception as e:
            logger.critical(f"Unexpected error while adding: {e}")
            raise exception_factory.unexpected_error({"click": click_id}) from None

    async def get_click_with_link(self, click_id: int) -> Click:
        try:
            stmt = (
                select(Click)
                .where(Click.id == click_id)
                .options(selectinload(Link.clicks))
            )
            result = await self.session.execute(stmt)
            click = result.scalar_one()
            return click

        except NoResultFound:
            logger.warning(f"Click with id {click_id} does not exists")
            raise exception_factory.not_found(
                resource="click", identifier=click_id
            ) from None

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding: {e}")
            raise exception_factory.database_error(click_id) from None

        except Exception as e:
            logger.critical(f"Unexpected error while adding: {e}")
            raise exception_factory.unexpected_error({"click": click_id}) from None
