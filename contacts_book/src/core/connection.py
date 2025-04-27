import contextlib
import logging
from typing import AsyncGenerator

from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from contacts_book.src.core.config import configuration

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


async_sessionmanager = AsyncDatabaseSessionManager(configuration.ASYNC_DB_URL)
sync_sessionmanager = SyncDatabaseSessionManager(configuration.SYNC_DB_URL)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_sessionmanager.session() as session:
        yield session
