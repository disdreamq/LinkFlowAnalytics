import logging

from sqlalchemy.exc import IntegrityError, NoResultFound, SQLAlchemyError

from src.core.exceptions.exceptions import (
    DataBaseException,
    NotFoundException,
    ValidationException,
)

logger = logging.getLogger(__name__)

def handle_service_exceptions(func):
    """Deco for service"""

    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)

        except NoResultFound as e:
            logger.exception(f'No result found error: {e}')
            raise NotFoundException('Not found exception') from e

        except IntegrityError as e:
            logger.exception(f"Business logic violation: {e}")
            raise ValidationException("Data constraint violation") from e

        except SQLAlchemyError as e:
            logger.exception(f"Database error in service: {e}")
            raise DataBaseException("Data base exception") from e

    return wrapper
