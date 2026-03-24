from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.settings import settings

async_engine = create_async_engine(url=settings.DB_URL, echo=False)
_async_session = async_sessionmaker(async_engine, class_=AsyncSession)


async def get_db() -> AsyncGenerator[AsyncSession, None]:

    async with async_session() as session:
        yield session


@asynccontextmanager
async def async_session():
    async with _async_session() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError:
            await session.rollback()
            raise
        finally:
            await session.close()
