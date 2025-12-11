from src.modules.click.models import Click
from src.modules.click.repository import ClickRepository
from src.modules.click.schemas.schemas import (
    SClickCreate,
    SClickResponse,
    SClickWithLinkResponse,
)


class ClickService:
    def __init__(self, repo: ClickRepository):
        self.repo = repo

    async def create_clicks(self, clicks: list[SClickCreate]) -> list[SClickResponse]:
        clicks_to_create = [Click(**click.model_dump()) for click in clicks]
        created_clicks = await self.repo.create_clicks(clicks_to_create)
        return [SClickResponse.model_validate(click) for click in created_clicks]

    async def get_click(self, click_id: int) -> SClickResponse:
        click = await self.repo.get_click(click_id)
        return SClickResponse.model_validate(click)

    async def get_click_with_link(self, click_id: int) -> SClickWithLinkResponse:
        click_with_link = await self.repo.get_click_with_link(click_id)
        return SClickWithLinkResponse.model_validate(click_with_link)
