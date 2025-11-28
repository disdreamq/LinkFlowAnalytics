from typing import Annotated
from fastapi import APIRouter, Depends, status
from fastapi.responses import RedirectResponse
import logging

from src.entities.link.dependencies import get_link_repository
from src.entities.link.schemas import SLinkCreate, SLinkGet
from src.entities.link.repository import LinkRepository
from src.core.exceptions_factory import exception_factory


logger = logging.getLogger(__name__)
router = APIRouter(tags=["links"])


@router.post(
    "/",
    response_model=SLinkGet,
    status_code=status.HTTP_201_CREATED,
    summary="Create short URL",
    description="Create a shortened URL for the provided original URL",
    responses={
        201: {"description": "URL successfully created"},
        400: {"description": "Invalid URL provided"},
        500: {"description": "Internal server error"},
    },
)
async def create_link(
    link: SLinkCreate,
    repo: Annotated[LinkRepository, Depends(get_link_repository)],
):
    new_link = await repo.create_link(link)
    if not new_link:
        raise
    return new_link.url


@router.get(
    "/{url}",
    response_class=RedirectResponse,
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    summary="Redirect to original URL",
    description="Redirect to the original URL using short code",
    responses={
        307: {"description": "Redirect to original URL"},
        404: {"description": "Short URL not found"},
    },
)
async def redirect(
    url: str, repo: Annotated[LinkRepository, Depends(get_link_repository)]
):
    link = await repo.get_link_by_url(url)
    return RedirectResponse(link.base_url)
