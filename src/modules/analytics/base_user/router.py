import logging
from typing import Annotated

from fastapi import APIRouter, status
from fastapi.params import Depends

from src.modules.analytics.base_user.schemas import (
    SBaseUserAllLinksResponse,
    SBaseUserSingleLinkResponse,
)
from src.modules.analytics.base_user.service import BaseUserAnalyticService
from src.modules.analytics.dependencies import get_base_user_analytics_service
from src.modules.auth.dependencies import require_auth
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
    current_user: Annotated[SUserInDB, Depends(require_auth)],
    analytic_service: Annotated[
        BaseUserAnalyticService, Depends(get_base_user_analytics_service)
    ],
):
    distr_for_click_counter = (
        await analytic_service.get_full_distribution_by_click_counter_for_user(
            current_user.id
        )
    )
    distr_by_week_days = (
        await analytic_service.get_full_distribution_by_week_days_for_user(
            current_user.id
        )
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
    current_user: Annotated[SUserInDB, Depends(require_auth)],
    analytic_service: Annotated[
        BaseUserAnalyticService, Depends(get_base_user_analytics_service)
    ],
):
    distr_by_week_days = (
        await analytic_service.get_distribution_by_week_days_single_link(
            user_id=current_user.id, link_url=link_url
        )
    )
    return SBaseUserSingleLinkResponse(
        url=link_url,
        click_counter=distr_by_week_days[0],
        distribution_by_week_days=distr_by_week_days[1],
    )
