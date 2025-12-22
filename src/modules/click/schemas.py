from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SClickCreate(BaseModel):
    link_id: int
    user_agent: str
    user_ip: str | None
    created_at: datetime


class SClickResponse(SClickCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
