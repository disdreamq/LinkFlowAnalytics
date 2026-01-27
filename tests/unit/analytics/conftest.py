import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.enums.enums import UserTarifPlan
from src.modules.analytics.base_user.service import BaseUserAnalyticService
from src.modules.analytics.premium_user.service import PremiumUserAnalyticService
from src.modules.click.schemas import SClickResponse
from src.modules.link.schemas import SLinkResponse


@pytest.fixture
def mock_link_service():
    service = MagicMock()

    service.get_with_clicks = AsyncMock()

    return service


@pytest.fixture
def mock_user_service():
    service = MagicMock()

    service.get_with_links = AsyncMock()

    return service


@pytest.fixture
def base_user_analytic_service(mock_link_service, mock_user_service):
    return BaseUserAnalyticService(mock_link_service, mock_user_service)


@pytest.fixture
def prem_user_analytic_service(mock_link_service, mock_user_service):
    return PremiumUserAnalyticService(mock_link_service, mock_user_service)


@pytest.fixture
def sample_user_with_links():
    user_with_links_with_links = {
        "id": 1,
        "email": "test@example.com",
        "password": "plain_password",
        "tarifplan": UserTarifPlan.Base,
        "created_at": datetime.datetime.now(),
        "updated_at": datetime.datetime.now(),
        "links": [
            SLinkResponse(
                id=1,
                user_id=1,
                base_url="https://example.com",
                url="aaaaa",
                click_counter=5,
                created_at=datetime.datetime.now(),
                updated_at=datetime.datetime.now(),
            ),
            SLinkResponse(
                id=2,
                user_id=1,
                base_url="https://example.com",
                url="aaaab",
                click_counter=5,
                created_at=datetime.datetime.now(),
                updated_at=datetime.datetime.now(),
            ),
        ],
    }

    return user_with_links_with_links


@pytest.fixture
def sample_user_with_one_link():
    user_with_links_with_link = {
        "id": 1,
        "email": "test@example.com",
        "password": "plain_password",
        "tarifplan": UserTarifPlan.Base,
        "created_at": datetime.datetime.now(),
        "updated_at": datetime.datetime.now(),
        "links": [
            SLinkResponse(
                id=1,
                user_id=1,
                base_url="https://example.com",
                url="aaaaa",
                click_counter=5,
                created_at=datetime.datetime.now(),
                updated_at=datetime.datetime.now(),
            )
        ],
    }

    return user_with_links_with_link


@pytest.fixture
def sample_links_with_clicks():
    links_with_clicks = [
        {
            "id": 1,
            "user_id": 1,
            "base_url": "https://www.example.com/",
            "url": "aaaaa",
            "click_counter": 0,
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now(),
        },
        {
            "id": 2,
            "user_id": 1,
            "base_url": "https://www.example.com/",
            "url": "aaaab",
            "click_counter": 2,
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now(),
            "clicks": [
                SClickResponse(
                    id=1,
                    link_id=2,
                    user_ip=None,
                    user_agent="Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
                    created_at=datetime.datetime(
                        year=2026, month=1, day=24, hour=15, minute=0, second=0
                    ),
                ),
                SClickResponse(
                    id=2,
                    link_id=2,
                    user_ip=None,
                    user_agent="Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
                    created_at=datetime.datetime(
                        year=2026, month=1, day=24, hour=15, minute=0, second=0
                    ),
                ),
            ],
        },
    ]

    return links_with_clicks


@pytest.fixture
def sample_link_with_clicks_different_browsers():
    link_with_clicks = {
        "id": 2,
        "user_id": 1,
        "base_url": "https://www.example.com/",
        "url": "aaaab",
        "click_counter": 3,
        "created_at": datetime.datetime.now(),
        "updated_at": datetime.datetime.now(),
        "clicks": [
            SClickResponse(
                id=1,
                link_id=2,
                user_ip=None,
                user_agent="Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
                created_at=datetime.datetime(
                    year=2026, month=1, day=24, hour=15, minute=0, second=0
                ),
            ),
            SClickResponse(
                id=2,
                link_id=2,
                user_ip=None,
                user_agent="Chrome/52.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
                created_at=datetime.datetime(
                    year=2026, month=1, day=24, hour=15, minute=0, second=0
                ),
            ),
            SClickResponse(
                id=2,
                link_id=2,
                user_ip=None,
                user_agent="Yandex/1.2 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
                created_at=datetime.datetime(
                    year=2026, month=1, day=24, hour=15, minute=0, second=0
                ),
            ),
        ],
    }

    return link_with_clicks


