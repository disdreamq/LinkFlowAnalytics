import logging
from typing import Annotated

from fastapi import APIRouter, status
from fastapi.params import Depends

from src.modules.user.dependencies import get_user_service
from modules.user.schemas import SUserCreate, SUserResponse, SUserUpdate
from src.modules.user.service import UserService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/",
    response_model=SUserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new user",
    responses={
        201: {"description": "User successfully created"},
        400: {"description": "Invalid user provided"},
        500: {"description": "Internal server error"},
    },
)
async def create_user(
    user: SUserCreate, service: Annotated[UserService, Depends(get_user_service)]
):
    user_to_create = await service.create_user(user)
    return user_to_create


@router.get(
    "/{user_id}",
    response_model=SUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user by id",
    responses={
        200: {"description": "User successfully found"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_user(
    user_id: int, service: Annotated[UserService, Depends(get_user_service)]
):
    user = await service.get_user_by_id(user_id)
    return SUserResponse.model_validate(user)


@router.put(
    "/{user_id}",
    response_model=SUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user by id",
    responses={
        200: {"description": "User successfully updated"},
        400: {"description": "Invalid user provided"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"},
    },
)
async def update_user(
    user_to_update: SUserUpdate,
    service: Annotated[UserService, Depends(get_user_service)],
):
    updated_user = await service.update_user(user_to_update)
    return SUserResponse.model_validate(updated_user)


@router.patch(
    "/{user_id}",
    response_model=SUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user by id",
    responses={
        200: {"description": "User successfully updated"},
        400: {"description": "Invalid user provided"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"},
    },
)
async def partically_update_user(
    user_to_update: SUserUpdate,
    service: Annotated[UserService, Depends(get_user_service)],
) -> SUserResponse:
    updated_user = await service.update_user(user_to_update)
    return SUserResponse.model_validate(updated_user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user by id",
    responses={
        204: {"description": "User successfully deleted"},
        400: {"description": "Invalid user provided"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"},
    },
)
async def delete_user(
    user_id: int, service: Annotated[UserService, Depends(get_user_service)]
):
    await service.delete_user(user_id)
    return {'ok': True}
