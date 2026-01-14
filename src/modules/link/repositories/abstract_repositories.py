from abc import abstractmethod
from typing import TypeVar

from src.core.abstract_repositories.db_repository import ICRUDRepository

T = TypeVar("T")


class IORMLinkRepository[T](ICRUDRepository):
    """Interface for link. Use for ORMs with eager load like SQLAlchemy.

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
        """Get multiple links by urls in one request.

        Args:
            urls (list[str]): link urls

        Raises:
            NotImplementedError: if method not implemented

        Returns:
            list[T]: list of links
        """
        raise NotImplementedError

    @abstractmethod
    async def get_multiple_links_by_ids(self, link_ids: list[int]) -> list[T]:
        raise NotImplementedError

    @abstractmethod
    async def increment_click_counters(self, links_data: dict[int, int]) -> list[T]:
        """Increment click counters for multiple links in one request.

        Args:
            links_data (dict[int, int]): dict with link id and incemetns for each link.

        Raises:
            NotImplementedError: if method not implemented

        Returns:
            list[T]: list of links.
        """
        raise NotImplementedError
