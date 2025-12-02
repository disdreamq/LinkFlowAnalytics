from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn
from src.modules import router

import src.db.init_models # noqa


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["src", "main.py"],
    )
