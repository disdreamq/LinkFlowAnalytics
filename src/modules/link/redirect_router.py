from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, status, BackgroundTasks, Request
from fastapi.responses import RedirectResponse
import logging


from src.redis.click_buffer import get_buffer
from src.modules.click.schemas import SClickCreate
from src.modules.link.dependencies import get_link_repository
from src.modules.link.repository import LinkRepository
from src.redis.click_buffer import ClickBuffer


logger = logging.getLogger(__name__)
router = APIRouter(tags=["redirect"])

@router.get(
    "/{url}",
    response_class=RedirectResponse,
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    summary="Redirect to original URL",
    description="Redirect to original URL from short URL",
    responses={
        307: {"description": "Redirect to original URL"},
        404: {"description": "Short URL not found"},
    },
)
async def redirect(
    url: str,
    repo: Annotated[LinkRepository, Depends(get_link_repository)],
    buffer: Annotated[ClickBuffer, Depends(get_buffer)],
    background_tasks: BackgroundTasks,
    request: Request,
):
    user_agent = request.headers.get("user-agent", "Unknown")
    user_ip = request.client.host if request.client else None
    link = await repo.get_link_by_url(str(url))
    new_click = SClickCreate(
        link_id=link.id,
        user_agent=user_agent,
        user_ip=user_ip if user_ip else None,
        created_at=datetime.now(),
    )
    background_tasks.add_task(buffer.add_click, new_click)
    return RedirectResponse(link.base_url)
