from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.modules.auth.schemas import STokenResponse
from src.modules.auth.service import (
    authenticate_user,
    create_access_token,
    get_current_user,
)
from src.modules.user.dependencies import get_user_service
from src.modules.user.schemas.schemas import SUserInDB, SUserUpdate
from src.modules.user.service import UserService

router = APIRouter(tags=["auth"])


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: Annotated[UserService, Depends(get_user_service)],
) -> STokenResponse:
    user = await authenticate_user(service, form_data.username, form_data.password)
    access_token_expires = timedelta(minutes=15)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return access_token


@router.get("/me")
async def read_user_me(
    current_user: Annotated[SUserInDB, Depends(get_current_user)],
):
    return current_user


@router.put("/tarifplan")
async def change_tarifplan(
    user_to_update: SUserUpdate,
    service: Annotated[UserService, Depends(get_user_service)],
):
    updated_user = await service.update_user(user_to_update)
    return updated_user
