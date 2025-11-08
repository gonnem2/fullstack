from pydantic import BaseModel, EmailStr, ConfigDict


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    day_expense_limit: float



class UserOut(BaseModel):
    """user из БД"""
    id: int
    username: str
    email: EmailStr
    hashed_password: str
    day_expense_limit: float

    model_config = ConfigDict(from_attributes=True)
