from typing import Annotated

from fastapi import Depends

from src.core.exception_factory import exception_factory
from src.modules.link.dependencies import get_link_repository
from src.modules.link.repository import LinkRepository
from src.modules.link.schemas.schemas import SLinkWithClicks
from src.modules.user.dependencies import get_user_repository
from src.modules.user.repository import UserRepository


async def _get_link_with_clicks_by_url(
    link_url: str, repo: Annotated[LinkRepository, Depends(get_link_repository)]
) -> SLinkWithClicks:
    link_id = (await repo.get_link_by_url(link_url)).id
    link_with_clicks = await repo.get_link_with_clicks(link_id)
    return link_with_clicks


async def get_distribution_by_week_days(
    link_url: str, repo: Annotated[LinkRepository, Depends(get_link_repository)]
) -> dict[str, int]:
    result: dict[str, int] = {}
    link = await _get_link_with_clicks_by_url(link_url, repo)
    for click in link.clicks:
        result[f'{click.created_at.strftime("%A")}'] = (
            result.get(f'{click.created_at.strftime("%A")}', 0) + 1
        )

    return result


async def _get_list_of_distribution_by_week_days_for_user(
    user_id: int,
    link_repo: Annotated[LinkRepository, Depends(get_link_repository)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> list[dict[str, int]]:
    links_statistics: list[dict[str, int]] = []

    user = await user_repo.get_user_with_all_links_by_user_id(user_id)

    for link in user.links:
        link_stats = await get_distribution_by_week_days(link.url, link_repo)
        links_statistics.append(link_stats)

    return links_statistics


async def get_full_distribution_by_week_days_for_user(
    user_id: int,
    link_repo: Annotated[LinkRepository, Depends(get_link_repository)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> dict[str, int]:
    full_week_days_statistics: dict[str, int] = {}

    links_stats = await _get_list_of_distribution_by_week_days_for_user(
        user_id, link_repo, user_repo
    )

    for stat in links_stats:
        for week_day in stat:
            full_week_days_statistics[week_day] = (
                full_week_days_statistics.get(week_day, 0) + stat[week_day]
            )

    return full_week_days_statistics


async def get_full_distribution_by_click_counter_for_user(
    user_id: int,
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> dict[str, int]:
    full_click_counter_statistics: dict[str, int] = {}

    user = await user_repo.get_user_with_all_links_by_user_id(user_id)

    for link in user.links:
        full_click_counter_statistics[link.url] = (
            full_click_counter_statistics.get(link.url, 0) + link.click_counter
        )

    return full_click_counter_statistics


async def check_id(
    url: str,
    user_id: int,
    link_repo: Annotated[LinkRepository, Depends(get_link_repository)],
):
    link = await link_repo.get_link_by_url(url)
    if link.user_id != user_id:
        raise exception_factory.not_found(resource="link", identifier=f"{url}")
