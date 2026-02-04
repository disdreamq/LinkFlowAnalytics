from datetime import datetime

import pytest


class TestGFLA:
    """Tests for /analytics/premium/summary/ (get method)
    GFLA - get_full_links_analytics
    """

    @pytest.mark.asyncio
    async def test_GFLA_success(
        self, sample_link_for_premium_user_analytics, client, premium_user
    ):
        response = await client.get(
            "/analytics/premium/summary", headers=premium_user["header"]
        )

        json = response.json()
        url = sample_link_for_premium_user_analytics["url"]
        assert json["user_id"] == premium_user["data"]["id"]
        assert url in json["full_distribution_by_click_counter"]
        assert json["full_distribution_by_click_counter"][url] == 50
        assert json["full_distribution_by_week_days"] == {
            f'{datetime.now().strftime("%A")}': 50
        }

    @pytest.mark.asyncio
    async def test_GFLA_empty_link(self, client, premium_user):
        response = await client.get(
            "/analytics/premium/summary", headers=premium_user["header"]
        )

        assert response.json()["full_distribution_by_click_counter"] == {}
        assert response.json()["full_distribution_by_week_days"] == {}

    @pytest.mark.asyncio
    async def test_GFLA_unauthorized(self, client):
        response = await client.get("/analytics/summary")

        assert response.status_code == 401


class TestGAFL:
    """Tests for /analytics/premium/{link_url} (get_method)
    GAFL - get_analytics_for_link
    """

    @pytest.mark.asyncio
    async def test_GAFL_success(
        self, sample_link_for_premium_user_analytics, client, premium_user
    ):
        response = await client.get(
            f"/analytics/premium/{sample_link_for_premium_user_analytics['url']}",
            headers=premium_user["header"],
        )

        json = response.json()
        assert sample_link_for_premium_user_analytics["url"] == json["url"]
        assert json["click_counter"] == 50
        assert json["distribution_by_week_days"] == {
            f'{datetime.now().strftime("%A")}': 50
        }

    @pytest.mark.asyncio
    async def test_GAFL_empty_link(self, client, premium_user, empty_link_premium_user):
        response = await client.get(
            f"/analytics/premium/{empty_link_premium_user['url']}",
            headers=premium_user["header"],
        )

        json = response.json()
        assert empty_link_premium_user["url"] == json["url"]
        assert json["click_counter"] == 0
        assert json["distribution_by_week_days"] == {}

    @pytest.mark.asyncio
    async def test_GAFL_unauthorized(
        self, client, sample_link_for_premium_user_analytics
    ):
        response = await client.get(
            f"/analytics/{sample_link_for_premium_user_analytics['url']}"
        )

        assert response.status_code == 401
