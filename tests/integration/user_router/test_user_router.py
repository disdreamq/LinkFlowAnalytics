import pytest
from sqlalchemy import select

from src.enums.enums import UserTarifPlan
from src.modules.user.models import User


class TestCreateUser:
    """Tests for /users/ (post method)"""

    @pytest.mark.asyncio
    async def test_create_user(
        self,
        db_session,
        client,
        sample_user_register_data,
    ):
        response = await client.post(
            "/users/",
            json=sample_user_register_data,
        )
        assert response.status_code == 201
        assert isinstance(response.json()["id"], int)
        assert response.json()["email"] == sample_user_register_data["email"]
        assert response.json()["tarifplan"] == UserTarifPlan.Base
        assert "created_at" in response.json()
        assert "updated_at" in response.json()

        stmt = select(User).where(User.id == response.json()["id"])
        result = await db_session.execute(stmt)
        user_in_db = result.scalar_one_or_none()

        assert user_in_db is not None
        assert user_in_db.email == sample_user_register_data["email"]
        assert user_in_db.tarifplan == UserTarifPlan.Base
        assert user_in_db.password != sample_user_register_data["password"]

    @pytest.mark.parametrize(
        "email, password",
        [
            ("1", "1"),
            ("1", "password123"),
            ("", "password123"),
            ("test@example.com", "1"),
            ("test@example.com", ""),
            ("", ""),
        ],
    )
    @pytest.mark.asyncio
    async def test_create_user_bad_data(self, client, email, password):
        response = await client.post(
            "/users/", json={"email": email, "password": password}
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_user_ununique_email(
        self,
        client,
        sample_user_register_data,
    ):
        response = await client.post(
            "/users/",
            json=sample_user_register_data,
        )
        assert response.status_code == 403

    @pytest.mark.parametrize(
        "malicious_input",
        [
            {"email": "test@example.com", "password": "' OR '1'='1"},
            {"email": "test@example.com", "password": "<script>alert('xss')</script>"},
            {
                "email": "test@example.com'; DROP TABLE users; --",
                "password": "password",
            },
        ],
    )
    @pytest.mark.asyncio
    async def test_create_user_malicious_input(self, client, malicious_input):
        """test SQL-injection"""
        response = await client.post("/users/", json=malicious_input)

        assert response.status_code in [400, 403, 422]

        response_json = response.json()
        if "detail" in response_json:
            detail = str(response_json["detail"]).lower()
            assert "sql" not in detail
            assert "syntax" not in detail


class TestGetUser:
    """Tests for /users/{user_id} (get method)"""

    @pytest.mark.asyncio
    async def test_get_user_success(self, client, admin_user):
        response = await client.get("/users/1", headers=admin_user["header"])
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == admin_user["data"]["id"]
        assert data["email"] == admin_user["data"]["email"]

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, client, admin_user):

        response = await client.get(f"/users/{52}", headers=admin_user["header"])

        assert response.status_code == 404

    @pytest.mark.parametrize("user_id", [-1, 0, "s", 2.5])
    @pytest.mark.asyncio
    async def test_get_user_bad_data(self, client, user_id, admin_user):
        response = await client.get(f"/users/{user_id}", headers=admin_user["header"])

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_user_authorization(self, client):
        user1_data = {"email": "user1@example.com", "password": "password123"}
        user2_data = {"email": "user2@example.com", "password": "password321"}

        user1_response = await client.post("/users/", json=user1_data)
        user2_response = await client.post("/users/", json=user2_data)

        user1_id = user1_response.json()["id"]
        user2_id = user2_response.json()["id"]
        login_response = await client.post(
            "/token",
            data={"username": user1_data["email"], "password": user1_data["password"]},
        )
        assert login_response.status_code == 200
        token_user1 = login_response.json()["access_token"]

        response = await client.get(
            f"/users/{user1_id}", headers={"Authorization": f"Bearer {token_user1}"}
        )
        assert response.status_code == 200

        response = await client.get(
            f"/users/{user2_id}", headers={"Authorization": f"Bearer {token_user1}"}
        )

        assert response.status_code == 403


