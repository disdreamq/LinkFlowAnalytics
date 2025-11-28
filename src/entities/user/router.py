from typing import Annotated
from fastapi import APIRouter
from fastapi.params import Depends
import logging

from src.entities.user.dependencies import get_user_repository
from src.entities.user.schemas import SUserCreate, SUserGet
from src.entities.user.repository import UserRepository

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/create")
async def create_link(
    user: SUserCreate, repo: Annotated[UserRepository, Depends(get_user_repository)]
):
    user_to_create = await repo.create_user(user)
    return user_to_create


@router.get("/{user_id}")
async def redirect(user_id: int, repo: Annotated[UserRepository, Depends(get_user_repository)]) -> SUserGet:
    user = await repo.get_user_by_id(user_id)
    return SUserGet.model_validate(user)
