from fastapi import APIRouter
from .link.router import router as link_router
from .user.router import router as user_router

router = APIRouter()

router.include_router(link_router)
router.include_router(user_router)
