from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.enums.enums import UserTarifPlan
from src.modules.user.schemas import SUserInDB


@pytest.fixture
def mock_user_service():
    service = MagicMock()
    service.get_by_email = AsyncMock()
    return service


@pytest.fixture
def sample_user_data():
    return {
        "id": 1,
        "email": "test@example.com",
        "password": "$2b$12$hashed_password",  # bcrypt
        "tarifplan": UserTarifPlan.Base,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }


@pytest.fixture
def sample_user_in_db(sample_user_data):
    return SUserInDB(**sample_user_data)


@pytest.fixture
def mock_settings():
    """Мок настроек приложения"""
    settings = MagicMock()
    settings.secret_key = "test_secret_key"
    settings.alghoritm = "HS256"
    return settings


@pytest.fixture
def sample_token_data():
    """Тестовые данные для токена"""
    return {
        "sub": "1",
        "email": "test@example.com",
        "username": "testuser",
    }
