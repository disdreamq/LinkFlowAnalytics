from abc import ABC, abstractmethod
from typing import Any


class IKeyValueRepository(ABC):
    """Interface for key-value storage.

    Raises:
        NotImplementedError for any not implemented methods.
    """

    @abstractmethod
    async def set_(self, *args, **kwargs) -> bool:
        raise NotImplementedError from None

    @abstractmethod
    async def get(self, *args, **kwargs) -> str | None:
        raise NotImplementedError from None

    @abstractmethod
    async def delete(self, *args, **kwargs) -> int:
        raise NotImplementedError from None

    @abstractmethod
    async def exists(self, *args, **kwargs) -> bool:
        raise NotImplementedError from None
