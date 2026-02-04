import pytest


@pytest.fixture
async def created_link_for_redirect(admin_user, client, link_data_register):
    response = await client.post(
        "/links/",
        json=link_data_register,
        headers=admin_user["header"],
    )
    return response.json()
