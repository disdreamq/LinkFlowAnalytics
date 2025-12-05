import logging
from typing import Annotated
from fastapi import APIRouter, status
from fastapi.params import Depends

from src.modules.analytics.base_user.schemas import SBaseUserAllLinksResponse, SBaseUserSingleLinkResponse
from src.modules.auth.service import get_current_user
from src.modules.user.schemas import SUserInDB


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["users"])


@router.get(
    "/summary",
    response_model=SBaseUserAllLinksResponse,
    status_code=status.HTTP_200_OK,
    summary="Get full analytics for base user by user_id for all links",
    responses={
        200: {"description": "Link successfully found"},
        404: {"description": "Link not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_full_links_analytics(
    current_user: Annotated[SUserInDB, Depends(get_current_user)],
): ...


@router.get(
    "/{link_url}",
    response_model=SBaseUserSingleLinkResponse,
    status_code=status.HTTP_200_OK,
    summary="Get analytics for link by link_url for base user",
    responses={
        200: {"description": "User successfully found"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_analytics_for_link(
    link_url: str, current_user: Annotated[SUserInDB, Depends(get_current_user)]
): ...
