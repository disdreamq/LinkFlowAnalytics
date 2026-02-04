import pytest

from src.enums.enums import UserTarifPlan


@pytest.fixture
async def premium_user(base_user, client):
    data = {**base_user["data"]}
    data["tarifplan"] = UserTarifPlan.Premium
    put_response = await client.put(
        f"/users/{data['id']}", json=data, headers=base_user["header"]
    )

    return {"data": put_response.json(), "header": base_user["header"]}


@pytest.fixture
async def sample_link_for_premium_user_analytics(premium_user, client):
    response = await client.post(
        "/links/",
        json={"base_url": "https://www.example.com/"},
        headers=premium_user["header"],
    )
    json = response.json()
    for _ in range(50):
        await client.get(f"/{json['url']}")
    return json


@pytest.fixture()
async def empty_link_premium_user(premium_user, client):
    link = await client.post(
        "/links/",
        json={"base_url": "https://www.example.com/"},
        headers=premium_user["header"],
    )
    return link.json()
