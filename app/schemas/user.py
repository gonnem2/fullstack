from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict, Field

from app.db.models.user import UserRoles
from app.schemas import dataclasses


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    day_expense_limit: Optional[float] = Field(1000)



class UserOut(BaseModel):
    """user из БД"""
    id: int
    username: str
    email: EmailStr
    day_expense_limit: float
    role: UserRoles = Field()

    model_config = ConfigDict(from_attributes=True)


class NewUserRole(BaseModel):
    user_role: UserRoles