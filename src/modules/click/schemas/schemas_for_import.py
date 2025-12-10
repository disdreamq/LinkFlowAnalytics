from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class ImportedSClickInDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    link_id: int
    user_agent: str
    user_ip: Optional[str]
    created_at: datetime
