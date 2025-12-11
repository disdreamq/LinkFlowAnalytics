from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.core.config import get_settings

engine = create_async_engine(
    get_settings().db_url,
    echo=False,
    future=True,
    pool_size=20,
    max_overflow=30,
)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)
