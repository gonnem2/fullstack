import pytest

pytestmark = pytest.mark.integration


class TestRegister:
    async def test_register_success(self, client):
        resp = await client.post(
            "/api/v1/auth/register",
            json={"username": "newuser", "email": "new@ex.com", "password": "pass"},
        )
        assert resp.status_code == 201
        assert "id" in resp.json()

    async def test_register_duplicate_username(self, client, registered_user):
        resp = await client.post(
            "/api/v1/auth/register",
            json={"username": "testuser", "email": "other@ex.com", "password": "pass"},
        )
        assert resp.status_code == 409


class TestLogin:
    async def test_login_success(self, client, registered_user):
        resp = await client.post(
            "/api/v1/auth/token",
            data={"username": "testuser", "password": "testpassword123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    async def test_login_wrong_password(self, client, registered_user):
        resp = await client.post(
            "/api/v1/auth/token",
            data={"username": "testuser", "password": "wrong"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert resp.status_code == 401

    async def test_login_nonexistent_user(self, client):
        resp = await client.post(
            "/api/v1/auth/token",
            data={"username": "nobody", "password": "pass"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert resp.status_code == 404


class TestRefresh:
    async def test_refresh_token(self, client, registered_user):
        login = await client.post(
            "/api/v1/auth/token",
            data={"username": "testuser", "password": "testpassword123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        refresh = login.json()["refresh_token"]
        resp = await client.post("/api/v1/auth/refresh", json=refresh)
        assert resp.status_code == 200
        assert "access_token" in resp.json()


class TestLogout:
    async def test_logout(self, client, registered_user):
        login = await client.post(
            "/api/v1/auth/token",
            data={"username": "testuser", "password": "testpassword123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        tokens = login.json()
        resp = await client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": tokens["refresh_token"]},
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert resp.status_code == 200
