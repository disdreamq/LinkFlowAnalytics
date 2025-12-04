from typing import Annotated
from fastapi import APIRouter, status
from fastapi.params import Depends
import logging

from src.modules.user.dependencies import get_user_repository
from src.modules.user.schemas import SUserCreate, SUserResponse, SUserUpdate
from src.modules.user.repository import UserRepository

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
    user: SUserCreate, repo: Annotated[UserRepository, Depends(get_user_repository)]
):
    user_to_create = await repo.create_user(user)
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
    user_id: int, repo: Annotated[UserRepository, Depends(get_user_repository)]
):
    user = await repo.get_user_by_id(user_id)
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
    new_user_data: SUserUpdate,
    repo: Annotated[UserRepository, Depends(get_user_repository)],
):
    user = await repo.update_user(new_user_data)
    return SUserResponse.model_validate(user)


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
    new_user_data: SUserUpdate,
    repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> SUserResponse:
    user = await repo.update_user(new_user_data)
    return SUserResponse.model_validate(user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    responses={
        204: {"description": "User successfully deleted"},
        400: {"description": "Invalid user provided"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"},
    },
)
async def delete_user(
    user_id: int,
    repo: Annotated[UserRepository, Depends(get_user_repository)],
):
    await repo.delete_user(user_id)
    return 
