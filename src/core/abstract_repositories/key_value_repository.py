from abc import ABC, abstractmethod
from typing import Any


class IKeyValueRepository(ABC):
    """
    Abstract repository with base CRUD.

    raises exception if entity not found, returns entity model.
    """

    @abstractmethod
    async def set_(self, *entity_data: Any) -> bool:
        raise NotImplementedError from None

    @abstractmethod
    async def get(self, *entity_data: Any) -> str | None:
        raise NotImplementedError from None

    @abstractmethod
    async def delete(self, *entity_data: Any) -> int:
        raise NotImplementedError from None

    @abstractmethod
    async def exists(self, *entity_data: Any) -> bool:
        raise NotImplementedError from None
