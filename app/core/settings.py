import os

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    DB_URL: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    SECRET_KEY: str
    ALGORITHM: str
    admin_username: str = Field("admin", alias="ADMIN_USERNAME")
    admin_password: str = Field("1111", alias="ADMIN_PASSWORD")
    memcached_addr: str = Field("127.0.0.1", alias="MEMCACHE_ADDR")
    memcached_port: str = Field("11211", alias="MEMCACHE_PORT")

    class Config:
        env_file = ".env"


settings = Settings()
