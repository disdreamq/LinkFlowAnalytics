from abc import abstractmethod
from typing import Any

from src.core.abstract_repositories.key_value_repository import IKeyValueRepository


class IRedisRepository(IKeyValueRepository):
    """Interface for redis.

    Raises:
        NotImplementedError for any not implemented methods.
    """

    @abstractmethod
    async def add_to_arr(self, *entity_data: Any) -> int:
        """Add elements to array in redis.

        Returns:
            int: Number of elements that was added to redis.
        """
        raise NotImplementedError from None

    @abstractmethod
    async def get_arr(self, *entity_data: Any) -> list[str]:
        """Get array from redis.

        Returns:
            list[str]: list of strings from redis.
        """
        raise NotImplementedError from None
