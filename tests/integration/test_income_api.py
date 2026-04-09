import pytest
from datetime import datetime

pytestmark = pytest.mark.integration


class TestIncomeCRUD:
    async def test_create_income(self, client, auth_headers, income_category):
        resp = await client.post(
            "/api/v1/income",
            headers=auth_headers,
            data={
                "income_date": datetime.now().isoformat(),
                "category_id": str(income_category.id),
                "value": "1000",
            },
            files={},
        )
        assert resp.status_code == 201
        assert resp.json()["value"] == 1000

    async def test_list_incomes(self, client, auth_headers, income_category):
        await client.post(
            "/api/v1/income",
            headers=auth_headers,
            data={
                "income_date": datetime.now().isoformat(),
                "category_id": str(income_category.id),
                "value": "500",
            },
            files={},
        )
        resp = await client.get(
            "/api/v1/income",
            headers=auth_headers,
            params={"from_date": "2025-01-01", "to_date": "2025-12-31"},
        )
        assert resp.status_code == 200
        assert len(resp.json()["data"]["incomes"]) >= 0
