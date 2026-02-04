import pytest
from sqlalchemy import select


class TestCreateLink:
    """Tests for /links/ (post method)"""

    @pytest.mark.asyncio
    async def test_create_link_success(
        self, admin_user, client, db_session, link_data_register
    ):
        create_response = await client.post(
            "/links/",
            json=link_data_register,
            headers=admin_user["header"],
        )
        assert create_response.status_code == 201

        response_data = create_response.json()
        link_url = response_data["url"]
        base_url = response_data.get("base_url", link_data_register["base_url"])

        from src.modules.link.models import Link

        stmt = select(Link).where(Link.url == link_url)
        result = await db_session.execute(stmt)
        link_in_db = result.scalar_one_or_none()

        assert link_in_db is not None
        assert link_in_db.url == link_url
        assert link_in_db.base_url == base_url

    @pytest.mark.parametrize(
        "base_url",
        ["", "short", "www.example.com/", 1, True],
    )
    @pytest.mark.asyncio
    async def test_create_link_bad_data(
        self,
        admin_user,
        client,
        base_url,
    ):
        response = await client.post(
            "/links/",
            json={"base_url": base_url},
            headers=admin_user["header"],
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_multiple_links(self, admin_user, client, link_data_register):
        for _ in range(10):
            create_response = await client.post(
                "/links/",
                json=link_data_register,
                headers=admin_user["header"],
            )
            assert create_response.status_code == 201
            assert create_response.json()["base_url"] == link_data_register["base_url"]

    @pytest.mark.parametrize(
        "base_url",
        [
            "http://example.com/",
            "https://example.com/path?query=param/",
            "https://sub.domain.example.com:8080/path/",
            "http://localhost:3000/",
        ],
    )
    async def test_create_link_valid_urls(self, admin_user, client, base_url):
        response = await client.post(
            "/links/",
            json={"base_url": base_url},
            headers=admin_user["header"],
        )
        assert response.status_code == 201
        assert response.json()["base_url"] == base_url

    @pytest.mark.parametrize(
        "base_url",
        [
            f"https://example.com/{'a'*1000}",
            "https://example.com/"
            + "x" * 100
            + "?"
            + "&".join([f"p{i}=v{i}" for i in range(50)]),
        ],
    )
    async def test_create_long_urls(self, admin_user, client, base_url):
        response = await client.post(
            "/links/", json={"base_url": base_url}, headers=admin_user["header"]
        )
        assert response.status_code == 201


class TestGetLink:
    """Tests for "/links/{link_url} (get method)"""

    @pytest.mark.asyncio
    async def test_get_link_success(self, admin_user, client, created_link):
        get_response = await client.get(
            f"/links/{created_link['url']}", headers=admin_user["header"]
        )
        assert get_response.status_code == 200
        assert get_response.json()["url"] == created_link["url"]
        assert get_response.json()["user_id"] == 1

    @pytest.mark.parametrize("link_url", ["aaaa", None, -1, "щщщщщ", 0])
    @pytest.mark.asyncio
    async def test_get_bad_data(self, admin_user, client, link_url):
        response = await client.get(
            f"/links/{link_url}",
            headers=admin_user["header"],
        )
        assert response.status_code == 422

    @pytest.mark.parametrize("link_url", ["bbbbb", "11111", "aaa11"])
    @pytest.mark.asyncio
    async def test_get_not_found(self, admin_user, client, link_url):
        response = await client.get(
            f"/links/{link_url}",
            headers=admin_user["header"],
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_link_authorization(self, client, link_data_register):
        user1_data = {"email": "user1@example.com", "password": "password123"}
        user2_data = {"email": "user2@example.com", "password": "password321"}

        await client.post("/users/", json=user1_data)
        await client.post("/users/", json=user2_data)

        login_response_user1 = await client.post(
            "/token",
            data={"username": user1_data["email"], "password": user1_data["password"]},
        )
        token_user1 = login_response_user1.json()["access_token"]

        login_response_user2 = await client.post(
            "/token",
            data={"username": user2_data["email"], "password": user2_data["password"]},
        )
        token_user2 = login_response_user2.json()["access_token"]

        response = await client.post(
            "/links/",
            json=link_data_register,
            headers={"Authorization": f"Bearer {token_user1}"},
        )
        url = response.json()["url"]
        another_user_response = await client.get(
            f"/links/{url}",
            headers={"Authorization": f"Bearer {token_user2}"},
        )
        assert another_user_response.status_code == 403

    @pytest.mark.parametrize(
        "header",
        [
            None,
            {"Authorization": "Bearer invalid_token"},
            {
                "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2..."
            },
            {"Authorization": "Basic YWRtaW46cGFzc3dvcmQ="},
        ],
    )
    async def test_auth_required(self, client, header, link_data_register):
        response = await client.post(
            "/links/",
            json=link_data_register,
            headers=header,
        )
        assert response.status_code in (401, 403)

    async def test_get_link_case_sensitive(self, admin_user, client):
        create_response = await client.post(
            "/links/",
            json={"base_url": "https://example.com"},
            headers=admin_user["header"],
        )
        original_url = create_response.json()["url"]

        if original_url.lower() != original_url.upper():
            modified_url = original_url.swapcase()
            response = await client.get(
                f"/links/{modified_url}",
                headers=admin_user["header"],
            )
            assert response.status_code == 404


class TestDeleteLink:
    """Tests for links/{link_url}, (delete method)"""

    @pytest.mark.asyncio
    async def test_delete_link_success(self, client, admin_user, created_link):
        response = await client.delete(
            f"/links/{created_link['url']}", headers=admin_user["header"]
        )
        assert response.status_code == 204

    @pytest.mark.parametrize("url", ["11111", "bbbbb", "5252a"])
    @pytest.mark.asyncio
    async def test_delete_link_not_found(self, client, admin_user, url):
        response = await client.delete(f"/links/{url}", headers=admin_user["header"])
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_link_authorization(self, client, link_data_register):
        user1_data = {"email": "user1@example.com", "password": "password123"}
        user2_data = {"email": "user2@example.com", "password": "password321"}

        await client.post("/users/", json=user1_data)
        await client.post("/users/", json=user2_data)

        login_response_user1 = await client.post(
            "/token",
            data={"username": user1_data["email"], "password": user1_data["password"]},
        )
        token_user1 = login_response_user1.json()["access_token"]

        login_response_user2 = await client.post(
            "/token",
            data={"username": user2_data["email"], "password": user2_data["password"]},
        )
        token_user2 = login_response_user2.json()["access_token"]

        response = await client.post(
            "/links/",
            json=link_data_register,
            headers={"Authorization": f"Bearer {token_user1}"},
        )
        url = response.json()["url"]
        another_user_response = await client.delete(
            f"/links/{url}",
            headers={"Authorization": f"Bearer {token_user2}"},
        )
        assert another_user_response.status_code == 403


class TestRedirectRouter:
    """Tests for "/{url}" (get method) for redirect users"""

    @pytest.mark.asyncio
    async def test_redirect_success(self, client, created_link):
        response = await client.get(f"/{created_link['url']}", follow_redirects=False)
        assert response.status_code == 307

    @pytest.mark.asyncio
    async def test_redirect_add_clicks(
        self, client, created_link_for_redirect, db_session
    ):
        """Tests for background tast adds clicks from buffer to db"""
        for _ in range(50):
            await client.get(
                f"/{created_link_for_redirect['url']}", follow_redirects=False
            )
        from src.modules.click.models import Click

        stmt = select(Click).where(Click.link_id == created_link_for_redirect["id"])
        result = await db_session.execute(stmt)
        clicks = result.scalars().all()
        assert len(clicks) in (49, 50)

    @pytest.mark.parametrize("url", ["", 5, "щщщщщ", "aaa", "bbbbb", "5252a"])
    @pytest.mark.asyncio
    async def test_redirect_bad_data_and_not_found(self, client, url):
        response = await client.get(f"/{url}", follow_redirects=False)
        assert response.status_code in (422, 404)

    @pytest.mark.asyncio
    async def test_redirect_correct_url(self, client, created_link):
        response = await client.get(f"/{created_link['url']}", follow_redirects=False)
        assert response.status_code == 307
        location_header = response.headers.get("location")
        assert location_header == created_link["base_url"]

    @pytest.mark.parametrize(
        "user_agent",
        [
            "",
            "A" * 1000,
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            None,
            "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
        ],
    )
    @pytest.mark.asyncio
    async def test_redirect_with_various_user_agents(
        self, client, created_link, user_agent
    ):
        headers = {}
        if user_agent is not None:
            headers["User-Agent"] = user_agent

        response = await client.get(
            f"/{created_link['url']}", headers=headers, follow_redirects=False
        )
        assert response.status_code == 307
        assert response.headers.get("location") == created_link["base_url"]
