import datetime

import pytest

from src.core.exceptions.exceptions import BusinessLogicException
from src.modules.click.schemas import SClickCreate, SClickResponse
from src.modules.click.service.click_buffer import ClickBuffer


class TestClickBufferAddClick:
    """Tests for add_click"""

    @pytest.mark.asyncio
    async def test_add_click_success(self, click_buffer, sample_click_create, cache):
        await click_buffer.add_click(sample_click_create)
        await click_buffer.add_click(sample_click_create)
        cached_clicks = await cache.get_arr("buffered_clicks")
        clicks = [SClickCreate.model_validate_json(click) for click in cached_clicks]
        assert len(clicks) == 2
        assert click_buffer.counter == 2

    @pytest.mark.asyncio
    async def test_add_click_fail(
        self, click_buffer_with_fake_cache, sample_click_create, fake_cache
    ):
        """Test for situation, when click did not cached"""

        fake_cache.get.return_value = None
        fake_cache.add_to_arr.side_effect = BusinessLogicException("")
        with pytest.raises(BusinessLogicException):
            await click_buffer_with_fake_cache.add_click(sample_click_create)

        assert click_buffer_with_fake_cache.counter == 0

    @pytest.mark.parametrize(
        "number_of_clicks",
        [1, 2, 5, 9],
    )
    @pytest.mark.asyncio
    async def test_add_click_many_params(
        self, click_buffer, sample_click_create, cache, number_of_clicks
    ):
        for _ in range(number_of_clicks):
            await click_buffer.add_click(sample_click_create)
        cached_clicks = await cache.get_arr("buffered_clicks")
        clicks = [SClickCreate.model_validate_json(click) for click in cached_clicks]
        assert len(clicks) == number_of_clicks
        assert click_buffer.counter == number_of_clicks

    @pytest.mark.asyncio
    async def test_add_click_recovery_from_cache(
        self,
        click_buffer,
        sample_click_create,
        mock_link_service,
        mock_click_service,
        cache,
    ):
        """Test for recorevy after shut down"""
        await click_buffer.add_click(sample_click_create)
        del click_buffer
        click_buffer = ClickBuffer(mock_click_service, mock_link_service, cache)
        await click_buffer.add_click(sample_click_create)

        cached_clicks = await cache.get_arr("buffered_clicks")
        clicks = [SClickCreate.model_validate_json(click) for click in cached_clicks]

        assert len(clicks) == 2
        assert click_buffer.counter == 2


class TestClickBufferWriteBufferToDB:
    """Tests for adding clicks in db from buffer"""

    @pytest.mark.asyncio
    async def test_write_buffer_to_db(
        self,
        click_buffer,
        sample_alot_of_clicks,
        cache,
        mock_click_service,
        mock_link_service,
    ):
        """Test for addint clicks to db from buffer, when counter is 10,
        it should write clicks to db form buffer"""

        mock_click_service.create.return_value = [
            SClickResponse(**click) for click in sample_alot_of_clicks
        ]
        mock_link_service.increment_click_counters.return_value = [
            SClickResponse(**click) for click in sample_alot_of_clicks
        ]

        for click in sample_alot_of_clicks:
            await click_buffer.add_click(SClickCreate(**click))

        cached_clicks = await cache.get_arr("buffered_clicks")
        clicks = [SClickCreate.model_validate_json(click) for click in cached_clicks]
        assert len(clicks) == 0
        assert click_buffer.counter == 0


class TestGetIncrementsForLinks:
    """Tests for _get_increments_for_links helper function"""

    def test_get_increments_for_links_single_link(
        self,
        click_buffer,
        sample_alot_of_clicks,
    ):
        """Test with clicks for single link"""

        clicks = [SClickResponse(**sample_alot_of_clicks[i]) for i in range(5)]

        result = click_buffer._get_increments_for_links(clicks)

        assert result == {1: 5}

    def test_get_increments_for_links_multiple_links(
        self,
        click_buffer,
    ):
        """Test with clicks for multiple links"""
        clicks = [
            SClickResponse(
                **{
                    "id": i,
                    "link_id": i,
                    "user_agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
                    "user_ip": None,
                    "created_at": datetime.datetime.now(),
                }
            )
            for i in range(1, 5)
        ]
        result = click_buffer._get_increments_for_links(clicks)

        assert result == {1: 1, 2: 1, 3: 1, 4: 1}

    def test_get_increments_for_links_empty_list(
        self,
        click_buffer,
    ):
        """Test with empty clicks list"""

        result = click_buffer._get_increments_for_links([])

        assert result == {}


class TestClickBufferEdgeCases:
    """Tests for edge cases"""

    @pytest.mark.asyncio
    async def test_add_click_with_max_length_zero(
        self, click_buffer, sample_click_create
    ):
        """Test behavior when max_length is 0 (should write immediately)"""
        click_buffer.max_lenght = 0

        await click_buffer.add_click(sample_click_create)

        assert click_buffer.counter == 0
