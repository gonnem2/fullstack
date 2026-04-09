"""
Роутер для получения курсов валют.
GET /api/v1/currency/rates — возвращает курсы USD, EUR, CNY к рублю.
"""

from fastapi import APIRouter, HTTPException

from app.service.currency.service import get_currency_rates

router = APIRouter(prefix="/currency", tags=["Currency"])


@router.get("/rates", summary="Получить курсы валют к рублю")
async def currency_rates():
    """
    Возвращает актуальные курсы USD, EUR, CNY к рублю.
    Данные кешируются на 1 час. При недоступности внешнего API — 503.
    """
    rates = await get_currency_rates()
    if rates is None:
        raise HTTPException(
            status_code=503, detail="Сервис курсов валют временно недоступен"
        )
    return rates
