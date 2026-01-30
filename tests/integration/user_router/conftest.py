import pytest

from src.enums.enums import UserTarifPlan


@pytest.fixture()
def sample_user_register_data():
    user_data = {
        "email": "test@example.com",
        "password": "password123",
    }
    return user_data


@pytest.fixture()
def sample_user_update_data():
    user_data = {
        "id": 0,
        "email": "test1@example.com",
        "password": "password123",
        "tarifplan": UserTarifPlan.Premium,
    }
    return user_data
