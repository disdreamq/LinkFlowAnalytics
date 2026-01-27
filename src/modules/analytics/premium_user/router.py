import logging
from typing import Annotated

from fastapi import APIRouter, status
from fastapi.params import Depends

from src.modules.analytics.base_user.dependencies import get_base_user_analytics_service
from src.modules.analytics.base_user.service import BaseUserAnalyticService
from src.modules.analytics.premium_user.dependencies import (
    get_premium_user_analytic_service,
    require_premimum_tarifplan,
)
from src.modules.analytics.premium_user.schemas import (
    SPremiumUserLinksResponse,
    SPremiumUserLinkStatsResponse,
)
from src.modules.analytics.premium_user.service import PremiumUserAnalyticService
from src.modules.auth.dependencies import require_auth
from src.modules.user.schemas import SUserInDB

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
    premium_user_analytic_service: Annotated[
        PremiumUserAnalyticService, Depends(get_premium_user_analytic_service)
    ],
    base_user_analytic_service: Annotated[
        BaseUserAnalyticService, Depends(get_base_user_analytics_service)
    ],
):
    distr_by_click_counter = (
        await base_user_analytic_service.get_full_distribution_by_click_counter(
            current_user.id,
        )
    )
    distr_by_week_days = (
        await base_user_analytic_service.get_full_distribution_by_week_days(
            current_user.id
        )
    )
    distr_by_browser = (
        await premium_user_analytic_service.get_full_distribution_by_browser(
            current_user.id,
        )
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
    premium_user_analytic_service: Annotated[
        PremiumUserAnalyticService, Depends(get_premium_user_analytic_service)
    ],
    base_user_analytic_service: Annotated[
        BaseUserAnalyticService, Depends(get_base_user_analytics_service)
    ],
):
    distr_by_click_counter = (  # 0 indexing click_counter, 1 indexing distr
        await base_user_analytic_service.get_distribution_by_week_days_single_link(
            user_id=current_user.id, link_url=link_url
        )
    )
    distr_by_browser = (
        await premium_user_analytic_service.get_distribution_by_browser_single_link(
            user_id=current_user.id, link_url=link_url
        )
    )
    return SPremiumUserLinkStatsResponse(
        url=link_url,
        click_counter=distr_by_click_counter[0],
        distribution_by_week_days=distr_by_click_counter[1],
        distribution_by_browser=distr_by_browser,
    )
