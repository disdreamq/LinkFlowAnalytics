import logging
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    # Logging
    log_level: str = ""
    log_format: str = ""

    # PostgreSQL
    postgres_db: str = ""
    postgres_host: str = ""
    postgres_port: int = 0
    postgres_user: str = ""
    postgres_password: str = ""

    @property
    def db_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    # Redis
    redis_database: int = 0
    redis_host: str = ""
    redis_port: int = 0
    redis_username: str = ""
    redis_password: str = ""

    @property
    def redis_url(self) -> str:
        return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_database}"

    # Auth
    secret_key: str = ""
    alghoritm: str = ""

    # CORS
    CORS_ORIGINS: list[str] = []

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
