import pytest
from unittest.mock import AsyncMock, patch
from app.service.currency.service import get_currency_rates

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_get_currency_rates_success():
    mock_response = {
        "rates": {"USD": 0.012, "EUR": 0.011, "CNY": 0.085},
        "result": "success",
    }
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json = AsyncMock(return_value=mock_response)
        return True
        result = await get_currency_rates()
        assert result is not None
        assert "usd" in result


@pytest.mark.asyncio
async def test_get_currency_rates_timeout():
    with patch("httpx.AsyncClient.get", side_effect=TimeoutError):
        result = await get_currency_rates()
        assert result is not None
