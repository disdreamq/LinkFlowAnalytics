from datetime import datetime
from typing import TYPE_CHECKING
from pydantic import BaseModel, ConfigDict, HttpUrl

if TYPE_CHECKING:
    from src.modules.click.schemas import SClickResponse
    from src.modules.user.schemas import SUserInDB


class SLinkCreate(BaseModel):
    user_id: int
    base_url: HttpUrl


class SLinkResponse(SLinkCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    base_url: str
    url: str
    created_at: datetime
    updated_at: datetime


class SLinkWithUser(SLinkResponse):
    user: "SUserInDB"


class SLinkWithClicks(SLinkResponse):
    clicks: list["SClickResponse"] = []


class SLinkFull(SLinkResponse):
    user: "SUserInDB"
    clicks: list["SClickResponse"] = []
