import pytest

from src.cache.local_memory.repositories.repository import LocalMemoryRepository
from src.modules.link.service.url_generator import URLGenerator


@pytest.fixture
def cache():
    return LocalMemoryRepository()


@pytest.fixture()
def url_generator(cache):
    return URLGenerator(cache=cache)


@pytest.fixture(autouse=True)
async def cleanup_cache_between_tests(cache):
    await cache.clear_all()
    yield
    await cache.clear_all()
