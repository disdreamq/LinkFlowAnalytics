import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.cache.local_memory.repositories.repository import LocalMemoryRepository
from src.modules.click.schemas import SClickCreate
from src.modules.click.service.click_buffer import ClickBuffer


@pytest.fixture
def cache():
    return LocalMemoryRepository()


@pytest.fixture
def fake_cache():
    cache = MagicMock()

    cache.add_to_arr = AsyncMock()
    cache.get = AsyncMock()
    cache.get_arr = AsyncMock()
    cache.delete = AsyncMock()
    cache.set_ = AsyncMock()

    return cache


@pytest.fixture
def mock_click_service():
    service = MagicMock()

    service.create = AsyncMock()
    return service


@pytest.fixture
def mock_link_service():
    service = MagicMock()

    service.increment_click_counters = AsyncMock()
    return service


@pytest.fixture
def click_buffer(mock_click_service, mock_link_service, cache):
    return ClickBuffer(mock_click_service, mock_link_service, cache)


@pytest.fixture
def click_buffer_with_fake_cache(mock_click_service, mock_link_service, fake_cache):
    return ClickBuffer(mock_click_service, mock_link_service, fake_cache)


@pytest.fixture
def sample_click_data():
    return {
        "id": 1,
        "link_id": 1,
        "user_agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",  # noqa: E501
        "user_ip": None,
        "created_at": datetime.datetime.now(),
    }


@pytest.fixture
def sample_click_create(sample_click_data):
    return SClickCreate(
        link_id=sample_click_data["link_id"],
        user_agent=sample_click_data["user_agent"],
        user_ip=sample_click_data["user_ip"],
        created_at=sample_click_data["created_at"],
    )


@pytest.fixture(scope="function", autouse=True)
async def cleanup_cache_between_tests(cache):
    await cache.clear_all()
    yield
    await cache.clear_all()
