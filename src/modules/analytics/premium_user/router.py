import logging
from typing import Annotated

from fastapi import APIRouter, status
from fastapi.params import Depends

from src.modules.analytics.base_user.service import (
    get_distribution_by_week_days,
    get_full_distribution_by_click_counter_for_user,
    get_full_distribution_by_week_days_for_user,
)
from src.modules.analytics.premium_user.dependencies import require_premimum_tarifplan
from src.modules.analytics.premium_user.schemas import (
    SPremiumUserLinksResponse,
    SPremiumUserLinkStatsResponse,
)
from src.modules.analytics.premium_user.service import (
    get_distribution_by_browser_for_link,
    get_full_distribution_by_browser_for_user,
)
from src.modules.auth.dependencies import require_auth
from src.modules.link.dependencies import get_link_service
from src.modules.link.service.service import LinkService
from src.modules.user.dependencies import get_user_service
from src.modules.user.schemas import SUserInDB
from src.modules.user.service import UserService

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/analytics/premium",
    tags=["users"],
    dependencies=[Depends(require_premimum_tarifplan)],
)


@router.get(
    "/summary",
    response_model=SPremiumUserLinksResponse,
    status_code=status.HTTP_200_OK,
    summary="Get full analytics for premium user by user_id for all links",
    responses={
        200: {"description": "Link successfully found"},
        404: {"description": "Link not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_full_links_analytics(
    current_user: Annotated[SUserInDB, Depends(require_auth)],
    link_service: Annotated[LinkService, Depends(get_link_service)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    distr_by_click_counter = await get_full_distribution_by_click_counter_for_user(
        current_user.id,
        user_service,
    )
    distr_by_week_days = await get_full_distribution_by_week_days_for_user(
        current_user.id, link_service, user_service
    )
    distr_by_browser = await get_full_distribution_by_browser_for_user(
        current_user.id, link_service, user_service
    )
    return SPremiumUserLinksResponse(
        user_id=current_user.id,
        full_distribution_by_click_counter=distr_by_click_counter,
        full_distribution_by_week_days=distr_by_week_days,
        full_distribution_by_browser=distr_by_browser,
    )


@router.get(
    "/{link_url}",
    response_model=SPremiumUserLinkStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get analytics for link by link_url for premium",
    responses={
        200: {"description": "User successfully found"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_analytics_for_link(
    link_url: str,
    current_user: Annotated[SUserInDB, Depends(require_auth)],
    link_service: Annotated[LinkService, Depends(get_link_service)],
):
    distr_by_click_counter = (
        await link_service.get_link_for_redirect(link_url)
    ).click_counter
    distr_by_week_days = await get_distribution_by_week_days(
        user_id=current_user.id, link_url=link_url, service=link_service
    )
    distr_by_browser = await get_distribution_by_browser_for_link(
        user_id=current_user.id, link_url=link_url, link_service=link_service
    )
    return SPremiumUserLinkStatsResponse(
        url=link_url,
        click_counter=distr_by_click_counter,
        distribution_by_week_days=distr_by_week_days,
        distribution_by_browser=distr_by_browser,
    )
