from abc import ABC, abstractmethod
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, NoResultFound

from src.entities.click.models import Click
from src.entities.click.schemas import SClickCreate
from src.core.exceptions_factory import exception_factory


logger = logging.getLogger(__name__)


class AbstractRepository(ABC):
    @abstractmethod
    async def create_click():
        raise NotImplementedError

    @abstractmethod
    async def get_click():
        raise NotImplementedError


class ClickRepository(AbstractRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_click(self, click: SClickCreate) -> Click:
        try:
            click_to_create = Click(**click.model_dump())
            self.session.add(click_to_create)
            await self.session.flush()
            return click_to_create

        except IntegrityError as e:
            logger.error(f"Integrity error while adding user: {e}")
            raise exception_factory.business_error(
                "Bad data error",
            )

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding: {e}")
            raise exception_factory.database_error(click)

        except Exception as e:
            logger.critical(f"Unexpected error while adding: {e}")
            raise exception_factory.unexpected_error({"click": click})

    async def get_click(self, click_id: int) -> Click:
        try:
            stmt = select(Click).where(Click.id == click_id)
            result = await self.session.execute(stmt)
            return result.scalar_one()

        except NoResultFound:
            logger.warning(f"Click with id {click_id} does not exists")
            raise exception_factory.not_found(resource="click", identifier=click_id)

        except SQLAlchemyError as e:
            logger.error(f"Database error while adding: {e}")
            raise exception_factory.database_error(click_id)

        except Exception as e:
            logger.critical(f"Unexpected error while adding: {e}")
            raise exception_factory.unexpected_error({"click": click_id})
