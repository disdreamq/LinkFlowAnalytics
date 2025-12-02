from datetime import datetime
from typing import TYPE_CHECKING, Optional
from pydantic import BaseModel, ConfigDict

from src.enums.enums import UserTarifPlan

if TYPE_CHECKING:
    from src.modules.link.schemas import SLinkResponse


class SUserCreate(BaseModel):
    email: str  # emailvalidator
    password: str


class SUserResponse(SUserCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tarifplan: UserTarifPlan
    created_at: datetime
    updated_at: datetime


class SUserResponseWithLinks(SUserResponse):
    links: list["SLinkResponse"] = []


class SUserUpdate(SUserCreate):
    email: Optional[str] = None
    password: Optional[str] = None
    tarifplan: Optional[UserTarifPlan] = None
