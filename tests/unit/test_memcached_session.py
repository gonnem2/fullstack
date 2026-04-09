import pytest
from unittest.mock import AsyncMock, patch
from app.core.memcached.session import memcached_session


@pytest.mark.asyncio
async def test_memcached_set_get():
    # используем реальный мок из conftest (InMemoryMemcached)
    await memcached_session.set("key", "value")
    result = await memcached_session.get("key")
    assert result == b"value"


@pytest.mark.asyncio
async def test_memcached_delete():
    await memcached_session.set("key2", "val")
    await memcached_session.delete("key2")
    result = await memcached_session.get("key2")
    assert result is None
