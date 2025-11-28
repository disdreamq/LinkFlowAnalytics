from typing import Annotated
from fastapi import APIRouter
from fastapi.params import Depends
from fastapi.responses import RedirectResponse
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.link.schemas import SLinkCreate
from src.entities.dependencies import get_session
from src.entities.link.repository import LinkRepository
from src.core.exceptions_factory import exception_factory


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/create")
async def create_link(
    link: SLinkCreate, session: Annotated[AsyncSession, Depends(get_session)]
):
    repo = LinkRepository(session)
    new_link = await repo.create_link(link)
    if not new_link:
        raise
    return new_link.url


@router.get("/{url}")
async def redirect(url: str, session: Annotated[AsyncSession, Depends(get_session)]):
    repo = LinkRepository(session)
    link = await repo.get_link_by_url(url)
    if not link:
        raise exception_factory.not_found(resource="link", identifier="url")
    return RedirectResponse(link.base_url)
