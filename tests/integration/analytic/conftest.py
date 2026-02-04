import uuid

import pytest


@pytest.fixture
async def sample_link_for_analytics(created_link, client):
    for _ in range(50):
        await client.get(f"/{created_link['url']}")

    return created_link


@pytest.fixture
async def base_user(client):
    unique_email = f"empty_{uuid.uuid4().hex[:8]}@example.com"
    data = {"email": unique_email, "password": "password123"}

    register_response = await client.post("/users/", json=data)
    login_response = await client.post(
        "/token", data={"username": data["email"], "password": data["password"]}
    )
    token = login_response.json()["access_token"]
    header = {"Authorization": f"Bearer {token}"}

    return {"data": register_response.json(), "header": header}


@pytest.fixture()
async def empty_link(base_user, client):
    link = await client.post(
        "/links/",
        json={"base_url": "https://www.example.com/"},
        headers=base_user["header"],
    )
    return link.json()
