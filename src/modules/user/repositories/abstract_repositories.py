from abc import abstractmethod
from typing import TypeVar

from src.core.abstract_repositories.db_repository import ICRUDRepository

T = TypeVar("T")


class IORMUserRepository[T](ICRUDRepository):
    """Intrface for user. Use for ORMs with eager load like SQLAlchemy.

    Raises exception if link not found, return user model with relationship if needed.
    """

    @abstractmethod
    async def get_by_email(self, email: str) -> T:
        raise NotImplementedError

    @abstractmethod
    async def get_with_links(self, user_id: int) -> T:
        """Get user with links due to eager load.

        Args:
            user_id

        Raises:
            NotImplementedError if method not implemented.

        Returns:
            User with links
        """
        raise NotImplementedError

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        raise NotImplementedError
