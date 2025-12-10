from fastapi import APIRouter

from .analytics import router as analytics_router
from .auth.router import router as auth_router
from .click.models import Click
from .link.models import Link
from .link.redirect_router import router as link_redirect_router
from .link.router import router as link_router
from .user.models import User
from .user.router import router as user_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(link_router)
router.include_router(user_router)
router.include_router(link_redirect_router)
router.include_router(analytics_router)

__all__ = ["User", "Link", "Click"] # noqa
