from pydantic import BaseModel, EmailStr, ConfigDict


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str



class UserOut(BaseModel):
    """user из БД"""
    id: int
    username: str
    email: EmailStr
    hashed_password: str

    model_config = ConfigDict(from_attributes=True)
