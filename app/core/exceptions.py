from typing import Optional


class BaseAppException(Exception):
    """Базовое исключение приложения"""

    def __init__(self, message: str, detail: Optional[str] = None):
        self.message = message
        self.detail = detail
        super().__init__(self.message)


class DatabaseException(BaseAppException):
    """Базовое исключение для ошибок БД"""

    pass


class NotFoundException(DatabaseException):
    """Объект не найден"""

    pass


class IntegrityException(DatabaseException):
    """Нарушение целостности данных"""

    pass


class ConnectionException(DatabaseException):
    """Ошибка подключения к БД"""

    pass


class BusinessLogicException(BaseAppException):
    """Ошибка бизнес-логики"""

    pass

class AlreadyExistsException(BaseAppException):
    """Пользователь с таким email уже сущестует"""
    
    pass
