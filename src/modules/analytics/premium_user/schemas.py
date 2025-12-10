from src.modules.analytics.base_user.schemas import (
    SBaseUserAllLinksResponse,
    SBaseUserSingleLinkResponse,
)


class SPremiumUserLinkStatsResponse(SBaseUserSingleLinkResponse):
    distribution_by_browser: dict[str, int]


class SPremiumUserLinksResponse(SBaseUserAllLinksResponse):
    full_distribution_by_browser: dict[str, int]
