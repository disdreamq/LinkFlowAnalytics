from abc import ABC, abstractmethod
from typing import Literal, TypeVar

T = TypeVar("T")


class ICRUDRepository[T](ABC):
    """
    Abstract repository with base CRUD.

    raises exception if entity not found, returns entity model.
    """

    @abstractmethod
    async def create(self, **entity_data) -> T:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, **entity_data) -> T:
        raise NotImplementedError

    @abstractmethod
    async def update(self, **entity_data) -> T:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, **entity_data) -> Literal[True]:
        raise NotImplementedError
