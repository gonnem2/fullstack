import aiomcache

from app.core.settings import settings


def _to_bytes(data: str | bytes) -> bytes:
    """Приводит ключ/значение к bytes (utf-8 для str)."""
    if isinstance(data, bytes):
        return data
    return str(data).encode("utf-8")


class AsyncMemcached:
    """Асинхронный Memcached-клиент на базе aiomcache, с авто-encode/bytes."""

    def __init__(self, host: str, port: int) -> None:
        """Создаёт пул соединений к Memcached."""
        self._client = aiomcache.Client(host, port)

    async def get(self, key: str | bytes) -> bytes | None:
        return await self._client.get(_to_bytes(key))

    async def set(
        self,
        key: str | bytes,
        value: str | bytes,
        exptime: int = 0,
    ) -> bool:
        """SET: сохраняет значение с TTL (exptime, сек). True при успехе."""
        return await self._client.set(
            _to_bytes(key),
            _to_bytes(value),
            exptime=exptime,
        )

    async def delete(self, key: str | bytes) -> bool:
        """DELETE: удаляет ключ. True, если ключ был удалён."""
        return await self._client.delete(_to_bytes(key))

    async def close(self) -> None:
        """Закрывает соединения пула."""
        await self._client.close()

    async def add(
        self,
        key: str | bytes,
        value: str | bytes,
        exptime: int = 0,
    ) -> bool:
        """
        ADD: атомарно устанавливает значение ТОЛЬКО если ключа ещё нет.
        True — если успешно добавлен, False — если ключ уже существует.
        """
        try:
            return await self._client.add(
                _to_bytes(key),
                _to_bytes(value),
                exptime=exptime,
            )
        except aiomcache.exceptions.ClientException:
            return False

    async def incr(self, key: str | bytes, delta: int = 1) -> int:
        """
        INCR: атомарно увеличивает счётчик.
        """
        return await self._client.incr(_to_bytes(key), delta)


memcached_session = AsyncMemcached(
    host=settings.memcached_addr,
    port=settings.memcached_port,
)
