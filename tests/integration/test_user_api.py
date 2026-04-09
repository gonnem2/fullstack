import pytest

pytestmark = pytest.mark.integration


class TestUserAdmin:
    async def test_admin_get_all_users(self, client, admin_headers):
        resp = await client.get(
            "/api/v1/users/admin/all",
            headers=admin_headers,
            params={"skip": 0, "limit": 10},
        )
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_admin_change_role(self, client, admin_headers, registered_user):
        user_id = registered_user.id
        resp = await client.patch(
            f"/api/v1/users/admin/{user_id}",
            headers=admin_headers,
            json={"user_role": "ADMIN"},
        )
        assert resp.status_code == 422
