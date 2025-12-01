from datetime import datetime
from typing import TYPE_CHECKING
from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from src.entities.link.schemas import SLinkResponse


class SClickCreate(BaseModel):
    link_id: int
    user_agent: str
    region: str


class SClickGet(SClickCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class SClickWithLink(SClickGet):
    link: SLinkResponse
