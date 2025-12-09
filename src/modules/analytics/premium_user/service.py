from typing import Annotated
from fastapi import Depends
from src.modules.analytics.base_user.service import _get_link_with_clicks_by_url
from src.modules.link.dependencies import get_link_repository
from src.modules.link.repository import LinkRepository
from src.modules.user.dependencies import get_user_repository
from src.modules.user.repository import UserRepository


async def get_distribution_by_browser_for_link(
    link_url: str, repo: Annotated[LinkRepository, Depends(get_link_repository)]
) -> dict[str, int]:
    link = await _get_link_with_clicks_by_url(link_url, repo)
    result: dict[str, int] = {}

    for click in link.clicks:
        # User_agent example from click table: # "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:145.0) Gecko/20100101 Firefox/145.0"
        browser = click.user_agent[: click.user_agent.find(" ")]
        result[browser] = result.get(browser, 0) + 1

    return result


async def get_full_distribution_by_browser_for_user(
    user_id: int,
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    link_repo: Annotated[LinkRepository, Depends(get_link_repository)],
) -> dict[str, int]:
    full_browser_statistics: dict[str, int] = {}
    links_stats = await _get_list_of_distribution_by_browser_for_user(
        user_id, user_repo, link_repo
    )

    for stat in links_stats:
        for browser in stat.keys():
            full_browser_statistics[browser] = (
                full_browser_statistics.get(browser, 0) + stat[browser]
            )

    return full_browser_statistics


async def _get_list_of_distribution_by_browser_for_user(
    user_id: int,
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    link_repo: Annotated[LinkRepository, Depends(get_link_repository)],
) -> list[dict[str, int]]:
    links_statistics: list[dict[str, int]] = []

    user = await user_repo.get_user_with_all_links_by_user_id(user_id)

    for link in user.links:
        link_stats = await get_distribution_by_browser_for_link(link.url, link_repo)
        links_statistics.append(link_stats)

    return links_statistics
