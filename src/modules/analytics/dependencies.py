from typing import Annotated

from fastapi.params import Depends

from src.modules.analytics.base_user.service import BaseUserAnalyticService
from src.modules.link.dependencies import get_link_service
from src.modules.link.service.service import LinkService
from src.modules.user.dependencies import get_user_service
from src.modules.user.service import UserService


async def get_base_user_analytics_service(
    link_service: Annotated[LinkService, Depends(get_link_service)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> BaseUserAnalyticService:
    return BaseUserAnalyticService(link_service, user_service)
