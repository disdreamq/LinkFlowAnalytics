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
        assert click_buffer.counter == number_of_clicks
        cached_clicks = await cache.get_arr("buffered_clicks")
        assert cached_clicks is not None
        assert len(cached_clicks) == number_of_clicks

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

    @pytest.mark.asyncio
    async def test_add_click_initializes_from_cache_counter(
        self,
        mock_click_service,
        mock_link_service,
        cache,
        sample_click_create,
    ):
        """Test that buffer initializes counter from cache on first add_click"""
        await cache.set_("buffer_counter", "5")
        await cache.add_to_arr("buffered_clicks", sample_click_create.model_dump_json())

        click_buffer = ClickBuffer(
            mock_click_service, mock_link_service, cache, max_lenght=10
        )
        await click_buffer.add_click(sample_click_create)

        assert click_buffer.counter == 6
        assert click_buffer.ready is True

    @pytest.mark.asyncio
    async def test_add_click_does_not_reinitialize_when_ready(
        self,
        mock_click_service,
        mock_link_service,
        cache,
        sample_click_create,
    ):
        """Test that _initialize is not called when buffer is already ready"""
        click_buffer = ClickBuffer(
            mock_click_service, mock_link_service, cache, max_lenght=10
        )
        await click_buffer.add_click(sample_click_create)
        first_counter = click_buffer.counter

        await click_buffer.add_click(sample_click_create)

        assert click_buffer.counter == first_counter + 1


class TestClickBufferWriteBufferToDB:
    """Tests for adding clicks in db from buffer"""

    @pytest.mark.asyncio
    async def test_write_buffer_to_db(
        self,
        click_buffer,
        sample_click_create,
        cache,
        mock_click_service,
        mock_link_service,
    ):
        """Test for adding clicks to db from buffer, when counter is 10,
        it should write clicks to db from buffer"""

        mock_click_service.create.return_value = [
            SClickResponse(
                id=i,
                link_id=1,
                user_agent="Mozilla/5.0",
                user_ip=None,
                created_at=datetime.datetime.now(),
            )
            for i in range(1, 11)
        ]
        mock_link_service.increment_click_counters.return_value = []

        for _ in range(10):
            await click_buffer.add_click(sample_click_create)

        cached_clicks = await cache.get_arr("buffered_clicks")
        assert cached_clicks is None or len(cached_clicks) == 0
        assert click_buffer.counter == 0

    @pytest.mark.asyncio
    async def test_write_buffer_to_db_clears_cache(
        self,
        click_buffer,
        sample_click_create,
        cache,
        mock_click_service,
        mock_link_service,
    ):
        """Test that buffer clears cache after writing to db"""
        mock_click_service.create.return_value = [
            SClickResponse(
                id=1,
                link_id=1,
                user_agent="Mozilla/5.0",
                user_ip=None,
                created_at=datetime.datetime.now(),
            )
        ]
        mock_link_service.increment_click_counters.return_value = []

        for _ in range(10):
            await click_buffer.add_click(sample_click_create)

        buffered_clicks = await cache.get_arr("buffered_clicks")
        assert buffered_clicks is None or len(buffered_clicks) == 0

        buffer_counter = await cache.get("buffer_counter")
        assert buffer_counter == "0" or buffer_counter is None

    @pytest.mark.asyncio
    async def test_write_buffer_to_db_calls_click_service_create(
        self,
        click_buffer,
        sample_click_data,
        mock_click_service,
        mock_link_service,
    ):
        """Test that click_service.create is called with correct clicks"""
        expected_clicks = [SClickCreate(**sample_click_data) for _ in range(10)]
        mock_click_service.create.return_value = [
            SClickResponse(
                id=i,
                link_id=1,
                user_agent="Mozilla/5.0",
                user_ip=None,
                created_at=datetime.datetime.now(),
            )
            for i in range(1, 11)
        ]
        mock_link_service.increment_click_counters.return_value = []

        for click in expected_clicks:
            await click_buffer.add_click(click)

        mock_click_service.create.assert_called_once()
        call_args = mock_click_service.create.call_args[0][0]
        assert len(call_args) == 10
        assert all(isinstance(c, SClickCreate) for c in call_args)

    @pytest.mark.asyncio
    async def test_write_buffer_to_db_calls_increment_click_counters(
        self,
        click_buffer,
        sample_click_data,
        mock_click_service,
        mock_link_service,
    ):
        """Test that link_service.increment_click_counters is called with correct dict"""  # noqa: E501
        expected_clicks = [SClickCreate(**sample_click_data) for _ in range(10)]
        mock_click_service.create.return_value = [
            SClickResponse(
                id=i,
                link_id=1,
                user_agent="Mozilla/5.0",
                user_ip=None,
                created_at=datetime.datetime.now(),
            )
            for i in range(1, 11)
        ]
        mock_link_service.increment_click_counters.return_value = []

        for click in expected_clicks:
            await click_buffer.add_click(click)

        mock_link_service.increment_click_counters.assert_called_once()
        call_args = mock_link_service.increment_click_counters.call_args[0][0]
        assert call_args == {1: 10}


