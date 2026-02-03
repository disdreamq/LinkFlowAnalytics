import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Path, status

from src.modules.auth.dependencies import require_auth
from src.modules.link.dependencies import get_link_service
from src.modules.link.schemas import (
    SLinkCreate,
    SLinkCreateDTO,
    SLinkResponse,
)
from src.modules.link.service.service import LinkService
from src.modules.user.schemas import SUserInDB

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
        422: {"description": "Invalid URL provided"},
        500: {"description": "Internal server error"},
    },
)
async def create_link(
    link: SLinkCreate,
    service: Annotated[LinkService, Depends(get_link_service)],
    current_user: Annotated[SUserInDB, Depends(require_auth)],
):
    link_to_create = SLinkCreateDTO(
        user_id=current_user.id, base_url=str(link.base_url)
    )
    created_link = await service.create(link_to_create)
    return created_link


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
async def get_link_by_url(
    link_url: Annotated[str, Path(pattern="^[A-Za-z0-9]{5}$")],
    service: Annotated[LinkService, Depends(get_link_service)],
    current_user: Annotated[SUserInDB, Depends(require_auth)],
):
    link = await service.get_by_url(user_id=current_user.id, link_url=link_url)
    return link


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
    link_url: Annotated[str, Path(pattern="^[A-Za-z0-9]{5}$")],
    service: Annotated[LinkService, Depends(get_link_service)],
    current_user: Annotated[SUserInDB, Depends(require_auth)],
):
    await service.delete(user_id=current_user.id, link_url=link_url)
    return
