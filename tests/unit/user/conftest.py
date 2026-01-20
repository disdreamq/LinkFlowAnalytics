import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.enums.enums import UserTarifPlan
from src.modules.user.schemas import SUserCreate, SUserUpdate
from src.modules.user.service import UserService


@pytest.fixture(scope="session", autouse=True)
def mock_user_repo():
    repo = MagicMock()

    repo.exists_by_email = AsyncMock()
    repo.create = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.get_by_email = AsyncMock()
    repo.get_with_all_links = AsyncMock()
    repo.update = AsyncMock()
    repo.delete = AsyncMock()

    return repo


@pytest.fixture(scope="session", autouse=True)
def user_service(mock_user_repo):
    return UserService(repo=mock_user_repo)


@pytest.fixture(scope="session", autouse=True)
def sample_user_data():
    return {
        "id": 1,
        "email": "test@example.com",
        "password": "plain_password",
        "tarifplan": UserTarifPlan.Base,
        "created_at": datetime.datetime.now(),
        "updated_at": datetime.datetime.now(),
    }


@pytest.fixture(scope="session", autouse=True)
def sample_user_create(sample_user_data):
    return SUserCreate(
        email=sample_user_data["email"],
        password=sample_user_data["password"],
    )


@pytest.fixture(scope="session", autouse=True)
def sample_user_update(
    sample_user_data,
):
    return SUserUpdate(
        id=sample_user_data["id"],
        email="new_email@example.com",
        password="new_password",
        tarifplan=UserTarifPlan.Premium,
    )
