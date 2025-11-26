from datetime import datetime
from typing import TYPE_CHECKING
from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from src.entities.click.schemas import SClickGet
    from src.entities.user.schemas import SUserGet


class SLinkCreate(BaseModel):
    user_id: int
    base_url: str
    url: str


class SLinkGet(SLinkCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class SLinkWithUser(SLinkGet):
    user: SUserGet


class SLinkWithClicks(SLinkGet):
    clicks: list[SClickGet] = []


class SLinkFull(SLinkGet):
    user: SUserGet
    clicks: list[SClickGet] = []