class TestUpdateUser:
    """Tests for /users/{user_id} (put method)"""

    @pytest.mark.asyncio
    async def test_update_user_success(self, client, sample_user_update_data):
        register_response = await client.post(
            "/users/",
            json={
                "email": sample_user_update_data["email"],
                "password": sample_user_update_data["password"],
            },
        )
        sample_user_update_data["id"] = register_response.json()["id"]
        login_response = await client.post(
            "/token",
            data={
                "username": sample_user_update_data["email"],
                "password": sample_user_update_data["password"],
            },
        )
        token = login_response.json()["access_token"]
        response = await client.put(
            f"/users/{sample_user_update_data['id']}",
            json=sample_user_update_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        assert response.json()["tarifplan"] == UserTarifPlan.Premium

    @pytest.mark.parametrize(
        "user_to_update, iter",
        [
            (
                {
                    "id": 0,
                    "email": "",
                    "password": "password123",
                    "tarifplan": UserTarifPlan.Base,
                },
                0,
            ),
            (
                {
                    "id": 0,
                    "email": "test@example.com",
                    "password": "",
                    "tarifplan": UserTarifPlan.Base,
                },
                1,
            ),
            (
                {
                    "id": 0,
                    "email": "test@example",
                    "password": "password123",
                    "tarifplan": UserTarifPlan.Base,
                },
                2,
            ),
            (
                {
                    "id": 0,
                    "email": "test@example.com",
                    "password": "p",
                    "tarifplan": UserTarifPlan.Base,
                },
                3,
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_update_user_bad_data(self, client, user_to_update, iter):
        register_response = await client.post(
            "/users/",
            json={
                "email": f"test{iter+5}@example.com",
                "password": "password123",
            },
        )
        user_to_update["id"] = register_response.json()["id"]
        login_response = await client.post(
            "/token",
            data={
                "username": f"test{iter+5}@example.com",
                "password": "password123",
            },
        )
        token = login_response.json()["access_token"]
        response = await client.put(
            f"/users/{user_to_update['id']}",
            json=user_to_update,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_another_user(self, client):
        user1_data = {"email": "user3@example.com", "password": "password123"}
        user2_data = {"email": "user4@example.com", "password": "password321"}

        user1_response = await client.post("/users/", json=user1_data)
        user2_response = await client.post("/users/", json=user2_data)

        user2_id = user2_response.json()["id"]
        login_response = await client.post(
            "/token",
            data={"username": user1_data["email"], "password": user1_data["password"]},
        )
        token_user1 = login_response.json()["access_token"]

        response = await client.put(
            f"/users/{user2_id}",
            json={
                "id": user2_id,
                "email": "user4@example.com",
                "password": "password123",
                "tarifplan": UserTarifPlan.Premium,
            },
            headers={"Authorization": f"Bearer {token_user1}"},
        )

        assert response.status_code == 403


class TestDeleteUser:
    """Tests for /users/{user_id} (delete method)"""

    @pytest.mark.asyncio
    async def test_delete_user_success(self, db_session, client, admin_user):
        register_response = await client.post(
            "/users/", json={"email": "user7@example.com", "password": "password123"}
        )
        user_id = register_response.json()["id"]

        del_response = await client.delete(
            f"/users/{user_id}", headers=admin_user["header"]
        )
        assert del_response.status_code == 204

    # TODO Сессии не комитятся, не удаляет поэтому.
    # get_response = await client.get(
    #     f"/users/{user_id}", headers=admin_user["header"]
    # )
    # print(get_response.json())
    # assert get_response.status_code == 404

    # stmt = select(User).where(User.id == user_id)
    # result = await db_session.execute(stmt)
    # user_in_db = result.scalar_one_or_none()
    # assert not user_in_db

    @pytest.mark.asyncio
    async def test_delete_another_user(self, client):
        user1_data = {"email": "user5@example.com", "password": "password123"}
        user2_data = {"email": "user6@example.com", "password": "password321"}

        user1_response = await client.post("/users/", json=user1_data)
        user2_response = await client.post("/users/", json=user2_data)

        user2_id = user2_response.json()["id"]
        login_response = await client.post(
            "/token",
            data={"username": user1_data["email"], "password": user1_data["password"]},
        )
        token_user1 = login_response.json()["access_token"]

        response = await client.delete(
            f"/users/{user2_id}",
            headers={"Authorization": f"Bearer {token_user1}"},
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_bad_data(self, client, admin_user):

        del_response = await client.delete(
            "/users/52", headers=admin_user["header"]
        )
        assert del_response.status_code == 404
