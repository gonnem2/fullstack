# FinanceTrack — Развёртывание (Лаб. 6)

## Быстрый старт

```bash
# 1. Клонировать репозиторий
git clone https://github.com/youruser/financetrack.git
cd financetrack

# 2. Создать .env из шаблона и заполнить
cp .env.example .env
nano .env

# 3. Запустить весь стек
docker compose up -d

# 4. Открыть в браузере
#    Приложение:  http://localhost
#    MinIO:       http://localhost:9001
```

## Запуск тестов локально

```bash
# Backend
docker compose -f docker-compose.test.yml up backend_test --build

# Frontend
docker compose -f docker-compose.test.yml up frontend_test

# Или без Docker:
cd backend && pytest tests/ -v
cd frontend && npm run test:coverage
```

## Структура сервисов

```
nginx (80) ──→ frontend (React/Nginx :80)
           └──→ backend (FastAPI :8000)
                    ├──→ postgres (:5432)
                    ├──→ memcached (:11211)
                    └──→ minio (:9000)
```

## GitHub Secrets (нужны для деплоя)

| Secret            | Описание                        |
|-------------------|---------------------------------|
| `DEPLOY_HOST`     | IP/домен сервера                |
| `DEPLOY_USER`     | SSH-пользователь                |
| `DEPLOY_SSH_KEY`  | Приватный SSH-ключ              |

`GITHUB_TOKEN` — предоставляется GitHub автоматически.

## CI/CD пайплайн

```
push → backend-tests (pytest)
     → frontend-tests (npm run test:coverage)
     ↓ (оба прошли)
     → build (Docker images → ghcr.io)
     ↓ (только main)
     → deploy (SSH → docker compose pull && up)
```
