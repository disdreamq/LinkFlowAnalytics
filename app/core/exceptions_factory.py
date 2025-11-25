from typing import Any, Optional, Type
from app.core.exceptions import AlreadyExistsException, BaseAppException, DataBaseException, NotFoundException, UnexpectedException, ValidationException, AuthenticationException, BusinessLogicException

class ExceptionFactory:
    """Фабрика исключений"""

    @staticmethod
    def create_exception(
        exception: Type[BaseAppException],
        message: str,
        detail: Optional[str] = '',
        **kwargs: Any,
    ) -> BaseAppException:
        return exception(message=message, detail=detail, **kwargs)
    @staticmethod
    def not_found(resource: str, identifier: Any) -> BaseAppException:
        return ExceptionFactory.create_exception(
            exception=NotFoundException,
            message=f"{resource} not found",
            detail=f"{resource} with id {identifier} was not found"
        )
        
    @staticmethod
    def already_exists(email: str):
        return ExceptionFactory.create_exception(
            exception=AlreadyExistsException,
            message="User with that email already exists",
            detail=f'User with email {email} already exists'
        )

    @staticmethod
    def validation_error(field: str, issue: str) -> BaseAppException:
        return ExceptionFactory.create_exception(
            exception=ValidationException,
            message="Validation error",
            detail=f"Field '{field}': {issue}"
        )

    @staticmethod
    def unauthorized(message: str = "Authentication required") -> BaseAppException:
        return ExceptionFactory.create_exception(
            exception=AuthenticationException,
            message=message,
            detail="Please provide valid authentication credentials"
        )

    @staticmethod
    def business_error(message: str, detail: Optional[str] = None) -> BaseAppException:
        return ExceptionFactory.create_exception(
            exception=BusinessLogicException,
            message=message,
            detail=detail,
        )

    @staticmethod
    def database_error(source: Any) -> BaseAppException:
        return ExceptionFactory.create_exception(
            exception=DataBaseException,
            message='Data base error',
            detail=f'Problems with data base while processing with {source}',
        )
    @staticmethod
    def unexpected_error(*args: Any, **kwargs: Any) -> BaseAppException:
        return ExceptionFactory.create_exception(
            exception=UnexpectedException,
            message='Unexpected exception',
            detail=f'Unexpected error while processing {args}, {kwargs}',
        )

exception_factory = ExceptionFactory()
