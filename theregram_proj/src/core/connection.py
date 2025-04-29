import contextlib
import logging
from typing import AsyncGenerator

from celery import Celery
from fastapi_mail import ConnectionConfig
from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import cloudinary

from theregram_proj.src.core.config import configuration

logging.basicConfig(level=logging.INFO)


class AsyncDatabaseSessionManager:
    def __init__(self, url: str):
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(autoflush=False, autocommit=False,
                                                                     bind=self._engine)

    @contextlib.asynccontextmanager
    async def session(self):
        if self._session_maker is None:
            raise Exception("Session not initialized")
        session = self._session_maker()
        try:
            yield session
        except Exception as err:
            logging.info(err)
            await session.rollback()
            raise
        finally:
            await session.close()


class SyncDatabaseSessionManager:
    def __init__(self, url: str):
        self._engine: Engine | None = create_engine(url)
        self._session_maker: sessionmaker = sessionmaker(autoflush=False, autocommit=False,
                                                         bind=self._engine)

    @contextlib.contextmanager
    def session(self):
        if self._session_maker is None:
            raise Exception("Session not initialized")
        session = self._session_maker()
        try:
            yield session
        except Exception as err:
            logging.info(err)
            session.rollback()
            raise
        finally:
            session.close()


async_sessionmanager = AsyncDatabaseSessionManager(configuration.POSTGRES_ASYNC_URL)
sync_sessionmanager = SyncDatabaseSessionManager(configuration.POSTGRES_SYNC_URL)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_sessionmanager.session() as async_session:
        yield async_session


def my_celery_task():
    with sync_sessionmanager.session() as sync_session:
        yield sync_session


celery_app = Celery(
    "theregram_proj",
    broker=configuration.REDIS_URL,
    backend=configuration.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)


mail_conf = ConnectionConfig(
    MAIL_USERNAME=configuration.MAIL_USERNAME,
    MAIL_PASSWORD=configuration.MAIL_PASSWORD,
    MAIL_FROM=configuration.MAIL_FROM,
    MAIL_PORT=configuration.MAIL_PORT,
    MAIL_SERVER=configuration.MAIL_SERVER,
    MAIL_FROM_NAME=configuration.MAIL_FROM_NAME,
    MAIL_STARTTLS=configuration.MAIL_STARTTLS,
    MAIL_SSL_TLS=configuration.MAIL_SSL_TLS,
    USE_CREDENTIALS=configuration.USE_CREDENTIALS,
    VALIDATE_CERTS=configuration.VALIDATE_CERTS,
    TEMPLATE_FOLDER=configuration.TEMPLATE_FOLDER,
)
