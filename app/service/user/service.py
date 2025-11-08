from sqlalchemy.ext.asyncio import AsyncSession

from app.db import User
from app.schemas.dataclasses.user import UserDTO
from app.service.user import crud as user_crud


class UserService:
    """Сервис бизнес логики юзера"""

    async def change_user_expense_limit(
        self, db: AsyncSession, user: User, new_limit: float
    ) -> UserDTO:
        """Изменяет дневной лимит трат"""

        changed_user = await user_crud.change_expense_limit(db, user, new_limit)
        return changed_user
