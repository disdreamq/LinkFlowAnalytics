from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Annotated

from src.enums.enums import UserTarifPlan


class SUserRegister(BaseModel):
    email: str
    password: str


class SUserResponse(SUserRegister):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tarifplan: UserTarifPlan
    created_at: datetime
    updated_at: datetime


class STokenResponse(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
