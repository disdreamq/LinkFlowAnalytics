from src.modules.analytics.base_user.schemas import (
    SBaseUserSingleLinkResponse,
    SBaseUserAllLinksResponse,
)


class SPremiumUserLinkStatsResponse(SBaseUserSingleLinkResponse):
    distribution_by_browser: dict[str, int]


class SPremiumUserLinksResponse(SBaseUserAllLinksResponse):
    full_distribution_by_browser: dict[str, int]
