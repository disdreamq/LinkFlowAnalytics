from typing import Annotated

from fastapi.params import Depends

from src.core.exception_factory import exception_factory
from src.enums.enums import UserTarifPlan
from src.modules.auth.dependencies import require_auth
from modules.user.schemas import SUserInDB


async def require_premimum_tarifplan(
    current_user: Annotated[SUserInDB, Depends(require_auth)],
):
    if current_user.tarifplan != UserTarifPlan.Premium:
        raise exception_factory.premission_denaied(current_user.id)
