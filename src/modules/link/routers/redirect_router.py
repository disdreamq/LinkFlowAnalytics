import logging
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from fastapi.responses import RedirectResponse

from src.modules.click.schemas.schemas import SClickCreate
from src.modules.click.service.click_buffer import ClickBuffer, get_buffer
from src.modules.link.dependencies import get_link_service
from src.modules.link.service.service import LinkService

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
    link_url: str,
    service: Annotated[LinkService, Depends(get_link_service)],
    buffer: Annotated[ClickBuffer, Depends(get_buffer)],
    background_tasks: BackgroundTasks,
    request: Request,
):
    user_agent = request.headers.get("user-agent", "Unknown")
    user_ip = request.client.host if request.client else None
    link = await service.get_link_for_redirect(link_url=link_url)
    new_click = SClickCreate(
        link_id=link.id,
        user_agent=user_agent,
        user_ip=user_ip if user_ip else None,
        created_at=datetime.now(),
    )
    background_tasks.add_task(buffer.add_click, new_click)
    return RedirectResponse(link.base_url)
