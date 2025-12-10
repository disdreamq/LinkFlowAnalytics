from typing import Annotated, Literal

from fastapi import Depends
from src.modules.link.dependencies import get_link_repository
from src.modules.link.repository import LinkRepository
from src.core.exception_factory import exception_factory


async def check_id(
    url: str,
    user_id: int,
    link_repo: Annotated[LinkRepository, Depends(get_link_repository)],
) -> Literal[True]:
    link = await link_repo.get_link_by_url(url)
    if link.user_id != user_id:
        raise exception_factory.not_found(resource='link', identifier=f'{url}')
    return True