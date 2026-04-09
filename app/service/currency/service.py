"""
Сервис получения курсов валют через сторонний API.
Используется бесплатный API: https://open.er-api.com (не требует ключа для базового использования).
Настройка через переменные окружения: CURRENCY_API_KEY (если потребуется).
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

# Кешируем курсы, чтобы не спамить внешний API
_cache: dict = {"data": None, "expires_at": 0.0}

EXTERNAL_API_URL = "https://open.er-api.com/v6/latest/RUB"
TIMEOUT_SECONDS = 5
CACHE_TTL_SECONDS = 3600  # 1 час


async def get_currency_rates() -> Optional[dict]:
    """
    Возвращает курсы USD, EUR, CNY к рублю.
    Результат кешируется на 1 час.
    При ошибке внешнего API возвращает None (graceful degradation).
    """
    now = time.monotonic()

    # Отдаём из кеша, если актуально
    if _cache["data"] is not None and now < _cache["expires_at"]:
        return _cache["data"]

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            response = await client.get(EXTERNAL_API_URL)
            response.raise_for_status()
            raw = response.json()
    except httpx.TimeoutException:
        logger.warning("Currency API timeout")
        return _cache["data"]  # вернём старый кеш, если есть
    except httpx.HTTPStatusError as e:
        logger.warning("Currency API HTTP error: %s", e)
        return _cache["data"]
    except Exception as e:
        logger.warning("Currency API error: %s", e)
        return _cache["data"]

    rates = raw.get("rates", {})

    # Курсы в ответе: сколько RUB за 1 USD/EUR/CNY → инвертируем
    def safe_rate(code: str) -> Optional[float]:
        r = rates.get(code)
        if r and r != 0:
            return round(1 / r, 4)  # 1 RUB = 1/r CODE → 1 CODE = r RUB
        return None

    # Проверяем структуру: open.er-api с base=RUB уже даёт "сколько RUB за единицу",
    # но если base=RUB, то rates[USD] = 0.011... (1 RUB = 0.011 USD)
    # → нам нужно сколько RUB стоит 1 USD = 1 / rates[USD]
    result = {
        "usd": safe_rate("USD"),
        "eur": safe_rate("EUR"),
        "cny": safe_rate("CNY"),
        "updated_at": datetime.utcnow().isoformat(),
    }

    _cache["data"] = result
    _cache["expires_at"] = now + CACHE_TTL_SECONDS

    return result
