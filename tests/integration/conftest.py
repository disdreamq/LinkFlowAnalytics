from unittest.mock import MagicMock

import fakeredis
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from main import app
from src.cache.redis.connection import RedisConnectionManager
from src.cache.redis.repositories.repository import RedisRepository, get_redis
from src.db.base import Base
from src.modules.dependencies import get_session
from tests.integration.dependencies import DependencyOverrides

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(url=TEST_DATABASE_URL)

TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        yield
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture()
async def db_session():
    async with TestingSessionLocal() as session, session.begin():
        yield session
        await session.commit()


@pytest.fixture
def fake_redis_client():
    client = fakeredis.FakeStrictRedis(decode_responses=True, encoding="utf-8")

    client.set("test:key", "test_value")

    return client


@pytest.fixture
def redis_repository_mock(fake_redis_client):
    """Mocking RedisRepository"""
    mock_manager = MagicMock(spec=RedisConnectionManager)

    mock_manager.client = fake_redis_client

    repo = RedisRepository(mock_manager)

    return repo


@pytest.fixture()
async def deps():
    overrides = DependencyOverrides(app)
    yield overrides
    overrides.clear()


@pytest.fixture()
async def client(deps, db_session):
    async def override_get_session():
        yield db_session

    async def override_get_redis():
        return redis_repository_mock

    deps.set(get_session, override_get_session)
    deps.set(get_redis, override_get_redis)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver", timeout=30.0
    ) as ac:
        yield ac
    deps.clear()
