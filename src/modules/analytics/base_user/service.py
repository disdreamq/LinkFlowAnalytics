from typing import Annotated

from fastapi import Depends

from src.modules.link.dependencies import get_link_service
from src.modules.link.service.service import LinkService
from src.modules.user.dependencies import get_user_service
from src.modules.user.service import UserService


class BaseUserAnalyticService:
    def __init__(
        self,
        link_service: Annotated[LinkService, Depends(get_link_service)],
        user_service: Annotated[UserService, Depends(get_user_service)],
    ):
        self.link_service = link_service
        self.user_service = user_service

    async def get_distribution_by_week_days_single_link(
        self,
        user_id: int,
        link_url: str,
    ) -> tuple[int, dict[str, int]]:
        """Returns distribution for single link by week days

        Args:
            user_id (int)
            link_url (str)
            service LinkService (Depends)

        Returns:
            dict[str, int]: dict with distribution by week days
        """

        result: dict[str, int] = {}
        link = await self.link_service.get_with_clicks(
            user_id=user_id, link_url=link_url
        )
        click_counter = link.click_counter
        for click in link.clicks:
            result[f'{click.created_at.strftime("%A")}'] = (
                result.get(f'{click.created_at.strftime("%A")}', 0) + 1
            )

        return click_counter, result

    async def _get_list_of_distribution_by_week_days_for_user(
        self,
        user_id: int,
    ) -> list[dict[str, int]]:
        """Helper for getting list of dicts with distribution by week days for user

        Args:
            user_id: int
            link_service: LinkService(Depends)
            user_service: UserService(Depends)

        Returns:
            list[dict[str, int]]: List of dicts with distribution by week days
            from func get_distribution_by_week_days_single_link
        """

        links_statistics: list[dict[str, int]] = []

        user = await self.user_service.get_with_links(user_id)

        for link in user.links:
            link_stats = await self.get_distribution_by_week_days_single_link(
                user_id=user_id, link_url=link.url
            )
            links_statistics.append(link_stats[1])

        return links_statistics

    async def get_full_distribution_by_week_days_for_user(
        self,
        user_id: int,
    ) -> dict[str, int]:
        """Function for getting full distribution by week days for user
        returns dict with this distribution, including all links with link.user_id equal
        to provided user_id

        Args:
            user_id: int
            link_service: LinkService(Depends)
            user_service: UserService(Depends)

        Returns:
            dict[str, int]: Dict with distribution by week days
        """

        full_week_days_statistics: dict[str, int] = {}

        links_stats = await self._get_list_of_distribution_by_week_days_for_user(
            user_id,
        )

        for stat in links_stats:
            for week_day in stat:
                full_week_days_statistics[week_day] = (
                    full_week_days_statistics.get(week_day, 0) + stat[week_day]
                )

        return full_week_days_statistics

    async def get_full_distribution_by_click_counter_for_user(
        self,
        user_id: int,
    ) -> dict[str, int]:
        """Function for getting full distribution by click counter for user
        returns dict with this distribution, including all links with link.user_id equal
        to provided user_id
        Args:
            user_id: int
            user_service: UserService(Depends)

        Returns:
            dict[str, int]: Dict with distribution by click counter
        """

        full_click_counter_statistics: dict[str, int] = {}

        user = await self.user_service.get_with_links(user_id)

        for link in user.links:
            full_click_counter_statistics[link.url] = (
                full_click_counter_statistics.get(link.url, 0) + link.click_counter
            )

        return full_click_counter_statistics
