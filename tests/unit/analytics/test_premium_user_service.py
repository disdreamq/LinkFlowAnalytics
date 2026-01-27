import pytest

from src.modules.link.schemas import SLinkWithClicks
from src.modules.user.schemas import SUserWithLinks


class TestGDBBSL:
    """Tests for get_distribution_by_browser_single_link"""

    @pytest.mark.asyncio
    async def test_GDBBSL_different_clicks_summing(
        self, mock_link_service, prem_user_analytic_service, sample_links_with_clicks
    ):
        """2 clicks from same browser"""
        mock_link_service.get_with_clicks.return_value = SLinkWithClicks(
            **sample_links_with_clicks[1]
        )

        result = (
            await prem_user_analytic_service.get_distribution_by_browser_single_link(
                sample_links_with_clicks[1]["user_id"],
                sample_links_with_clicks[1]["url"],
            )
        )

        assert result == {"Mozilla/5.0": 2}

    @pytest.mark.asyncio
    async def test_GDBBSL_different_browsers(
        self,
        mock_link_service,
        prem_user_analytic_service,
        sample_link_with_clicks_different_browsers,
    ):
        mock_link_service.get_with_clicks.return_value = SLinkWithClicks(
            **sample_link_with_clicks_different_browsers
        )

        result = (
            await prem_user_analytic_service.get_distribution_by_browser_single_link(
                sample_link_with_clicks_different_browsers["user_id"],
                sample_link_with_clicks_different_browsers["url"],
            )
        )

        assert result == {"Mozilla/5.0": 1, "Chrome/52.0": 1, "Yandex/1.2": 1}

    @pytest.mark.asyncio
    async def test_GDBBSL_empty_link(
        self,
        mock_link_service,
        prem_user_analytic_service,
        sample_links_with_clicks,
    ):
        mock_link_service.get_with_clicks.return_value = SLinkWithClicks(
            **sample_links_with_clicks[0]
        )

        result = (
            await prem_user_analytic_service.get_distribution_by_browser_single_link(
                sample_links_with_clicks[0]["user_id"],
                sample_links_with_clicks[0]["url"],
            )
        )

        assert result == {}

    @pytest.mark.asyncio
    async def test_GDBBSL_different_browsers_summing_click_counters(
        self,
        mock_link_service,
        prem_user_analytic_service,
        sample_link_with_clicks_different_browsers_summing_click_counter,
    ):
        """Tests for 3 clicks and 2 bworsers for summing this 2 browsers together"""
        mock_link_service.get_with_clicks.return_value = SLinkWithClicks(
            **sample_link_with_clicks_different_browsers_summing_click_counter
        )

        result = (
            await prem_user_analytic_service.get_distribution_by_browser_single_link(
                sample_link_with_clicks_different_browsers_summing_click_counter[
                    "user_id"
                ],
                sample_link_with_clicks_different_browsers_summing_click_counter["url"],
            )
        )

        assert result == {"Mozilla/5.0": 1, "Chrome/52.0": 2}


class TestGFDBB:
    """Tests for get_full_distribution_by_browser"""

    @pytest.mark.asyncio
    async def test_GFDBB_different_clicks_summing(
        self,
        mock_user_service,
        mock_link_service,
        prem_user_analytic_service,
        sample_user_with_links,
        sample_links_with_clicks,
    ):
        mock_user_service.get_with_links.return_value = SUserWithLinks(
            **sample_user_with_links
        )

        mock_link_service.get_with_clicks.return_value = SLinkWithClicks(
            **sample_links_with_clicks[1]
        )

        result = await prem_user_analytic_service.get_full_distribution_by_browser(
            sample_user_with_links["id"]
        )

        assert result == {"Mozilla/5.0": 4}

    @pytest.mark.asyncio
    async def test_GFDBB_different_browsers(
        self,
        mock_user_service,
        mock_link_service,
        prem_user_analytic_service,
        sample_user_with_links,
        sample_link_with_clicks_different_browsers,
    ):
        mock_user_service.get_with_links.return_value = SUserWithLinks(
            **sample_user_with_links
        )

        mock_link_service.get_with_clicks.return_value = SLinkWithClicks(
            **sample_link_with_clicks_different_browsers
        )

        result = await prem_user_analytic_service.get_full_distribution_by_browser(
            sample_user_with_links["id"]
        )

        assert result == {"Mozilla/5.0": 2, "Chrome/52.0": 2, "Yandex/1.2": 2}

    @pytest.mark.asyncio
    async def test_GFDBB_empty_link(
        self,
        mock_user_service,
        mock_link_service,
        prem_user_analytic_service,
        sample_user_with_one_link,
        sample_links_with_clicks,
    ):
        mock_user_service.get_with_links.return_value = SUserWithLinks(
            **sample_user_with_one_link
        )

        mock_link_service.get_with_clicks.return_value = SLinkWithClicks(
            **sample_links_with_clicks[0]
        )

        result = await prem_user_analytic_service.get_full_distribution_by_browser(
            sample_links_with_clicks[0]["id"]
        )

        assert result == {}

    @pytest.mark.asyncio
    async def test_GFDBB_different_browsers_summing_click_counters(
        self,
        mock_user_service,
        mock_link_service,
        prem_user_analytic_service,
        sample_user_with_one_link,
        sample_link_with_clicks_different_browsers_summing_click_counter,
    ):
        mock_user_service.get_with_links.return_value = SUserWithLinks(
            **sample_user_with_one_link
        )

        mock_link_service.get_with_clicks.return_value = SLinkWithClicks(
            **sample_link_with_clicks_different_browsers_summing_click_counter
        )

        result = await prem_user_analytic_service.get_full_distribution_by_browser(
            sample_link_with_clicks_different_browsers_summing_click_counter["user_id"]
        )

        assert result == {"Mozilla/5.0": 1, "Chrome/52.0": 2}
