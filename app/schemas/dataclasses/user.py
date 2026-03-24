from dataclasses import dataclass

from app.db.models.user import UserRoles


@dataclass
class UserDTO:
    id: int
    username: str
    email: str
    hashed_password: str
    role: UserRoles
    day_expense_limit: float
