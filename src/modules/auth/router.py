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
from src.modules.user.dependencies import get_user_repository
from src.modules.user.repository import UserRepository
from src.modules.user.schemas.schemas import SUserInDB, SUserUpdate

router = APIRouter(tags=["auth"])


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> STokenResponse:
    user = await authenticate_user(repo, form_data.username, form_data.password)
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
    repo: Annotated[UserRepository, Depends(get_user_repository)],
):
    updated_user = await repo.update_user(user_to_update)
    return updated_user
