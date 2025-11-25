from pydantic import BaseModel

from app.enums.enums import UserTarifPlan
from app.src.link.models import Link

class SUserCreate(BaseModel):
    email: str #emailvalidator
    password: str
    
class SUserGet(SUserCreate):
    id: int
    tarifplan: UserTarifPlan
    links: list[Link]
    
class SUserUpdate(SUserGet):
    pass