from abc import ABC, abstractmethod
from typing import Any, Literal, TypeVar

T = TypeVar("T")


class ICRUDRepository[T](ABC):
    """Interface for db repositories with base CRUD.

    Raises:
        NotImplementedError for any not implemented methods.
    """

    @abstractmethod
    async def create(self, *entity_data: Any) -> T:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, *entity_data: Any) -> T:
        raise NotImplementedError

    @abstractmethod
    async def update(self, *entity_data: Any) -> T:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, *entity_data: Any) -> Literal[True]:
        raise NotImplementedError
