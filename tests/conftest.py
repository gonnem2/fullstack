import asyncio
import tempfile
import os

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.core.security import encode_password
from app.db.models.base import Base
from app.db.models import *
from app.db.database import get_db
from app.main import app
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.schemas.dataclasses.category import CategoryDTO

# Временный файл для БД (данные сохраняются между соединениями)
temp_db = tempfile.NamedTemporaryFile(delete=False)
TEST_DATABASE_URL = f"sqlite+aiosqlite:///{temp_db.name}"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = sessionmaker(
    bind=test_engine, class_=AsyncSession, expire_on_commit=False
)


async def override_get_db():
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_tables():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    os.unlink(temp_db.name)  # удаляем временный файл после тестов


@pytest_asyncio.fixture
async def db_session():
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client():
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# --- Данные для тестов ---
USER_DATA = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123",
}


@pytest_asyncio.fixture
async def registered_user(db_session):
    from app.db.models.user import User

    user = User(
        username=USER_DATA["username"],
        email=USER_DATA["email"],
        hashed_password=encode_password(USER_DATA["password"]),
        role="USER",
        day_expense_limit=1000.0,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_headers(client, registered_user):
    resp = await client.post(
        "/api/v1/auth/token",
        data={"username": USER_DATA["username"], "password": USER_DATA["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_user(db_session):
    from app.db.models.user import User

    admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password=encode_password("adminpass"),
        role="ADMIN",
        day_expense_limit=5000.0,
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


@pytest_asyncio.fixture
async def admin_headers(client, admin_user):
    resp = await client.post(
        "/api/v1/auth/token",
        data={"username": "admin", "password": "adminpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def expense_category(client, auth_headers):
    """Создаёт категорию expense через API."""
    resp = await client.post(
        "/api/v1/categories/",
        json={"title": "Еда", "type_of_category": "expense"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    resp = resp.json()
    return CategoryDTO(
        id=resp["id"],
        title=resp["title"],
        user_id=resp["user_id"],
        type_of_category=resp["type_of_category"],
    )


@pytest_asyncio.fixture
async def income_category(client, auth_headers):
    """Создаёт категорию income через API."""
    resp = await client.post(
        "/api/v1/categories/",
        json={"title": "Зарплата", "type_of_category": "income"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    resp = resp.json()
    return CategoryDTO(
        id=resp["id"],
        title=resp["title"],
        user_id=resp["user_id"],
        type_of_category=resp["type_of_category"],
    )


# --- Мок Memcached ---
class InMemoryMemcached:
    def __init__(self):
        self._store = {}

    async def set(self, key, value, exptime=0):
        self._store[key] = value.encode() if isinstance(value, str) else value
        return True

    async def get(self, key):
        return self._store.get(key)

    async def delete(self, key):
        self._store.pop(key, None)
        return True


@pytest.fixture(autouse=True)
def mock_memcached():
    from app.core.memcached.session import memcached_session

    fake = InMemoryMemcached()
    memcached_session.set = fake.set
    memcached_session.get = fake.get
    memcached_session.delete = fake.delete
    yield


@pytest_asyncio.fixture(autouse=True, scope="function")
async def recreate_tables():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
