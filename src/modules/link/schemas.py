from datetime import datetime
from typing import TYPE_CHECKING
from pydantic import BaseModel, ConfigDict, HttpUrl

if TYPE_CHECKING:
    from src.modules.click.schemas import SClickInDB
    from src.modules.user.schemas import SUserInDB


class SLinkCreate(BaseModel):
    base_url: HttpUrl


class SLinkCreateInDB(SLinkCreate):
    user_id: int


class SLinkResponse(SLinkCreateInDB):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    base_url: str
    url: str
    click_counter: int
    created_at: datetime
    updated_at: datetime


class SLinkWithUser(SLinkResponse):
    user: "SUserInDB"


class SLinkWithClicks(SLinkResponse):
    clicks: list["SClickInDB"] = []


class SLinkFull(SLinkResponse):
    user: "SUserInDB"
    clicks: list["SClickInDB"] = []

SLinkWithClicks.model_rebuild()
SLinkFull.model_rebuild()