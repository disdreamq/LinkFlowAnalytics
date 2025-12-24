from typing import Annotated

from fastapi.params import Depends

from src.core.exceptions.exceptions import PremissonDenaiedException
from src.enums.enums import UserTarifPlan
from src.modules.auth.dependencies import require_auth
from src.modules.user.schemas import SUserInDB


async def require_premimum_tarifplan(
    current_user: Annotated[SUserInDB, Depends(require_auth)],
):
    if current_user.tarifplan != UserTarifPlan.Premium:
        raise PremissonDenaiedException(
            f"User with user id {current_user.id} doest not match required tarif plan"
        )
