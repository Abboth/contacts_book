import os
from pathlib import Path
from pydantic import EmailStr, SecretStr
from dotenv import load_dotenv
from celery import Celery
from fastapi_mail import ConnectionConfig


load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "default-unsafe-key")
    ASYNC_DB_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/bday_bot_DB"
    SYNC_DB_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/bday_bot_DB"


configuration = Config

celery_app = Celery(
    "contacts_book",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

mail_conf = ConnectionConfig(
    MAIL_USERNAME="alexmikhailov90@gmail.com",
    MAIL_PASSWORD="uzvt ftag mhkn tnee",
    MAIL_FROM="alexmikhailov90@gmail.com",
    MAIL_PORT=465,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_FROM_NAME="contacts service",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / 'templates',
)