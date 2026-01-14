from abc import abstractmethod
from typing import Any

from src.core.abstract_repositories.key_value_repository import IKeyValueRepository


class ILocalMemoryRepository(IKeyValueRepository):
    """ Interface for mock redis in local memory.

    Raises:
        NotImplementedError for any not implemented  methods.
    """
    @abstractmethod
    async def add_to_arr(self, *entity_data: Any) -> int:
        """Adding data to array in local memory.

        Raises:
            NotImplementedError

        Returns:
            int: Number of emelents added to array. If array with that
            name doesnt exists - creating it.
        """
        raise NotImplementedError from None

    @abstractmethod
    async def get_arr(self, *entity_data: Any) -> list[Any]:
        """Get array from local memory.

        Raises:
            NotImplementedError

        Returns:
            list[Any]: array from local memeory.
        """
        raise NotImplementedError from None
