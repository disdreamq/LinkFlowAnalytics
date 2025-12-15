from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends

from src.core.config import get_settings
from src.core.exception_factory import exception_factory
from src.core.security import verify_password
from src.modules.auth.schemas import STokenResponse
from src.modules.user.dependencies import get_user_service
from src.modules.user.schemas.schemas import SUserInDB
from src.modules.user.service import UserService


async def authenticate_user(
    service: Annotated[UserService, Depends(get_user_service)],
    email: str,
    password: str,
) -> SUserInDB:
    user = await service.get_user_by_email(email)
    if not user or not verify_password(
        plain_password=password, hash_password=user.password
    ):
        raise exception_factory.unauthorized()
    return SUserInDB.model_validate(user)


def create_access_token(
    data: dict, expires_delta: timedelta | None = None
) -> STokenResponse:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, get_settings().secret_key, algorithm=get_settings().alghoritm
    )
    return STokenResponse(access_token=encoded_jwt, token_type="bearer")
