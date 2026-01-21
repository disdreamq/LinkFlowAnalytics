import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.cache.local_memory.repositories.repository import LocalMemoryRepository
from src.modules.link.schemas import SLinkCreateDTO, SLinkUpdate
from src.modules.link.service.service import LinkService


@pytest.fixture
def cache():
    return LocalMemoryRepository()


@pytest.fixture()
def mock_link_repo():
    repo = MagicMock()

    repo.create = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.get_by_url = AsyncMock()
    repo.get_with_clicks = AsyncMock()
    repo.get_multiple_links_by_urls = AsyncMock()
    repo.get_multiple_links_by_ids = AsyncMock()
    repo.update = AsyncMock()
    repo.increment_click_counters = AsyncMock()
    repo.delete = AsyncMock()

    return repo


@pytest.fixture()
def mock_url_generator():
    url_generator = MagicMock()
    url_generator.get_url = AsyncMock()
    return url_generator


@pytest.fixture()
def link_service(mock_link_repo, cache, mock_url_generator):
    return LinkService(
        repo=mock_link_repo, cache=cache, url_generator=mock_url_generator
    )


@pytest.fixture(scope="session")
def sample_link_data():
    return {
        "id": 1,
        "user_id": 1,
        "base_url": "https://www.example.com/",
        "url": "aaaaa",
        "click_counter": 0,
        "created_at": datetime.datetime.now(),
        "updated_at": datetime.datetime.now(),
    }


@pytest.fixture(scope="session")
def sample_link_create(sample_link_data):
    return SLinkCreateDTO(
        user_id=sample_link_data["user_id"], base_url=sample_link_data["base_url"]
    )


@pytest.fixture(scope="session")
def sample_link_update(sample_link_data):
    return SLinkUpdate(
        user_id=sample_link_data["user_id"],
        url="baaaa",
        base_url="https://www.pisyatdva.com/",
    )


@pytest.fixture(scope="session")
def sample_links_data_dict():
    return {
        0: 5,
        1: 10,
        2: 0,
    }
@pytest.fixture(scope="session")
def sample_links_with_incremented_click_counter(sample_link_data):
    first_link = sample_link_data.copy()
    first_link['click_counter'] = 5
    second_link = sample_link_data.copy()
    second_link['click_counter'] = 10
    third_link = sample_link_data.copy()
    third_link["click_counter"] = 0
    return first_link, second_link, third_link
