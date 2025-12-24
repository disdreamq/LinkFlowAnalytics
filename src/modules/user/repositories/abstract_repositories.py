from abc import abstractmethod
from typing import TypeVar

from src.core.abstract_repositories.db_repository import ICRUDRepository

T = TypeVar("T")

class IORMUserRepository[T](ICRUDRepository):
    """
    Abstract ORM user repository for ORMs with eager load like SQLAlchemy.

    Raises exception if link not found, return user model with relationship if needed.
    """

    @abstractmethod
    async def get_by_email(self, email: str) -> T:
        raise NotImplementedError

    @abstractmethod
    async def get_with_links(self, user_id: int) -> T:
        raise NotImplementedError

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        raise NotImplementedError
