from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn
from src.entities.link.router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
