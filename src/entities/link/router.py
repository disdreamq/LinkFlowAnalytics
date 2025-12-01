from typing import Annotated
from fastapi import APIRouter, Depends, status
from fastapi.responses import RedirectResponse
import logging

from pydantic import HttpUrl

from src.entities.link.dependencies import get_link_repository
from src.entities.link.schemas import SLinkCreate, SLinkResponse
from src.entities.link.repository import LinkRepository


logger = logging.getLogger(__name__)
router = APIRouter(tags=["links"])


@router.post(
    "/",
    response_model=SLinkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create short URL",
    description="Create a shor URL for simplify base URL",
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
    return new_link


@router.get(
    "/{url}",
    response_class=RedirectResponse,
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    summary="Redirect to original URL",
    description="Redirect to original URL from short URL",
    responses={
        307: {"description": "Redirect to original URL"},
        404: {"description": "Short URL not found"},
    },
)
async def redirect(
    url: HttpUrl, repo: Annotated[LinkRepository, Depends(get_link_repository)]
):
    link = await repo.get_link_by_base_url(str(url))
    return RedirectResponse(link.base_url)
