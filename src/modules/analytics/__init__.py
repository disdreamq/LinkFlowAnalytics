from fastapi import APIRouter

from .base_user.router import router as base_user_router
from .premium_user.router import router as premium_user_router

router = APIRouter()
router.include_router(base_user_router)
router.include_router(premium_user_router)