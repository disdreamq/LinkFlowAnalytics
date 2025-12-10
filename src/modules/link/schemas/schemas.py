from datetime import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl

from src.modules.click.schemas.schemas_for_import import ImportedSClickInDB
from src.modules.user.schemas.schemas_for_import import ImportedSUserInDB


class SLinkCreate(BaseModel):
    base_url: HttpUrl


class SLinkCreateInDB(SLinkCreate):
    user_id: int


class SLinkResponse(SLinkCreateInDB):
    model_config = ConfigDict(from_attributes=True)

    id: int
    base_url: str
    url: str
    click_counter: int
    created_at: datetime
    updated_at: datetime


class SLinkWithUser(SLinkResponse):
    user: ImportedSUserInDB


class SLinkWithClicks(SLinkResponse):
    clicks: list[ImportedSClickInDB] = []


class SLinkFull(SLinkResponse):
    user: ImportedSUserInDB
    clicks: list[ImportedSClickInDB] = []
