import pytest

from unittest.mock import Mock, AsyncMock

from fastapi import Form
from sqlalchemy import select

from src.auth.security import auth_security
from src.core import message
from src.mail_services.models import Email, EmailTemplates
from src.users.repository import get_user_by_email
from tests.conftest import TestingSessionLocal, client

test_user = {"username": "deadpool", "email": "deadpool@example.com", "hashed_pwd": "123456789", "role_id": 1}


@pytest.mark.asyncio
async def test_confirm_email(client):
    fake_token = await auth_security.create_email_token({"sub": test_user["email"]})

    response = client.get(f"/service/confirm_email/{fake_token}")
    async with TestingSessionLocal() as session:
        user = await get_user_by_email(test_user["email"], session)

    assert response.status_code == 200, response.text
    assert user.is_verified == True
    assert response.json() == {"message": "Email confirmed"}


@pytest.mark.asyncio
async def test_email_already_confirmed(client):
    fake_token = await auth_security.create_email_token({"sub": test_user["email"]})

    response = client.get(f"/service/confirm_email/{fake_token}")
    async with TestingSessionLocal() as session:
        user = await get_user_by_email(test_user["email"], session)

    assert response.status_code == 200, response.text
    assert user.is_verified == True
    assert response.json() == {"message": "Your email is already confirmed"}


@pytest.mark.asyncio
async def test_email_confirm_for_not_exist_user(client):
    fake_token = await auth_security.create_email_token({"sub": "fake@gmail.com"})

    response = client.get(f"/service/confirm_email/{fake_token}")
    data = response.json()
    assert response.status_code == 404
    assert data["detail"] == message.USER_NOT_FOUNDED_BY_EMAIL


@pytest.mark.asyncio
async def test_verify_request_already_confirmed(client, monkeypatch):
    async with TestingSessionLocal() as session:
        user = await get_user_by_email(test_user["email"], session)

    mock_send_email = AsyncMock()
    monkeypatch.setattr("src.mail_services.routes.prepare_email_verification", mock_send_email)

    response = client.post("/service/verify_request/", json={"email": test_user["email"]})

    assert response.status_code == 200, response.text
    assert response.json() == {"message": "Your email is already confirmed"}
    assert mock_send_email.call_count == 0


@pytest.mark.asyncio
async def test_verify_request(client, monkeypatch):
    async with TestingSessionLocal() as session:
        user = await get_user_by_email(test_user["email"], session)
        user.is_verified = False
        await session.commit()

    mock_send_email = AsyncMock()
    monkeypatch.setattr("src.mail_services.routes.prepare_email_verification", mock_send_email)

    response = client.post("/service/verify_request/", json={"email": test_user["email"]})

    assert response.status_code == 200, response.text
    assert response.json() == {"message": "Check your email for confirmation."}
    assert mock_send_email.call_count == 1


def test_password_change_request(client, monkeypatch):
    mock_pwd_reset_request = AsyncMock()
    monkeypatch.setattr("src.mail_services.routes.prepare_password_reset", mock_pwd_reset_request)

    response = client.post("/service/reset_password/", json={"email": test_user["email"]})

    assert response.status_code == 200, response.text
    assert response.json() == {"message": "Password reset form has been sent to your email."}
    assert mock_pwd_reset_request.call_count == 1


@pytest.mark.asyncio
async def test_password_change(client):
    fake_token = await auth_security.create_email_token({"sub": test_user["email"]})
    new_password = "new_pwd"

    async with TestingSessionLocal() as session:
        old_user_data = await get_user_by_email(test_user["email"], session)

    response = client.patch(f"/service/reset_password/{fake_token}",
                            data={"new_password": new_password, "repeat_password": new_password})
    async with TestingSessionLocal() as session:
        new_user_data = await get_user_by_email(test_user["email"], session)
    assert old_user_data.hashed_pwd != new_user_data.hashed_pwd
    assert new_user_data != new_password
    assert response.status_code == 200, response.text


@pytest.mark.asyncio
async def test_password_change_different_input_passwords(client):
    fake_token = await auth_security.create_email_token({"sub": test_user["email"]})

    response = client.patch(f"/service/reset_password/{fake_token}",
                            data={"new_password": "new_password", "repeat_password": "wrong_password"})
    assert response.status_code == 400
    assert response.json()["detail"] == message.PASSWORD_NOT_MATCH


@pytest.mark.asyncio
async def test_letter_opened_by_user(client):
    async with TestingSessionLocal() as session:
        template = EmailTemplates(name="test", subject="test", params={"test": "test"})
        letter = Email(user_id=1, template_id=1)
        session.add_all([template, letter])
        await session.commit()
        await session.refresh(letter)
        tracking_token = await auth_security.create_tracking_token(letter.id)

        response = client.get(f"/service/mark_open/{tracking_token}")
        await session.refresh(letter)

        assert response.status_code == 200
        assert letter.opened == True