@pytest.fixture
def sample_link_with_clicks_different_browsers_summing_click_counter():
    link_with_clicks = {
        "id": 2,
        "user_id": 1,
        "base_url": "https://www.example.com/",
        "url": "aaaab",
        "click_counter": 3,
        "created_at": datetime.datetime.now(),
        "updated_at": datetime.datetime.now(),
        "clicks": [
            SClickResponse(
                id=1,
                link_id=2,
                user_ip=None,
                user_agent="Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
                created_at=datetime.datetime(
                    year=2026, month=1, day=24, hour=15, minute=0, second=0
                ),
            ),
            SClickResponse(
                id=2,
                link_id=2,
                user_ip=None,
                user_agent="Chrome/52.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
                created_at=datetime.datetime(
                    year=2026, month=1, day=24, hour=15, minute=0, second=0
                ),
            ),
            SClickResponse(
                id=2,
                link_id=2,
                user_ip=None,
                user_agent="Chrome/52.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
                created_at=datetime.datetime(
                    year=2026, month=1, day=24, hour=15, minute=0, second=0
                ),
            ),
        ],
    }

    return link_with_clicks


@pytest.fixture
def sample_link_many_clicks():
    link_with_clicks = {
        "id": 1,
        "user_id": 1,
        "base_url": "https://www.example.com/",
        "url": "aaaab",
        "click_counter": 4,
        "created_at": datetime.datetime.now(),
        "updated_at": datetime.datetime.now(),
        "clicks": [
            SClickResponse(
                id=1,
                link_id=1,
                user_ip=None,
                user_agent="Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
                created_at=datetime.datetime(
                    year=2026, month=1, day=24, hour=15, minute=0, second=0
                ),
            ),
            SClickResponse(
                id=2,
                link_id=1,
                user_ip=None,
                user_agent="Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
                created_at=datetime.datetime(
                    year=2026, month=1, day=24, hour=15, minute=0, second=0
                ),
            ),
            SClickResponse(
                id=3,
                link_id=1,
                user_ip=None,
                user_agent="Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
                created_at=datetime.datetime(
                    year=2026, month=1, day=23, hour=15, minute=0, second=0
                ),
            ),
            SClickResponse(
                id=4,
                link_id=1,
                user_ip=None,
                user_agent="Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
                created_at=datetime.datetime(
                    year=2026, month=1, day=22, hour=15, minute=0, second=0
                ),
            ),
        ],
    }
    return link_with_clicks


@pytest.fixture
def sample_link_with_clicks_full_weak():
    link_with_clicks = {
        "id": 1,
        "user_id": 1,
        "base_url": "https://www.example.com/",
        "url": "aaaab",
        "click_counter": 4,
        "created_at": datetime.datetime.now(),
        "updated_at": datetime.datetime.now(),
        "clicks": [
            SClickResponse(
                id=1,
                link_id=1,
                user_ip=None,
                user_agent="Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
                created_at=datetime.datetime(
                    year=2026, month=1, day=24, hour=15, minute=0, second=0
                ),
            ),
            SClickResponse(
                id=2,
                link_id=1,
                user_ip=None,
                user_agent="Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
                created_at=datetime.datetime(
                    year=2026, month=1, day=23, hour=15, minute=0, second=0
                ),
            ),
            SClickResponse(
                id=3,
                link_id=1,
                user_ip=None,
                user_agent="Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
                created_at=datetime.datetime(
                    year=2026, month=1, day=22, hour=15, minute=0, second=0
                ),
            ),
            SClickResponse(
                id=4,
                link_id=1,
                user_ip=None,
                user_agent="Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
                created_at=datetime.datetime(
                    year=2026, month=1, day=21, hour=15, minute=0, second=0
                ),
            ),
            SClickResponse(
                id=5,
                link_id=1,
                user_ip=None,
                user_agent="Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
                created_at=datetime.datetime(
                    year=2026, month=1, day=20, hour=15, minute=0, second=0
                ),
            ),
            SClickResponse(
                id=6,
                link_id=1,
                user_ip=None,
                user_agent="Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
                created_at=datetime.datetime(
                    year=2026, month=1, day=19, hour=15, minute=0, second=0
                ),
            ),
            SClickResponse(
                id=7,
                link_id=1,
                user_ip=None,
                user_agent="Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
                created_at=datetime.datetime(
                    year=2026, month=1, day=18, hour=15, minute=0, second=0
                ),
            ),
        ],
    }
    return link_with_clicks
