import uvicorn
from fastapi import FastAPI

import src.db.init_models  # noqa
from src.modules import router

app = FastAPI()
app.include_router(router)

def main():
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["src", "main.py"],
    )


if __name__ == "__main__":
    main()
