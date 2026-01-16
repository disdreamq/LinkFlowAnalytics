import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from main import app
from src.db.base import Base
from src.db.session import engine


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        yield
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def get_client() -> AsyncClient:
    ac = AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    )
    return ac
