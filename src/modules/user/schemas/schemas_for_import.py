from datetime import datetime
from pydantic import BaseModel, ConfigDict

from src.enums.enums import UserTarifPlan


class ImportedSUserInDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    password: str
    tarifplan: UserTarifPlan
    created_at: datetime
    updated_at: datetime
