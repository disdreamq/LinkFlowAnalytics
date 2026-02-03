import pytest


@pytest.fixture
def link_data_register():
    link_data = {
        "base_url": "https://www.example.com/",
    }
    return link_data


@pytest.fixture
async def created_link(admin_user, client, link_data_register):
    response = await client.post(
        "/links/",
        json=link_data_register,
        headers=admin_user["header"],
    )
    return response.json()

@pytest.fixture
async def created_link_for_redirect(admin_user, client, link_data_register):
    response = await client.post(
        "/links/",
        json=link_data_register,
        headers=admin_user["header"],
    )
    return response.json()
