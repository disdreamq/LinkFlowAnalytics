from pydantic import BaseModel

from app.enums.enums import UserTarifPlan

class SUserCreate(BaseModel):
    email: str #emailvalidator
    password: str
    
class SUserGet(SUserCreate):
    id: int
    tarifplan: UserTarifPlan
    
