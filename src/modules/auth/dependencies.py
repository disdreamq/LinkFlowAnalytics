from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

from src.core.config import get_settings
from src.core.exceptions.exceptions import AuthenticationException
from src.modules.auth.schemas import TokenData
from src.modules.user.dependencies import get_user_service
from src.modules.user.schemas import SUserInDB
from src.modules.user.service import UserService

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def require_auth(
    service: Annotated[UserService, Depends(get_user_service)],
    token: Annotated[str, Depends(_oauth2_scheme)],
) -> SUserInDB:
    try:
        payload = jwt.decode(
            token, get_settings().secret_key, algorithms=[get_settings().alghoritm]
        )
        username = payload.get("sub")
        if username is None:
            raise AuthenticationException("Auth error") from None
        token_data = TokenData(username=username)
        if not token_data.username:
            raise AuthenticationException("Auth error") from None
    except InvalidTokenError:
        raise AuthenticationException("Auth error") from None

    user = await service.get_by_email(token_data.username)
    if user is None:
        raise AuthenticationException("Auth error") from None
    return SUserInDB.model_validate(user)
