from typing import Annotated

from fastapi import Depends

from src.modules.link.dependencies import get_link_service
from src.modules.link.service.service import LinkService
from src.modules.user.dependencies import get_user_service
from src.modules.user.service import UserService


async def get_distribution_by_week_days(
    user_id: int,
    link_url: str,
    service: Annotated[LinkService, Depends(get_link_service)],
) -> dict[str, int]:
    result: dict[str, int] = {}
    link = await service.get_link_with_clicks(user_id=user_id, link_url=link_url)
    for click in link.clicks:
        result[f'{click.created_at.strftime("%A")}'] = (
            result.get(f'{click.created_at.strftime("%A")}', 0) + 1
        )

    return result


async def _get_list_of_distribution_by_week_days_for_user(
    user_id: int,
    link_service: Annotated[LinkService, Depends(get_link_service)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> list[dict[str, int]]:
    links_statistics: list[dict[str, int]] = []

    user = await user_service.get_user_with_all_links(user_id)

    for link in user.links:
        link_stats = await get_distribution_by_week_days(
            user_id=user_id, link_url=link.url, service=link_service
        )
        links_statistics.append(link_stats)

    return links_statistics


async def get_full_distribution_by_week_days_for_user(
    user_id: int,
    link_service: Annotated[LinkService, Depends(get_link_service)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> dict[str, int]:
    full_week_days_statistics: dict[str, int] = {}

    links_stats = await _get_list_of_distribution_by_week_days_for_user(
        user_id, link_service, user_service
    )

    for stat in links_stats:
        for week_day in stat:
            full_week_days_statistics[week_day] = (
                full_week_days_statistics.get(week_day, 0) + stat[week_day]
            )

    return full_week_days_statistics


async def get_full_distribution_by_click_counter_for_user(
    user_id: int,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> dict[str, int]:
    full_click_counter_statistics: dict[str, int] = {}

    user = await user_service.get_user_with_all_links(user_id)

    for link in user.links:
        full_click_counter_statistics[link.url] = (
            full_click_counter_statistics.get(link.url, 0) + link.click_counter
        )

    return full_click_counter_statistics
