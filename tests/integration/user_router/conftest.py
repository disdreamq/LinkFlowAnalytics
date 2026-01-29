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


@pytest.fixture(autouse=True)
async def register_admin_user(client):
    admin_data = {"email": "admin@example.com", "password": "adminadmin"}
    await client.post(
        "/users/",
        json=admin_data,
    )


@pytest.fixture()
async def admin_user(client):
    admin_data = {"email": "admin@example.com", "password": "adminadmin"}
    response = await client.post(
        "/token",
        data={"username": admin_data["email"], "password": admin_data["password"]},
    )
    token = response.json()["access_token"]
    header = {"Authorization": f"Bearer {token}"}
    resp = await client.get("users/1", headers=header)
    return {"data": resp.json(), "header": header}
