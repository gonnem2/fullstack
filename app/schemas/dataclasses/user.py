from dataclasses import dataclass


@dataclass
class UserDTO:
    id: int
    username: str
    email: str
    hashed_password: str
    day_expense_limit: float
