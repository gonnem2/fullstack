import pytest

pytestmark = pytest.mark.integration


class TestCategoryCreate:
    async def test_create_expense_category(self, client, auth_headers):
        resp = await client.post(
            "/api/v1/categories/",
            json={"title": "Транспорт", "type_of_category": "expense"},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["type_of_category"] == "expense"

    async def test_create_income_category(self, client, auth_headers):
        resp = await client.post(
            "/api/v1/categories/",
            json={"title": "Зарплата", "type_of_category": "income"},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["type_of_category"] == "income"


class TestCategoryRead:
    async def test_list_categories(self, client, auth_headers, expense_category):
        resp = await client.get("/api/v1/categories/", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "categories" in data
        assert len(data["categories"]) >= 1
        # проверяем, что созданная категория есть в списке
        assert any(cat["id"] == expense_category.id for cat in data["categories"])

    async def test_get_category_by_id(self, client, auth_headers, expense_category):
        cat_id = expense_category.id
        resp = await client.get(f"/api/v1/categories/{cat_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == cat_id

    async def test_get_nonexistent_category(self, client, auth_headers):
        resp = await client.get("/api/v1/categories/99999", headers=auth_headers)
        assert resp.status_code == 404


class TestCategoryUpdate:
    async def test_update_category(self, client, auth_headers, expense_category):
        cat_id = expense_category.id
        resp = await client.put(
            f"/api/v1/categories/{cat_id}",
            json={"title": "Еда и напитки", "type_of_category": "expense"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["title"] == "Еда и напитки"


class TestCategoryDelete:
    async def test_delete_category(self, client, auth_headers):
        # Создаём категорию специально для удаления
        create = await client.post(
            "/api/v1/categories/",
            json={"title": "Удалить меня", "type_of_category": "expense"},
            headers=auth_headers,
        )
        cat_id = create.json()["id"]
        resp = await client.delete(f"/api/v1/categories/{cat_id}", headers=auth_headers)
        assert resp.status_code == 204
        get = await client.get(f"/api/v1/categories/{cat_id}", headers=auth_headers)
        assert get.status_code == 404
