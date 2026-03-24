from app.db.database import async_session
from . import crud as auth_repo


async def create_admin_user():
    """
    Создает админ пользователя, если его нет.
    """
    async with async_session() as session:
        await auth_repo.create_admin_user(session)


startup_callbacks = [
    create_admin_user,
]
