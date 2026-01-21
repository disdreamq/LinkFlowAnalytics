from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.enums.enums import UserTarifPlan
from src.modules.link.schemas import SLinkResponse


class SUserCreate(BaseModel):
    email: EmailStr
    password: Annotated[str, Field(min_length=8)]


class SUserInDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    password: str
    tarifplan: UserTarifPlan
    created_at: datetime
    updated_at: datetime


class SUserUpdate(BaseModel):
    id: int
    email: EmailStr | None = None
    password: Annotated[str, Field(min_length=8)] | None = None
    tarifplan: UserTarifPlan | None = None


class SUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    tarifplan: UserTarifPlan
    created_at: datetime
    updated_at: datetime


class SUserWithLinks(SUserInDB):
    links: list[SLinkResponse] = []
