from typing import Annotated
from fastapi.params import Depends
from src.core.exception_factory import exception_factory
from src.enums.enums import UserTarifPlan
from src.modules.auth.service import get_current_user
from src.modules.user.schemas import SUserInDB


async def required_premimum_tarifplan(
    current_user: Annotated[SUserInDB, Depends(get_current_user)],
):
    if current_user.tarifplan != UserTarifPlan.Premium:
        raise exception_factory.premission_denaied(current_user.id)
