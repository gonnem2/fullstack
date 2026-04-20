# ── Базовый образ ────────────────────────────────────────────────────────────
FROM python:3.13-slim

WORKDIR /app

# Устанавливаем системные зависимости (необходимы для работы приложения)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libcairo2 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем uv (менеджер пакетов)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Копируем файл с зависимостями и исходный код
COPY pyproject.toml ./
COPY . .

# Устанавливаем все зависимости и сам проект (аналог pip install -e .)
RUN uv pip install --system .

# Переключаемся на непривилегированного пользователя
RUN useradd -m -u 1001 appuser && chown -R appuser:appuser /app
USER 1001

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]