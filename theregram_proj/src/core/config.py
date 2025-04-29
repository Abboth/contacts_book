from pydantic import ConfigDict, EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY_JWT: str = "eqwiubfe"
    ALGORITHM: str = "HS256"

    POSTGRES_ASYNC_URL: str = "postgresql+asyncpg://postgres:12345@localhost:5432/qqq"
    POSTGRES_SYNC_URL: str = "postgresql+psycopg2://postgres:12345@localhost:5432/qqq"

    MAIL_USERNAME: str = "theregram@gmail.com"
    MAIL_PASSWORD: str = "qwerty"
    MAIL_FROM: EmailStr = "theregram@gmail.com"
    MAIL_PORT: int = 44422
    MAIL_SERVER: str = "gmail"
    MAIL_FROM_NAME: str = "theregram"
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = False
    VALIDATE_CERTS: bool = False
    TEMPLATE_FOLDER: str = "./template"

    REDIS_DOMAIN: str = "redis"
    REDIS_PORT: int = 21342
    REDIS_PWD: str | None = None
    REDIS_URL: str = "redis://redis:0000/0"

    CLOUDINARY_CLOUD: str = "unidfiunwqea"
    CLOUDINARY_API_KEY: int = 998584823489192
    CLOUDINARY_SECRET_KEY: str = "M9JQWEOJUNasfndWUawW0"
    CLOUDINARY_SECURE: bool = True
    CLOUDINARY_URL: str = "cloudinary://991232532532:Moujnw3123UW123ssw249640@dqveqtvreywk?secure=True"

    model_config = ConfigDict(extra='ignore', env_file=".env", env_file_decoding="utf-8")  # noqa


configuration = Settings()
