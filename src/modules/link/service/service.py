import json
import logging
from typing import Annotated, Literal

from fastapi import Depends

from src.core.abstract_repositories.key_value_repository import IKeyValueRepository
from src.core.exceptions.exceptions import PermissionDeniedException
from src.db.deco_for_SQLAlchemy_servicies import handle_service_exceptions
from src.modules.link.repositories.abstract_repositories import IORMLinkRepository
from src.modules.link.schemas import (
    SLinkCreateDTO,
    SLinkResponse,
    SLinkUpdate,
    SLinkWithClicks,
)
from src.modules.link.service.url_generator import URLGenerator, get_url_generator

logger = logging.getLogger(__name__)


class LinkService:

    def __init__(
        self,
        repo: IORMLinkRepository,
        cache: IKeyValueRepository,
        url_generator: Annotated[URLGenerator, Depends(get_url_generator)],
    ):
        self.repo = repo
        self.cache = cache
        self.url_generator = url_generator

    @handle_service_exceptions
    async def create(self, link_to_create: SLinkCreateDTO) -> SLinkResponse:
        short_url = await self.url_generator.get_url()
        new_link = await self.repo.create(
            **link_to_create.model_dump(), short_url=short_url
        )
        logger.info(f"Created link {link_to_create}")
        return SLinkResponse.model_validate(new_link)

    @handle_service_exceptions
    async def get_by_url(self, user_id: int, link_url: str) -> SLinkResponse:
        await self._verify_id(user_id, link_url)
        link_in_db = await self.repo.get_by_url(link_url)
        link = SLinkResponse.model_validate(link_in_db)
        logger.info(f"Returned link {link_url=} for user with id {user_id}")
        return link

    @handle_service_exceptions
    async def get_with_clicks(self, user_id: int, link_url: str) -> SLinkWithClicks:
        """Get link with clicks due to eager load.

        Args:
            user_id (int)
            link_url (str)

        Returns:
            SLinkWithClicksResponse: Link with clicks.
        """
        await self._verify_id(user_id, link_url)
        link_wtih_clicks = await self.repo.get_with_clicks(link_url)
        logger.info(
            f"Returned link with clicks with {link_url=} for user with id {user_id}"
        )
        return SLinkWithClicks.model_validate(link_wtih_clicks)

    @handle_service_exceptions
    async def update(self, user_id: int, link_to_update: SLinkUpdate) -> SLinkResponse:
        await self._verify_id(user_id, link_to_update.url)
        link_url = link_to_update.url
        link_data = link_to_update.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )
        updated_user = await self.repo.update(link_url, link_data)
        logger.info(f"Updated link {link_to_update} for user with id {user_id}")
        return SLinkResponse.model_validate(updated_user)

    @handle_service_exceptions
    async def delete(self, user_id: int, link_url: str) -> Literal[True]:
        await self._verify_id(user_id, link_url)
        logger.info(f"Deleted link with {link_url=} for user with id {user_id}")
        return await self.repo.delete(link_url)

    @handle_service_exceptions
    async def increment_click_counters(
        self, links_data: dict[int, int]
    ) -> list[SLinkResponse]:
        """Incremet click counters for multiple links.

        Args:
            links_data (dict[int, int]): dict with link ids and click_counter increments

        Returns:
            list[SLinkResponse]: list of links.
        """
        links_with_incemented_click_counter = await self.repo.increment_click_counters(
            links_data
        )
        logger.info(f"Incremented click counters for links {list[links_data.keys()]}")
        return [
            SLinkResponse.model_validate(link)
            for link in links_with_incemented_click_counter
        ]

    @handle_service_exceptions
    async def get_for_redirect(
        self,
        link_url: str,
    ) -> SLinkResponse:
        """Get link with cache"""
        if link_in_cache := await self.cache.get(f"link_url_{link_url}"):
            return SLinkResponse.model_validate(json.loads(link_in_cache))
        else:
            link_in_db = await self.repo.get_by_url(link_url)
            link = SLinkResponse.model_validate(link_in_db)
            await self.cache.set_(
                f"link_url_{link_url}", link.model_dump_json(), expire=10
            )
            logger.info(f"Redirected from {link_url=}")
            return link

    @handle_service_exceptions
    async def _verify_id(self, current_user_id: int, link_url: str):
        link = await self.repo.get_by_url(link_url)
        if current_user_id != 1 and current_user_id != link.user_id:
            raise PermissionDeniedException(
                f"Can not verify {current_user_id=} with link id {link.user_id}"
            )
