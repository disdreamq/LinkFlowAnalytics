from abc import ABC, abstractmethod
import logging
from typing import Literal, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, NoResultFound

from src.core.exceptions_factory import exception_factory
from src.entities.link.models import Link
from src.entities.link.schemas import SLinkCreate

logger = logging.getLogger(__name__)


class AbstractRepository(ABC):
    @abstractmethod
    async def create_link():
        raise NotImplementedError

    @abstractmethod
    async def get_user():
        raise NotImplementedError

    @abstractmethod
    async def update_user():
        raise NotImplementedError

    @abstractmethod
    async def delete_user():
        raise NotImplementedError


class LinkRepository(AbstractRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_link(self, link: SLinkCreate) -> Link:
        return Link()