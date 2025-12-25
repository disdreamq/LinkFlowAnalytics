from abc import abstractmethod
from typing import Any

from src.core.abstract_repositories.key_value_repository import IKeyValueRepository


class ILocalMemoryRepository(IKeyValueRepository):

    @abstractmethod
    async def add_to_arr(self, *entity_data: Any) -> int:
        raise NotImplementedError from None

    @abstractmethod
    async def get_arr(self, *entity_data: Any) -> list[Any]:
        raise NotImplementedError from None
