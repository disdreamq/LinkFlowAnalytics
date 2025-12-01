from datetime import datetime
from typing import TYPE_CHECKING
from pydantic import BaseModel, ConfigDict, HttpUrl

if TYPE_CHECKING:
    from src.entities.click.schemas import SClickGet
    from src.entities.user.schemas import SUserGet


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
    user: "SUserGet"


class SLinkWithClicks(SLinkResponse):
    clicks: list["SClickGet"] = []


class SLinkFull(SLinkResponse):
    user: "SUserGet"
    clicks: list["SClickGet"] = []
