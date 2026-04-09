import pytest
from datetime import datetime
from httpx import AsyncClient

pytestmark = pytest.mark.e2e


async def test_full_user_flow(client: AsyncClient):
    # 1. Регистрация
    reg = await client.post(
        "/api/v1/auth/register",
        json={"username": "e2euser", "email": "e2e@example.com", "password": "e2epass"},
    )
    assert reg.status_code == 201

    # 2. Логин
    login = await client.post(
        "/api/v1/auth/token",
        data={"username": "e2euser", "password": "e2epass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login.status_code == 200
    tokens = login.json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    # 3. Создать категорию расходов
    cat = await client.post(
        "/api/v1/categories/",
        json={"title": "Кафе", "type_of_category": "expense"},
        headers=headers,
    )
    assert cat.status_code == 201
    cat_id = cat.json()["id"]

    # 4. Создать расход с текущей датой
    now = datetime.now().isoformat()
    spend = await client.post(
        "/api/v1/spending",
        headers=headers,
        data={
            "expense_date": now,
            "category_id": str(cat_id),
            "cost": "450",
        },
        files={},  # multipart/form-data
    )
    assert spend.status_code == 201

    # 5. Получить список расходов (без фильтрации по дате, чтобы увидеть созданный)
    spendings = await client.get("/api/v1/spending", headers=headers)
    assert spendings.status_code == 200
    assert len(spendings.json()["data"]["expenses"]) == 1

    # 6. Получить статистику за неделю (расход сегодняшний, должен попасть)
    stats = await client.get(
        "/api/v1/stats/expenses", headers=headers, params={"period": "week"}
    )
    assert stats.status_code == 200
    assert stats.json()["total"] == 450

    # 7. Выход
    logout = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": tokens["refresh_token"]},
        headers=headers,
    )
    assert logout.status_code == 200
