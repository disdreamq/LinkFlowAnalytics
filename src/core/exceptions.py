from typing import Any, Optional

from fastapi import HTTPException, status


class BaseAppException(HTTPException):
    """Базовое исключение для FastApi"""

    def __init__(
        self,
        status_code: int,
        message: str,
        detail: Optional[str] = None,
        headers: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status_code, detail=detail or message, headers=headers
        )
        self.message = message


class NotFoundException(BaseAppException):
    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=message,
            detail=detail,
        )
        
class AlreadyExistsException(BaseAppException):
    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message=message,
            detail=detail,
        )

class ValidationException(BaseAppException):
    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=message,
            detail=detail,
        )


class AuthenticationException(BaseAppException):
    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=message,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class BusinessLogicException(BaseAppException):
    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=message,
            detail=detail,
        )
        
        
class DataBaseException(BaseAppException):
    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=message,
            detail=detail,
        )
        
class UnexpectedException(BaseAppException):
    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=message,
            detail=detail,
        )