class TestGetIncrementsForLinks:
    """Tests for _get_increments_for_links helper function"""

    def test_get_increments_for_links_single_link(
        self,
        click_buffer,
    ):
        """Test with clicks for single link"""

        clicks = [
            SClickResponse(
                id=i,
                link_id=1,
                user_agent="Mozilla/5.0",
                user_ip=None,
                created_at=datetime.datetime.now(),
            )
            for i in range(1, 6)
        ]

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
                    "user_agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",  # noqa: E501
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

    def test_get_increments_for_links_mixed_link_ids(
        self,
        click_buffer,
    ):
        """Test with clicks having mixed link_ids"""
        clicks = [
            SClickResponse(
                **{
                    "id": i,
                    "link_id": i % 3 + 1,
                    "user_agent": "Mozilla/5.0",
                    "user_ip": None,
                    "created_at": datetime.datetime.now(),
                }
            )
            for i in range(6)
        ]
        result = click_buffer._get_increments_for_links(clicks)

        assert result == {1: 2, 2: 2, 3: 2}


class TestClickBufferEdgeCases:
    """Tests for edge cases"""

    @pytest.mark.asyncio
    async def test_add_click_with_max_length_zero(
        self,
        click_buffer,
        sample_click_create,
        mock_click_service,
        mock_link_service,
    ):
        """Test behavior when max_length is 0 (should write immediately)"""
        mock_click_service.create.return_value = [
            SClickResponse(id=1, **sample_click_create.model_dump())
        ]
        mock_link_service.increment_click_counters.return_value = []

        click_buffer.max_lenght = 0
        await click_buffer.add_click(sample_click_create)

        assert click_buffer.counter == 0
        mock_click_service.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_click_with_max_length_one(
        self,
        click_buffer,
        sample_click_create,
        mock_click_service,
        mock_link_service,
    ):
        """Test behavior when max_length is 1 (should write after each click)"""
        mock_click_service.create.return_value = [
            SClickResponse(id=1, **sample_click_create.model_dump())
        ]
        mock_link_service.increment_click_counters.return_value = []

        click_buffer.max_lenght = 1
        await click_buffer.add_click(sample_click_create)

        assert click_buffer.counter == 0
        mock_click_service.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_click_business_logic_exception_on_zero_return(
        self,
        click_buffer_with_fake_cache,
        sample_click_create,
        fake_cache,
    ):
        """Test that BusinessLogicException is raised when add_to_arr returns 0"""
        fake_cache.get.return_value = None
        fake_cache.add_to_arr.return_value = 0

        with pytest.raises(BusinessLogicException) as exc_info:
            await click_buffer_with_fake_cache.add_click(sample_click_create)

        assert "Error while addint click to redis buffer" in str(exc_info.value.message)
        assert click_buffer_with_fake_cache.counter == 0
