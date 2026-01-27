from typing import Annotated

from fastapi import Depends

from src.modules.link.dependencies import get_link_service
from src.modules.link.service.service import LinkService
from src.modules.user.dependencies import get_user_service
from src.modules.user.service import UserService


class PremiumUserAnalyticService:
    def __init__(
        self,
        link_service: Annotated[LinkService, Depends(get_link_service)],
        user_service: Annotated[UserService, Depends(get_user_service)],
    ):
        self.link_service = link_service
        self.user_service = user_service

    async def get_distribution_by_browser_single_link(
        self,
        user_id: int,
        link_url: str,
    ) -> dict[str, int]:
        """Func returns a dict with browser as a key and summ of clicks from this
        browser as a value

        Args:
            user_id: int
            link_url: str

        Returns:
            dict[str, int]: dict with browser: sum of clicks from this browser
        """
        link = await self.link_service.get_with_clicks(
            user_id=user_id, link_url=link_url
        )
        result: dict[str, int] = {}

        for click in link.clicks:
            # User_agent example from click table: # "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:145.0) Gecko/20100101 Firefox/145.0"
            browser = click.user_agent[: click.user_agent.find(" ")]
            result[browser] = result.get(browser, 0) + 1

        return result

    async def get_full_distribution_by_browser(
        self,
        user_id: int,
    ) -> dict[str, int]:
        full_browser_statistics: dict[str, int] = {}
        links_stats = await self._get_list_of_distribution_by_browser(user_id)

        for stat in links_stats:
            for browser in stat:
                full_browser_statistics[browser] = (
                    full_browser_statistics.get(browser, 0) + stat[browser]
                )

        return full_browser_statistics

    async def _get_list_of_distribution_by_browser(
        self,
        user_id: int,
    ) -> list[dict[str, int]]:
        links_statistics: list[dict[str, int]] = []

        user = await self.user_service.get_with_links(user_id)

        for link in user.links:
            link_stats = await self.get_distribution_by_browser_single_link(
                user_id=user_id, link_url=link.url
            )
            links_statistics.append(link_stats)

        return links_statistics
