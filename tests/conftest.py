import asyncio
import logging

import pytest
import pytest_asyncio

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.pool import StaticPool
from app import app as application
from src.auth.security import auth_security
from src.core.base import Base
from src.core.connection import get_db
from src.users.models import User, Role

logging.basicConfig(level=logging.INFO)

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./sqlite_db.sqlite"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)

test_user = {"username": "deadpool", "email": "deadpool@example.com", "hashed_pwd": "123456789", "role_id": 1}

import pytest_asyncio


@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_models_wrap():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with TestingSessionLocal() as session:
        hashed_pwd = auth_security.get_password_hash(test_user["hashed_pwd"])
        role = Role(id=1, role_name="admin")
        user = User(
            username=test_user["username"],
            email=test_user["email"],
            hashed_pwd=hashed_pwd,
            role_id=test_user["role_id"]
        )
        session.add_all([role, user])
        await session.commit()


@pytest.fixture(scope="module")
def client():
    async def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        except Exception as err:
            await session.rollback()
            logging.error(err)
            raise
        finally:
            await session.close()

    application.dependency_overrides[get_db] = override_get_db

    yield TestClient(application)
