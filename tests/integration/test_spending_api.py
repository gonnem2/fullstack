import pytest
from datetime import datetime, timedelta

pytestmark = pytest.mark.integration


class TestSpendingCRUD:
    async def test_create_spending(self, client, auth_headers, expense_category):
        resp = await client.post(
            "/api/v1/spending",
            headers=auth_headers,
            data={
                "expense_date": datetime.now().isoformat(),
                "category_id": expense_category.id,
                "cost": 150.0,
                "comment": "Обед",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["value"] == 150.0

    async def test_get_spendings_filter(self, client, auth_headers, expense_category):
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        # создаём две траты
        await client.post(
            "/api/v1/spending",
            headers=auth_headers,
            data={
                "expense_date": yesterday.isoformat(),
                "category_id": expense_category.id,
                "cost": 100,
            },
        )
        await client.post(
            "/api/v1/spending",
            headers=auth_headers,
            data={
                "expense_date": now.isoformat(),
                "category_id": expense_category.id,
                "cost": 200,
            },
        )
        resp = await client.get(
            "/api/v1/spending",
            headers=auth_headers,
            params={
                "from_date": now.replace(hour=0, minute=0).isoformat(),
                "to_date": now.isoformat(),
            },
        )
        assert resp.status_code == 200
        assert len(resp.json()["data"]["expenses"]) == 1

    async def test_update_spending(self, client, auth_headers, expense_category):
        create = await client.post(
            "/api/v1/spending",
            headers=auth_headers,
            data={
                "expense_date": datetime.now().isoformat(),
                "category_id": expense_category.id,
                "cost": 50,
            },
            files={}
        )
        spend_id = create.json()["id"]
        resp = await client.put(
            f"/api/v1/spending/{spend_id}",
            headers=auth_headers,
            json={"category_id": expense_category.id, "cost": 75},
        )
        assert resp.status_code == 200
        assert resp.json()["value"] == 75

    async def test_delete_spending(self, client, auth_headers, expense_category):
        create = await client.post(
            "/api/v1/spending",
            headers=auth_headers,
            data={
                "expense_date": datetime.now().isoformat(),
                "category_id": expense_category.id,
                "cost": 30,
            },
        )
        spend_id = create.json()["id"]
        resp = await client.delete(f"/api/v1/spending/{spend_id}", headers=auth_headers)
        assert resp.status_code == 200
        get = await client.get(f"/api/v1/spending/{spend_id}", headers=auth_headers)
        assert get.status_code == 404
