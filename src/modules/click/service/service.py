from src.modules.click.models import Click
from src.modules.click.repository import ClickRepository
from modules.click.schemas import (
    SClickCreate,
    SClickResponse,
    SClickWithLinkResponse,
)


class ClickService:
    def __init__(self, repo: ClickRepository):
        self.repo = repo

    async def create_clicks(self, clicks: list[SClickCreate]) -> list[SClickResponse]:
        clicks_to_create = [Click(**click.model_dump()) for click in clicks]
        created_clicks = await self.repo.create(clicks_to_create)
        return [SClickResponse.model_validate(click) for click in created_clicks]

    async def get_click(self, click_id: int) -> SClickResponse:
        click = await self.repo.get_by_id(click_id)
        return SClickResponse.model_validate(click)
