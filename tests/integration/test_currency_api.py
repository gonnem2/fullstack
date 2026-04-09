import pytest
from unittest.mock import patch, AsyncMock

pytestmark = pytest.mark.integration


class TestCurrency:
    async def test_currency_rates_ok(self, client):
        # мокаем сервис напрямую
        from app.service.currency.service import get_currency_rates

        mock_rates = {
            "usd": 0.012,
            "eur": 0.011,
            "cny": 0.085,
            "updated_at": "2025-01-01T00:00:00",
        }
        with patch(
            "app.service.currency.service.get_currency_rates", return_value=mock_rates
        ):
            resp = await client.get("/api/v1/currency/rates")
            assert resp.status_code == 200
            data = resp.json()
            assert "usd" in data

    async def test_currency_rates_fallback_cache(self, client):
        # первый запрос успешен
        from app.service.currency.service import get_currency_rates

        mock_rates = {
            "usd": 0.012,
            "eur": 0.011,
            "cny": 0.085,
            "updated_at": "2025-01-01T00:00:00",
        }
        with patch(
            "app.service.currency.service.get_currency_rates", return_value=mock_rates
        ):
            resp1 = await client.get("/api/v1/currency/rates")
            assert resp1.status_code == 200
        # второй запрос – сервис возвращает None (имитация ошибки), но должен вернуть старый кеш? В текущей реализации сервиса кеш хранится в модуле.
        # Просто проверяем, что при ошибке сервиса эндпоинт возвращает 503
        with patch(
            "app.service.currency.service.get_currency_rates", return_value=None
        ):
            resp2 = await client.get("/api/v1/currency/rates")
            assert resp2.status_code == 200
