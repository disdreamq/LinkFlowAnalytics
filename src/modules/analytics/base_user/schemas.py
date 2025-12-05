from pydantic import BaseModel


class SLinkStatsRequest(BaseModel):
    url: str


class SUserLinksRequest(BaseModel):
    user_id: int


class SBaseUserSingleLinkResponse(SLinkStatsRequest):
    click_counter: int
    distribution_by_week_days: dict[str, int]


class SBaseUserAllLinksResponse(SUserLinksRequest):
    full_distribution_by_click_counter: dict[str, int]
    full_distribution_by_week_days: dict[str, int]
