import logging
from typing import Annotated

from fastapi import APIRouter, status
from fastapi.params import Depends

from src.modules.analytics.base_user.schemas import (
    SBaseUserAllLinksResponse,
    SBaseUserSingleLinkResponse,
)
from src.modules.analytics.base_user.service import (
    check_id,
    get_distribution_by_week_days,
    get_full_distribution_by_click_counter_for_user,
    get_full_distribution_by_week_days_for_user,
)
from src.modules.auth.service import get_current_user
from src.modules.link.dependencies import get_link_repository
from src.modules.link.repository import LinkRepository
from src.modules.user.dependencies import get_user_repository
from src.modules.user.repository import UserRepository
from src.modules.user.schemas.schemas import SUserInDB

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
    link_repo: Annotated[LinkRepository, Depends(get_link_repository)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
):
    distr_for_click_counter = await get_full_distribution_by_click_counter_for_user(
        current_user.id, user_repo
    )
    distr_by_week_days = await get_full_distribution_by_week_days_for_user(
        current_user.id, link_repo, user_repo
    )
    return SBaseUserAllLinksResponse(
        user_id=current_user.id,
        full_distribution_by_click_counter=distr_for_click_counter,
        full_distribution_by_week_days=distr_by_week_days,
    )


@router.get(
    "/{link_url}",
    response_model=SBaseUserSingleLinkResponse,
    status_code=status.HTTP_200_OK,
    summary="Get analytics for link by link_url for base user",
    responses={
        200: {"description": "Link successfully found"},
        404: {"description": "Link not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_analytics_for_link(
    link_url: str,
    current_user: Annotated[SUserInDB, Depends(get_current_user)],
    link_repo: Annotated[LinkRepository, Depends(get_link_repository)],
):
    await check_id(link_url, current_user.id, link_repo)
    click_counter = (await link_repo.get_link_by_url(link_url)).click_counter
    distr_by_week_days = await get_distribution_by_week_days(link_url, link_repo)
    return SBaseUserSingleLinkResponse(
        url=link_url,
        click_counter=click_counter,
        distribution_by_week_days=distr_by_week_days,
    )
