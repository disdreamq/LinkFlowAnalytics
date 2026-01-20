import datetime
from unittest.mock import MagicMock

import pytest

from src.cache.local_memory.repositories.repository import in_memory_cache
from src.core.exceptions.exceptions import PremissonDenaiedException
from src.modules.click.schemas import SClickResponse
from src.modules.link.schemas import SLinkResponse, SLinkWithClicksResponse


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
        assert await in_memory_cache.exists(f'link_url_{sample_link_data["url"]}')

    @pytest.mark.asyncio
    async def test_get_by_url_fail_dut_to_incorrect_user_id(
        self,
        link_service,
        sample_link_data,
    ):
        """Test for get_by_url that fails due to _verify_id returns False"""
        with pytest.raises(PremissonDenaiedException):
            await link_service.get_by_url(52, sample_link_data["url"])


class TestLinkServiceGetWithClicks:
    """Tests for get_with_clicks"""

    @pytest.mark.asyncio
    async def test_get_by_url_success(
        self,
        mock_link_repo,
        link_service,
        sample_link_data,
    ):
        mock_link_repo.get_by_url.return_value = MagicMock(**sample_link_data)
        mock_link_repo.get_with_clicks.return_value = MagicMock(
            **sample_link_data,
            links=[
                SClickResponse(
                    id=1,
                    link_id=1,
                    user_ip=None,
                    user_agent="Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
                    created_at=datetime.datetime.now(),
                ),
                SClickResponse(
                    id=2,
                    link_id=1,
                    user_ip=None,
                    user_agent="Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
                    created_at=datetime.datetime.now(),
                ),
            ],
        )
        result = await link_service.get_with_clicks(
            sample_link_data["id"], sample_link_data["url"]
        )

        assert isinstance(result, SLinkWithClicksResponse)
