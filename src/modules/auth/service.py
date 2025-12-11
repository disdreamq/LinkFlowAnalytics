from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

from src.core.config import get_settings
from src.core.exception_factory import exception_factory
from src.core.security import verify_password
from src.modules.auth.schemas import STokenResponse, TokenData
from src.modules.user.dependencies import get_user_repository
from src.modules.user.repository import UserRepository
from src.modules.user.schemas.schemas import SUserInDB, SUserResponse

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def authenticate_user(
    repo: Annotated[UserRepository, Depends(get_user_repository)],
    email: str,
    password: str,
) -> SUserInDB:
    user = await repo.get_user_by_email(email)
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


async def get_current_user(
    repo: Annotated[UserRepository, Depends(get_user_repository)],
    token: Annotated[str, Depends(_oauth2_scheme)],
) -> SUserResponse:
    try:
        payload = jwt.decode(
            token, get_settings().secret_key, algorithms=[get_settings().alghoritm]
        )
        username = payload.get("sub")
        if username is None:
            raise exception_factory.unauthorized()
        token_data = TokenData(username=username)
        if not token_data.username:
            raise exception_factory.unauthorized()
    except InvalidTokenError:
        raise exception_factory.unauthorized() from None

    user = await repo.get_user_by_email(token_data.username)
    if user is None:
        raise exception_factory.unauthorized()
    return SUserResponse.model_validate(user)
