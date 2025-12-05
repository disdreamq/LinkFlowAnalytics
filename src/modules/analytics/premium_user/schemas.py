
from src.modules.analytics.base_user.schemas import SBaseUserLinkStatsResponse, SUserLinksRequest


class SPremiumUserLinkStatsResponse(SBaseUserLinkStatsResponse):
    distribution_by_browser: dict[str, int]


class SBaseUserLinksResponse(SUserLinksRequest):
    full_distribution_by_click_counter: dict[str, int]
    full_distribution_by_week_days: dict[str, int]


class SPremiumUserLinksResponse(SBaseUserLinksResponse):
    full_distribution_by_browser: dict[str, int]
