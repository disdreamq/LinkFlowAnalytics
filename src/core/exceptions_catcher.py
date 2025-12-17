import logging
from collections.abc import Callable

from sqlalchemy.exc import IntegrityError, NoResultFound, SQLAlchemyError

from src.core.exception_factory import exception_factory

logger = logging.getLogger(__name__)


def exceptions_catcher(func: Callable) -> Callable:
    async def wrapper(
        identifier,
        *args,
        **kwargs,
    ):
        try:
            result = await func(identifier, *args, **kwargs)
            return result

        except IntegrityError as e:
            logger.exception(f"Integrity error while adding user: {e}")
            raise exception_factory.business_error(
                "Bad data error",
            ) from None

        except SQLAlchemyError as e:
            logger.exception(f"Database error while adding: {e}")
            raise exception_factory.database_error(identifier) from None

        except Exception as e:
            logger.exception(f"Unexpected error while adding: {e}")
            raise exception_factory.unexpected_error({f"{str(identifier)=}"}) from None

    return wrapper


def exceptions_and_no_result_catcher(func: Callable) -> Callable:
    async def wrapper(
        self,
        identifier: int | None = None,
        *args,
        **kwargs,
    ):
        try:
            result = await func(
                self, identifier, *args, **kwargs
            )
            return result

        except NoResultFound:
            logger.warning(f"User with email {identifier} does not exists")
            raise exception_factory.not_found(
                resource="user",
                identifier=identifier
            ) from None

        except IntegrityError as e:
            logger.exception(f"Integrity error while adding user: {e}")
            raise exception_factory.business_error(
                "Bad data error",
            ) from None

        except SQLAlchemyError as e:
            logger.exception(f"Database error while adding: {e}")
            raise exception_factory.database_error(identifier) from None

        except Exception as e:
            logger.exception(f"Unexpected error while adding: {e}")
            raise exception_factory.unexpected_error({f"{str(identifier)=}"}) from None

    return wrapper
