from abc import ABC, abstractmethod
from typing import Any, Literal, TypeVar

T = TypeVar("T")


class ICRUDRepository[T](ABC):
    """Interface for db repositories with base CRUD.

    Raises:
        NotImplementedError for any not implemented methods.
    """

    @abstractmethod
    async def create(self, *args, **kwargs) -> T:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, *args, **kwargs) -> T:
        raise NotImplementedError

    @abstractmethod
    async def update(self, *args, **kwargs) -> T:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, *args, **kwargs) -> Literal[True]:
        raise NotImplementedError
