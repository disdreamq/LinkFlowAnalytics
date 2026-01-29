import pytest

from src.modules.link.schemas import SLinkWithClicks
from src.modules.user.schemas import SUserWithLinks


class TestGDBWDSL:
    """Tests for get_distribution_by_week_days_single_link"""

    @pytest.mark.asyncio
    async def test_GDBWDSL_success(
        self, base_user_analytic_service, mock_link_service, sample_links_with_clicks
    ):
        """Test for GDBWDSL happy path"""
        mock_link_service.get_with_clicks.return_value = SLinkWithClicks(
            **sample_links_with_clicks[1]
        )

        result = (
            await base_user_analytic_service.get_distribution_by_week_days_single_link(
                sample_links_with_clicks[1]["user_id"],
                sample_links_with_clicks[1]["url"],
            )
        )

        assert result == (2, {"Saturday": 2})

    @pytest.mark.asyncio
    async def test_GDBWDSL_empty_link(
        self, base_user_analytic_service, mock_link_service, sample_links_with_clicks
    ):
        """Test for GDBWDSL happy path"""
        mock_link_service.get_with_clicks.return_value = SLinkWithClicks(
            **sample_links_with_clicks[0]
        )

        result = (
            await base_user_analytic_service.get_distribution_by_week_days_single_link(
                sample_links_with_clicks[1]["user_id"],
                sample_links_with_clicks[1]["url"],
            )
        )

        assert result == (0, {})

    @pytest.mark.asyncio
    async def test_GDBWDSL_full_weak(
        self,
        base_user_analytic_service,
        mock_link_service,
        sample_link_with_clicks_full_weak,
    ):
        """Test for correct week days name"""
        mock_link_service.get_with_clicks.return_value = SLinkWithClicks(
            **sample_link_with_clicks_full_weak
        )

        result = (
            await base_user_analytic_service.get_distribution_by_week_days_single_link(
                sample_link_with_clicks_full_weak["user_id"],
                sample_link_with_clicks_full_weak["url"],
            )
        )[1]

        assert "Monday" in result
        assert "Tuesday" in result
        assert "Wednesday" in result
        assert "Saturday" in result
        assert "Friday" in result
        assert "Thursday" in result

    @pytest.mark.asyncio
    async def test_GDBWDSL_different_days(
        self,
        base_user_analytic_service,
        mock_link_service,
        sample_link_many_clicks,
    ):
        """Test for summing click_counters"""
        mock_link_service.get_with_clicks.return_value = SLinkWithClicks(
            **sample_link_many_clicks
        )

        result = (
            await base_user_analytic_service.get_distribution_by_week_days_single_link(
                sample_link_many_clicks["user_id"], sample_link_many_clicks["url"]
            )
        )

        assert result == (
            4,
            {
                "Saturday": 2,
                "Friday": 1,
                "Thursday": 1,
            },
        )


