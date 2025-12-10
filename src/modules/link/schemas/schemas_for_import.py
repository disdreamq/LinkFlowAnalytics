from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ImportedSLinkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    base_url: str
    url: str
    click_counter: int
    created_at: datetime
    updated_at: datetime
    