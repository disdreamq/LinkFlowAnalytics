import uvicorn
from fastapi import FastAPI

from src.modules import router
import src.db.init_models  # noqa


def main():
    app = FastAPI()
    app.include_router(router)
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["src", "main.py"],
    )


if __name__ == "__main__":
    main()
