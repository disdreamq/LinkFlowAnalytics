from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from src.modules.link.schemas.schemas_for_import import ImportedSLinkResponse

class SClickCreate(BaseModel):
    link_id: int
    user_agent: str
    user_ip: Optional[str]
    created_at: datetime


class SClickInDB(SClickCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class SClickInDBWithLink(SClickInDB):
    link: ImportedSLinkResponse
