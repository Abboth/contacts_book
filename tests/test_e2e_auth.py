from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock

import pytest
from fastapi_limiter import FastAPILimiter
from sqlalchemy import select

from src.auth.models import AuthSession
from src.auth.security import auth_security
from src.users.models import User
from tests.conftest import TestingSessionLocal, client
from src.core import message

user_data = {"username": "Abboth", "email": "Abboth@gmail.com", "password": "123456789", "role_id": 1}


def test_signup(client, monkeypatch):
    FastAPILimiter.redis = AsyncMock()
    FastAPILimiter.identifier = AsyncMock(return_value="test_limit")
    FastAPILimiter.http_callback = AsyncMock()

    mock_send_email = AsyncMock()
    monkeypatch.setattr("src.auth.routes.prepare_email_verification", mock_send_email)
    response = client.post("/auth/signup", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "avatar" in data
    assert "password" not in data
    assert mock_send_email.call_count == 1


def test_exists_signup(client, monkeypatch):
    FastAPILimiter.redis = AsyncMock()
    FastAPILimiter.identifier = AsyncMock(return_value="test_limit")
    FastAPILimiter.http_callback = AsyncMock()

    response = client.post("/auth/signup", json=user_data)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == message.ACCOUNT_EXIST


def test_login_not_confirmed(client):
    response = client.post("/auth/login", data={"username": user_data["email"], "password": user_data["password"]})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == message.EMAIL_NOT_CONFIRMED


@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(select(User).where(User.email == user_data["email"]))
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.is_verified = True
            await session.commit()

    response = client.post("/auth/login", data={"username": user_data["email"], "password": user_data["password"]})
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "token_type" in data


def test_login_invalid_password(client):
    response = client.post("/auth/login", data={"username": user_data["email"], "password": "invalid_password"})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == message.INVALID_PASSWORD


def test_login_invalid_email(client):
    response = client.post("/auth/login", data={"username": "invalid_email", "password": user_data["password"]})
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == message.USER_NOT_FOUNDED_BY_EMAIL


def test_get_refresh_token(client):
    response = client.post("/auth/login", data={"username": user_data["email"], "password": user_data["password"]})
    assert response.status_code == 200, response.text
    old_data = response.json()

    response = client.get("/auth/refresh_token", headers={"Authorization": f"Bearer {old_data['refresh_token']}"})
    assert response.status_code == 200, response.text
    new_data = response.json()
    assert old_data["access_token"] != new_data["access_token"]
    assert old_data["refresh_token"] != new_data["refresh_token"]
    assert "token_type" in new_data


def test_get_refresh_token_not_authenticated(client):
    response = client.get("/auth/refresh_token")
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_refresh_token_with_fake_credentials(client):
    fake_refresh_token = await auth_security.create_refresh_token(data={"sub": user_data["email"]})
    response = client.get(
        "/auth/refresh_token",
        headers={"Authorization": f"Bearer {fake_refresh_token}"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == message.BAD_CREDENTIALS

@pytest.mark.asyncio
async def test_refresh_token_no_session(client, monkeypatch):
    fake_token_data = await auth_security.create_refresh_token(data={"sub": user_data["email"]})
    fake_token = fake_token_data["token"]

    mock_user = AsyncMock()
    mock_user.email = user_data["email"]
    mock_user.auth_session = []

    mock_get_user_by_email = AsyncMock(return_value=mock_user)
    monkeypatch.setattr("src.users.repository.get_user_by_email", mock_get_user_by_email)

    response = client.get(
        "/auth/refresh_token",
        headers={"Authorization": f"Bearer {fake_token}"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == message.INVALID_TOKEN