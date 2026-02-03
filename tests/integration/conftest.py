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


@pytest.fixture(scope="module", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        yield
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session():
    async with TestingSessionLocal() as session, session.begin():
        yield session
        await session.commit()


@pytest.fixture
async def redis_session():
    get_redis = RedisRepository(RedisConnectionManager(1))
    yield get_redis


@pytest.fixture()
async def deps():
    overrides = DependencyOverrides(app)
    yield overrides
    overrides.clear()


@pytest.fixture()
async def client(deps, db_session, redis_session):
    async def override_get_session():
        yield db_session

    async def override_get_redis():
        return redis_session

    deps.set(get_session, override_get_session)
    deps.set(get_redis, override_get_redis)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver", timeout=30.0
    ) as ac:
        yield ac


@pytest.fixture(autouse=True)
async def register_admin_user(client):
    admin_data = {"email": "admin@example.com", "password": "adminadmin"}
    await client.post(
        "/users/",
        json=admin_data,
    )


@pytest.fixture()
async def admin_user(client):
    admin_data = {"email": "admin@example.com", "password": "adminadmin"}
    response = await client.post(
        "/token",
        data={"username": admin_data["email"], "password": admin_data["password"]},
    )
    token = response.json()["access_token"]
    header = {"Authorization": f"Bearer {token}"}
    resp = await client.get("users/1", headers=header)
    return {"data": resp.json(), "header": header}
