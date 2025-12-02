from fastapi import APIRouter
from .modules.link.router import router as link_router
from .modules.user.router import router as user_router

router = APIRouter()

router.include_router(link_router)
router.include_router(user_router)

from .modules.user.models import User
from .modules.link.models import Link
from .modules.click.models import Click

__all__ = ["User", "Link", "Click"]