class TestGFDBWD:
    """Tests for get_full_distribution_by_week_days_for_user"""

    @pytest.mark.asyncio
    async def test_GFDBWD_success(
        self,
        base_user_analytic_service,
        mock_link_service,
        mock_user_service,
        sample_user_with_links,
        sample_links_with_clicks,
    ):
        mock_user_service.get_with_links.return_value = SUserWithLinks(
            **sample_user_with_links
        )
        mock_link_service.get_with_clicks.return_value = SLinkWithClicks(
            **sample_links_with_clicks[1]
        )

        result = await base_user_analytic_service.get_full_distribution_by_week_days(
            sample_user_with_links["id"]
        )

        assert "Saturday" in result
        assert result["Saturday"] == 4

    @pytest.mark.asyncio
    async def test_GFDBWD_empty_links(
        self,
        base_user_analytic_service,
        mock_link_service,
        sample_user_with_links,
        sample_links_with_clicks,
        mock_user_service,
    ):
        """Test for GDBWD user with links with 0 click_counter"""
        mock_user_service.get_with_links.return_value = SUserWithLinks(
            **sample_user_with_links
        )
        mock_link_service.get_with_clicks.return_value = SLinkWithClicks(
            **sample_links_with_clicks[0]
        )

        result = await base_user_analytic_service.get_full_distribution_by_week_days(
            sample_user_with_links["id"]
        )

        assert result == {}

    @pytest.mark.asyncio
    async def test_GFDBWD_full_weak(
        self,
        base_user_analytic_service,
        mock_user_service,
        mock_link_service,
        sample_user_with_links,
        sample_link_with_clicks_full_weak,
    ):
        """Test for correct week days name"""
        mock_user_service.get_with_links.return_value = SUserWithLinks(
            **sample_user_with_links
        )
        mock_link_service.get_with_clicks.return_value = SLinkWithClicks(
            **sample_link_with_clicks_full_weak
        )

        result = await base_user_analytic_service.get_full_distribution_by_week_days(
            sample_user_with_links["id"]
        )

        assert "Monday" in result
        assert "Tuesday" in result
        assert "Wednesday" in result
        assert "Saturday" in result
        assert "Friday" in result
        assert "Thursday" in result

    @pytest.mark.asyncio
    async def test_GFDBWD_different_days(
        self,
        base_user_analytic_service,
        mock_user_service,
        mock_link_service,
        sample_user_with_links,
        sample_link_many_clicks,
    ):
        """Test for summing click_counters"""
        mock_user_service.get_with_links.return_value = SUserWithLinks(
            **sample_user_with_links
        )
        mock_link_service.get_with_clicks.return_value = SLinkWithClicks(
            **sample_link_many_clicks
        )

        result = await base_user_analytic_service.get_full_distribution_by_week_days(
            sample_user_with_links["id"]
        )

        assert result == {
            "Saturday": 4,
            "Friday": 2,
            "Thursday": 2,
        }

    @pytest.mark.asyncio
    async def test_GFDBWD_one_link(
        self,
        base_user_analytic_service,
        mock_link_service,
        sample_user_with_one_link,
        sample_links_with_clicks,
        mock_user_service,
    ):
        """Test for GDBWD user with links with 0 click_counter"""
        mock_user_service.get_with_links.return_value = SUserWithLinks(
            **sample_user_with_one_link
        )
        mock_link_service.get_with_clicks.return_value = SLinkWithClicks(
            **sample_links_with_clicks[1]
        )

        result = await base_user_analytic_service.get_full_distribution_by_week_days(
            sample_user_with_one_link["id"]
        )

        assert result == {"Saturday": 2}


class TestGFDBU:
    "Tests for get_full_distribution_by_url"

    @pytest.mark.asyncio
    async def test_GFDBU_success(
        self,
        base_user_analytic_service,
        mock_user_service,
        sample_user_with_links,
    ):
        mock_user_service.get_with_links.return_value = SUserWithLinks(
            **sample_user_with_links
        )

        result = (
            await base_user_analytic_service.get_full_distribution_by_url(
                sample_user_with_links["id"]
            )
        )

        assert result == {"aaaaa": 5, "aaaab": 5}

    @pytest.mark.asyncio
    async def test_GFDBСС_empty_links(
        self,
        base_user_analytic_service,
        sample_user_with_links,
        mock_user_service,
    ):
        sample_user_with_links["links"] = []
        """Test for GDBWD user with links with 0 click_counter"""
        mock_user_service.get_with_links.return_value = SUserWithLinks(
            **sample_user_with_links
        )

        result = (
            await base_user_analytic_service.get_full_distribution_by_url(
                sample_user_with_links["id"]
            )
        )

        assert result == {}

    @pytest.mark.asyncio
    async def test_GFDBU_one_link(
        self,
        base_user_analytic_service,
        sample_user_with_one_link,
        mock_user_service,
    ):
        """Test for GDBWD user with links with 0 click_counter"""
        mock_user_service.get_with_links.return_value = SUserWithLinks(
            **sample_user_with_one_link
        )

        result = (
            await base_user_analytic_service.get_full_distribution_by_url(
                sample_user_with_one_link["id"]
            )
        )

        assert result == {"aaaaa": 5}
