from datetime import datetime
from typing import TYPE_CHECKING, Optional
from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from src.modules.link.schemas import SLinkResponse


class SClickCreate(BaseModel):
    link_id: int
    user_agent: str
    user_ip: Optional[str]
    created_at: datetime


class SClickInDB(SClickCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class SClickInDBWithLink(SClickInDB):
    link: "SLinkResponse"
