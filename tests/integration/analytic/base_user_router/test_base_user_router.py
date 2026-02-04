from datetime import datetime

import pytest


class TestGFLA:
    """Tests for /analytics/summary (get method)
    GFLA - get_full_links_analytics
    """

    @pytest.mark.asyncio
    async def test_GFLA_success(self, sample_link_for_analytics, client, admin_user):
        response = await client.get("/analytics/summary", headers=admin_user["header"])

        json = response.json()
        assert json["user_id"] == admin_user["data"]["id"]
        assert "aaaaa" in json["full_distribution_by_click_counter"]
        assert json["full_distribution_by_click_counter"]["aaaaa"] == 50
        assert json["full_distribution_by_week_days"] == {
            f'{datetime.now().strftime("%A")}': 50
        }

    @pytest.mark.asyncio
    async def test_GFLA_empty_link(self, client, empty_user):
        response = await client.get("/analytics/summary", headers=empty_user["header"])

        assert response.json()["user_id"] == empty_user["data"]["id"]
        assert response.json()["full_distribution_by_click_counter"] == {}
        assert response.json()["full_distribution_by_week_days"] == {}

    @pytest.mark.asyncio
    async def test_GFLA_unauthorized(self, client):
        response = await client.get("/analytics/summary")

        assert response.status_code == 401


class TestGAFL:
    """Tests for /analytics/{link_url} (get_method)
    GAFL - get_analytics_for_link
    """

    @pytest.mark.asyncio
    async def test_GAFL_success(self, sample_link_for_analytics, client, admin_user):
        response = await client.get(
            f"/analytics/{sample_link_for_analytics['url']}",
            headers=admin_user["header"],
        )

        json = response.json()
        assert sample_link_for_analytics["url"] == json["url"]
        assert json["click_counter"] == 50
        assert json["distribution_by_week_days"] == {
            f'{datetime.now().strftime("%A")}': 50
        }

    @pytest.mark.asyncio
    async def test_GAFL_empty_link(self, client, empty_user, empty_link):
        response = await client.get(
            f"/analytics/{empty_link['url']}", headers=empty_user["header"]
        )

        json = response.json()
        assert empty_link["url"] == json["url"]
        assert json["click_counter"] == 0
        assert json["distribution_by_week_days"] == {}

    @pytest.mark.asyncio
    async def test_GAFL_unauthorized(self, client, sample_link_for_analytics):
        response = await client.get(f"/analytics/{sample_link_for_analytics['url']}")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_GAFL_another_user(
        self, client, sample_link_for_analytics, empty_user
    ):
        response = await client.get(
            f"/analytics/{sample_link_for_analytics['url']}",
            headers=empty_user["header"],
        )
        assert response.status_code == 403

    @pytest.mark.parametrize("url", ["5252a", "uuuuu", "pepeW"])
    @pytest.mark.asyncio
    async def test_GAFL_not_found(self, client, admin_user, url):
        response = await client.get(f"/analytics/{url}", headers=admin_user["header"])

        assert response.status_code == 404

    @pytest.mark.parametrize(
        "url", [1, True, "aa", -1, "aaA", "AAAAAAAAAAAA", "a" * 256]
    )
    @pytest.mark.asyncio
    async def test_GAFL_bad_url(self, client, admin_user, url):
        response = await client.get(f"/analytics/{url}", headers=admin_user["header"])

        assert response.status_code == 422
