from contextlib import asynccontextmanager
from fastapi import FastAPI
from alembic.config import Config
from alembic import command

def run_migrations():
    """
    Автоматический запуск миграций, не для прода.
    """
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

@asynccontextmanager
async def lifespan(app: FastAPI):
    run_migrations()
    yield

app = FastAPI(lifespan=lifespan)
