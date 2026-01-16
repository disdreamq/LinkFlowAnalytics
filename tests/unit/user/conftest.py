from unittest.mock import AsyncMock, MagicMock

import pytest

from enums.enums import UserTarifPlan
from src.modules.user.schemas import SUserCreate, SUserUpdate
from src.modules.user.service import UserService


@pytest.fixture(scope="function", autouse=True)
def mock_user_repo():
    repo = MagicMock()

    repo.exists_by_email = AsyncMock()
    repo.create = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.get_by_email = AsyncMock()
    repo.get_with_links = AsyncMock()
    repo.update = AsyncMock()
    repo.delete = AsyncMock()

    return repo


@pytest.fixture(scope="session", autouse=True)
def user_service(mock_repo):
    return UserService(repo=mock_repo)


@pytest.fixture(scope="session", autouse=True)
def sample_user_data():
    return {
        "id": 1,
        "email": "test@example.com",
        "password": "plain_password",
        "tarifplan": UserTarifPlan.Base,
    }


@pytest.fixture(scope="session", autouse=True)
def sample_user_create():
    data = sample_user_data()
    return SUserCreate(
        email=data["email"],
        password=data["password"],
    )


@pytest.fixture(scope="session", autouse=True)
def sample_user_update(
    new_email: str | None = None,
    new_password: str | None = None,
    new_tarifplan: UserTarifPlan | None = None,
):
    data = sample_user_data()
    return SUserUpdate(
        id=data["id"],
        email=new_email,
        password=new_password,
        tarifplan=new_tarifplan,
    )
