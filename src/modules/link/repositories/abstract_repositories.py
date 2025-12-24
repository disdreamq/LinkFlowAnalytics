from abc import abstractmethod
from typing import TypeVar

from core.abstract_repositories.db_repository import ICRUDRepository

T = TypeVar("T")


class IORMLinkRepository[T](ICRUDRepository):
    """
    Abstract ORM link repository for ORMs with eager load like SQLAlchemy.

    Raises exception if link not found, return link model with relationship if needed.
    """

    @abstractmethod
    async def get_by_url(self, url: str) -> T:
        raise NotImplementedError

    @abstractmethod
    async def get_with_clicks(self, url: str) -> T:
        raise NotImplementedError

    @abstractmethod
    async def get_multiple_links_by_urls(self, urls: list[str]) -> list[T]:
        raise NotImplementedError

    @abstractmethod
    async def get_multiple_links_by_ids(self, link_ids: list[int]) -> list[T]:
        raise NotImplementedError

    @abstractmethod
    async def increment_click_counters(self, links_data: dict[int, int]) -> list[T]:
        raise NotImplementedError
