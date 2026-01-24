from typing import Annotated

from fastapi.params import Depends

from src.core.exceptions.exceptions import PremissonDenaiedException
from src.enums.enums import UserTarifPlan
from src.modules.analytics.premium_user.service import PremiumUserAnalyticService
from src.modules.auth.dependencies import require_auth
from src.modules.link.dependencies import get_link_service
from src.modules.link.service.service import LinkService
from src.modules.user.dependencies import get_user_service
from src.modules.user.schemas import SUserInDB
from src.modules.user.service import UserService


async def require_premimum_tarifplan(
    current_user: Annotated[SUserInDB, Depends(require_auth)],
):
    if current_user.tarifplan != UserTarifPlan.Premium:
        raise PremissonDenaiedException(
            f"User with user id {current_user.id} doest not match required tarif plan"
        )


async def get_premium_user_analytic_service(
    link_service: Annotated[LinkService, Depends(get_link_service)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> PremiumUserAnalyticService:
    return PremiumUserAnalyticService(link_service, user_service)
