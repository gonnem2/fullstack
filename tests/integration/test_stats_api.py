import pytest
from datetime import datetime

pytestmark = pytest.mark.integration


class TestStats:
    async def test_expense_stats(self, client, auth_headers, expense_category):
        # создаём несколько расходов
        for i in range(3):
            await client.post(
                "/api/v1/spending",
                headers=auth_headers,
                data={
                    "expense_date": datetime.now().isoformat(),
                    "category_id": expense_category.id,
                    "cost": 100 * (i + 1),
                },
            )
        resp = await client.get(
            "/api/v1/stats/expenses", headers=auth_headers, params={"period": "week"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "total" in data
        assert data["total"] == 600

    async def test_dynamic_stats(self, client, auth_headers, expense_category):
        resp = await client.get(
            "/api/v1/stats/dynamic", headers=auth_headers, params={"period": "month"}
        )
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
