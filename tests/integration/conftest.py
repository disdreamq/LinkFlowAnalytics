import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from main import app
from src.db.base import Base
from src.modules.dependencies import get_session
from tests.integration.dependencies import DependencyOverrides

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(url=TEST_DATABASE_URL)

TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        yield
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
async def db_session():
    async with TestingSessionLocal() as session, session.begin():
        yield session


@pytest.fixture(scope="function", autouse=True)
async def get_client():
    ac = AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    )
    return ac


@pytest.fixture()
async def deps():
    overrides = DependencyOverrides(app)
    yield overrides
    overrides.clear()


@pytest.fixture()
async def client(deps, db_session):
    async def override_get_session():
        yield db_session

    deps.set(get_session, override_get_session)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver", timeout=30.0
    ) as ac:
        yield ac
    deps.clear()


@pytest.fixture()
def sample_user_register_data():
    user_data = {
        "email": "test@example.com",
        "password": "password123",
    }
    return user_data
