import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.core.exception_factory import exception_factory
from src.modules.auth.service import get_current_user
from src.modules.link.dependencies import get_link_service
from src.modules.link.schemas.schemas import (
    SLinkCreate,
    SLinkCreateDTO,
    SLinkResponse,
)
from src.modules.link.service.service import LinkService
from src.modules.user.schemas.schemas import SUserInDB

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/links", tags=["links"])


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
    service: Annotated[LinkService, Depends(get_link_service)],
    current_user: Annotated[SUserInDB, Depends(get_current_user)],
):
    link_to_create = SLinkCreateDTO(
        user_id=current_user.id, base_url=str(link.base_url)
    )
    new_link = await service.create_link(link_to_create)
    return new_link


@router.get(
    "/{link_url}",
    response_model=SLinkResponse,
    status_code=status.HTTP_200_OK,
    summary="Get info about link by short url",
    description="Get base_url, url and click_counter for link ",
    responses={
        200: {"description": "Link successfully found"},
        404: {"description": "Link not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_link_by_short_url(
    link_url: str,
    service: Annotated[LinkService, Depends(get_link_service)],
    current_user: Annotated[SUserInDB, Depends(get_current_user)],
):
    link = await service.get_link(link_url)
    if link.user_id == current_user.id:
        return link
    else:
        raise exception_factory.not_found("link id", "{link.id}")


@router.delete(
    "/{link_url}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete link",
    description="Delete link by short url",
    responses={
        204: {"description": "Link successfully deleted"},
        400: {"description": "Invalid link provided"},
        404: {"description": "Link not found"},
        500: {"description": "Internal server error"},
    },
)
async def delete_link(
    link_url: str,
    service: Annotated[LinkService, Depends(get_link_service)],
    current_user: Annotated[SUserInDB, Depends(get_current_user)],
):
    link = await service.get_link(link_url)
    if link.user_id == current_user.id:
        await service.delete_link(link_url)
        return
    else:
        raise exception_factory.not_found("link url", "{link.url}")
