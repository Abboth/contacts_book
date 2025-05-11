from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.security import auth_security
from src.mail_services.repository import draft_letter
from src.users.models import User
from src.mail_services.service import celery_task_email


async def prepare_email_verification(user: User, host: str, db: AsyncSession):
    """
    Prepare email verification letter and send to Celery.

    :param user: The user object requiring verification.
    :type user: User
    :param host: Base URL used to build verification link.
    :type host: str
    :param db: The database session.
    :type db: AsyncSession
    :return: None
    :rtype: None
    """

    letter_id = await draft_letter(user, db)
    token = await auth_security.create_email_token({"sub": user.email})
    tracking_token = await auth_security.create_tracking_token(letter_id)
    template_data = {
        "subject": "Confirm your email",
        "template_name": "email_verification.html",
        "params": {"host": host, "username": user.username, "token": token, "tracking_token": tracking_token}}

    celery_task_email.delay(user.email, letter_id, template_data)


async def prepare_password_reset(user: User, host: str, db: AsyncSession):
    """
    Prepare a password reset email and send to Celery.

    :param user: The user object requesting password reset.
    :type user: User
    :param host: Base URL used to build password reset link.
    :type host: str
    :param db: The database session.
    :type db: AsyncSession
    :return: None
    :rtype: None
    """

    letter_id = await draft_letter(user, db)
    token = await auth_security.create_email_token({"sub": user.email})
    tracking_token = await auth_security.create_tracking_token(letter_id)
    template_data = {
        "subject": "Reset your password",
        "template_name": "reset_password_request.html",
        "params": {"host": host, "username": user.username, "token": token, "tracking_token": tracking_token}}

    celery_task_email.delay(user.email, letter_id, template_data)
