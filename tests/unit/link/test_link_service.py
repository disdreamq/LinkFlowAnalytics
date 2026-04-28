import datetime
from unittest.mock import MagicMock

import pytest

from src.core.exceptions.exceptions import PermissionDeniedException
from src.modules.click.schemas import SClickResponse
from src.modules.link.schemas import SLinkResponse, SLinkWithClicks


class TestLinkServiceCreate:
    """Tests for create"""

    @pytest.mark.asyncio
    async def test_create_success(
        self,
        mock_link_repo,
        link_service,
        sample_link_create,
        sample_link_data,
        mock_url_generator,
    ):
        mock_url_generator.get_url.return_value = sample_link_data["url"]
        mock_link_repo.create.return_value = MagicMock(**sample_link_data)

        result = await link_service.create(sample_link_create)

        assert isinstance(result, SLinkResponse)
        assert result.id == sample_link_data["id"]
        assert result.base_url == sample_link_data["base_url"]
        assert result.url == sample_link_data["url"]
        assert result.click_counter == 0


class TestLinkServiceGetByUrl:
    """Tests for get_by_url"""

    @pytest.mark.asyncio
    async def test_get_by_url_success(
        self,
        mock_link_repo,
        link_service,
        sample_link_data,
    ):
        mock_link_repo.get_by_url.return_value = MagicMock(**sample_link_data)

        result = await link_service.get_by_url(
            sample_link_data["user_id"], sample_link_data["url"]
        )

        assert isinstance(result, SLinkResponse)
        assert result.url == sample_link_data["url"]
        assert result.user_id == sample_link_data["user_id"]

    @pytest.mark.asyncio
    async def test_get_by_url_fail_dut_to_incorrect_user_id(
        self,
        link_service,
        sample_link_data,
    ):
        """Test for get_by_url that fails due to _verify_id returns False"""
        with pytest.raises(PermissionDeniedException):
            await link_service.get_by_url(52, sample_link_data["url"])


class TestLinkServiceGetWithClicks:
    """Tests for get_with_clicks"""

    @pytest.mark.asyncio
    async def test_get_with_clicks_success(
        self,
        mock_link_repo,
        link_service,
        sample_link_data,
    ):
        mock_link_repo.get_by_url.return_value = MagicMock(**sample_link_data)
        mock_link_repo.get_with_clicks.return_value = MagicMock(
            **sample_link_data,
            clicks=[
                SClickResponse(
                    id=1,
                    link_id=1,
                    user_ip=None,
                    user_agent="Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",  # noqa: E501
                    created_at=datetime.datetime.now(),
                ),
                SClickResponse(
                    id=2,
                    link_id=1,
                    user_ip=None,
                    user_agent="Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",  # noqa: E501
                    created_at=datetime.datetime.now(),
                ),
            ],
        )
        result = await link_service.get_with_clicks(
            sample_link_data["id"], sample_link_data["url"]
        )

        assert isinstance(result, SLinkWithClicks)
        assert isinstance(result.clicks[0], SClickResponse)
        assert isinstance(result.clicks[1], SClickResponse)
        assert result.clicks[0].id == 1
        assert result.clicks[0].link_id == 1
        assert result.clicks[1].id == 2
        assert result.clicks[1].link_id == 1
        assert result.id == sample_link_data["id"]
        assert result.user_id == sample_link_data["user_id"]
        assert result.base_url == sample_link_data["base_url"]
        assert result.url == sample_link_data["url"]

    @pytest.mark.asyncio
    async def test_get_with_clicks_success_empty_clicks(
        self,
        mock_link_repo,
        link_service,
        sample_link_data,
    ):
        mock_link_repo.get_by_url.return_value = MagicMock(**sample_link_data)
        mock_link_repo.get_with_clicks.return_value = MagicMock(**sample_link_data)
        result = await link_service.get_with_clicks(
            sample_link_data["id"], sample_link_data["url"]
        )

        assert isinstance(result, SLinkWithClicks)
        assert result.id == sample_link_data["id"]
        assert result.user_id == sample_link_data["user_id"]
        assert result.base_url == sample_link_data["base_url"]
        assert result.url == sample_link_data["url"]
        assert len(result.clicks) == 0


class TestLinkServiceUpdate:
    """Tests for update"""

    @pytest.mark.asyncio
    async def test_update_success(
        self,
        mock_link_repo,
        link_service,
        sample_link_update,
    ):
        mock_link_repo.get_by_url.return_value = MagicMock(
            **sample_link_update.model_dump()
        )
        mock_link_repo.update.return_value = MagicMock(
            **sample_link_update.model_dump()
        )

        result = await link_service.update(
            sample_link_update.user_id, sample_link_update
        )

        assert result.url == sample_link_update.url
        assert result.user_id == sample_link_update.user_id
        assert result.base_url == sample_link_update.base_url


class TestLinkServiceDelete:
    """Tests for delete"""

    @pytest.mark.asyncio
    async def test_delete_success(
        self,
        mock_link_repo,
        link_service,
        sample_link_data,
    ):
        mock_link_repo.get_by_url.return_value = MagicMock(**sample_link_data)
        mock_link_repo.delete.return_value = True

        result = await link_service.delete(
            sample_link_data["user_id"], sample_link_data["url"]
        )

        assert result


class TestLinkServiceIncrementClickCounters:
    """Tests for increment_click_counters"""

    @pytest.mark.asyncio
    async def test_increment_click_counters_success(
        self,
        mock_link_repo,
        link_service,
        sample_links_with_incremented_click_counter,
        sample_links_data_dict,
    ):
        mock_link_repo.increment_click_counters.return_value = [
            MagicMock(**sample_links_with_incremented_click_counter[0]),
            MagicMock(**sample_links_with_incremented_click_counter[1]),
            MagicMock(**sample_links_with_incremented_click_counter[2]),
        ]

        result = await link_service.increment_click_counters(sample_links_data_dict)

        assert len(result) == 3
        assert isinstance(result, list)
        assert isinstance(result[0], SLinkResponse)
        assert isinstance(result[1], SLinkResponse)
        assert result[0].click_counter == sample_links_data_dict[0]
        assert result[1].click_counter == sample_links_data_dict[1]
        assert (
            result[2].click_counter == sample_links_data_dict[2]
        )  # 0 here, nothing should change


class TestLinkServiceGetForRedirect:
    """Tests for get_for_redirect"""

    @pytest.mark.asyncio
    async def test_get_for_redirect_not_cached_success(
        self, mock_link_repo, link_service, sample_link_data, cache
    ):
        mock_link_repo.get_by_url.return_value = MagicMock(**sample_link_data)

        result = await link_service.get_for_redirect(sample_link_data["url"])

        assert isinstance(result, SLinkResponse)
        assert result.url == sample_link_data["url"]
        assert await cache.exists(f"link_url_{sample_link_data['url']}")

    @pytest.mark.asyncio
    async def test_get_for_redirect_cached_success(
        self, mock_link_repo, link_service, sample_link_data
    ):
        mock_link_repo.get_by_url.return_value = MagicMock(**sample_link_data)
        await link_service.get_for_redirect(sample_link_data["url"])
        result = await link_service.get_for_redirect(sample_link_data["url"])

        assert isinstance(result, SLinkResponse)
        assert result.url == sample_link_data["url"]
