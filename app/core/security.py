from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def encode_password(password: str) -> str:
    return pwd_context.hash(password)


def validate_password(password_from_user: str, hashed_password_from_db: str) -> bool:
    return pwd_context.verify(password_from_user, hashed_password_from_db)
