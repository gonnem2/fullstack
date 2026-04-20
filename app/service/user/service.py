from sqlalchemy.ext.asyncio import AsyncSession

from app.db import User
from app.db.models.user import UserRoles
from app.schemas.dataclasses.user import UserDTO
from app.service.user import crud as user_repo
from app.service.user.exception import UserNotFoundException


class UserService:
    """Сервис бизнес логики юзера"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def change_user_expense_limit(self, user: User, new_limit: float) -> UserDTO:
        """Изменяет дневной лимит трат"""

        changed_user = await user_repo.change_expense_limit(db, user, new_limit)
        return changed_user

    async def change_user_role(self, user_id: int, new_user_role: UserRoles) -> None:
        """Меняет роль пользователя на переданную"""
        # проверяем существует ли юзер вообще
        user_exists: UserDTO | None = await user_repo.get_user_by_id(
            session=self.session, user_id=user_id
        )

        if not user_exists:
            raise UserNotFoundException("Пользователь не найден")

        _ = await user_repo.change_user_role(
            session=self.session, user_id=user_id, new_user_role=new_user_role
        )

    async def get_all_users(self, skip: int, limit: int) -> list[UserDTO]:
        """Возвращает список всех пользователей"""

        users: list[UserDTO | None] = await user_repo.get_all_users(
            session=self.session, skip=skip, limit=limit
        )
        return users
