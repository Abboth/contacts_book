import asyncio
import logging

from fastapi_mail import FastMail, MessageSchema, MessageType
from fastapi_mail.errors import ConnectionErrors

from sqlalchemy.orm import Session

from contacts_book.src.auth.security import auth_security
from contacts_book.src.core.config import celery_app, mail_conf
from contacts_book.src.core.connection import sync_sessionmanager
from contacts_book.src.mail_services.prepare_letters_template import prepare_email_verification, prepare_password_reset
from contacts_book.src.mail_services import repository as mail_repository
from contacts_book.src.users import repository as user_repository
from contacts_book.src.users.models import User

logging.basicConfig(level=logging.INFO)


@celery_app.task
def send_email(email: str, host: str, email_type: str):
    asyncio.run(mail_processing(email, host, email_type))


async def mail_processing(email: str, host: str, email_type: str):
    with sync_sessionmanager.session() as db:
        user = user_repository.get_user_by_email_sync(email, db)
        letter_id = await mail_repository.draft_letter(user, db)
        if email_type == "verify":
            await verify_email(user, host, letter_id, db)
        elif email_type == "reset":
            await reset_password(user, host, letter_id, db)


async def verify_email(user: User, host: str, letter_id: int, db: Session):
    try:
        verification_token = await auth_security.create_email_token({"sub": user.email})
        tracking_token = await auth_security.create_tracking_token(letter_id)
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[user.email],
            template_body={"host": host,
                           "username": user.username,
                           "token": verification_token,
                           "tracking_token": tracking_token},
                    subtype=MessageType.html
        )
        fm = FastMail(mail_conf)
        template_data = await prepare_email_verification(user, host, verification_token, tracking_token)
        await fm.send_message(message, template_name=template_data.template_name)
        await mail_repository.letter_register(letter_id, template_data, db)
    except ConnectionErrors as err:
        logging.info(err)


async def reset_password(user: User, host: str, letter_id: int, db: Session):
    try:
        token_verification = await auth_security.create_email_token({"sub": user.email})
        tracking_token = await auth_security.create_tracking_token(letter_id)
        message = MessageSchema(
            subject="Reset you'r password",
            recipients=[user.email],
            template_body={"host": host,
                           "username": user.username,
                           "token": token_verification,
                           "tracking_token": tracking_token},
                    subtype=MessageType.html
        )
        fm = FastMail(mail_conf)
        await fm.send_message(message, template_name="reset_password_request.html")
        template_data = await prepare_password_reset(user, host, token_verification, tracking_token)
        await mail_repository.letter_register(letter_id, template_data, db)

    except ConnectionErrors as err:
        logging.info(err)


async def verification_letter(user: User, host: str):
    if user.is_verified:
        return {"message": "Your email is already confirmed"}

    mail_type = "verify"
    send_email.delay(user.email, host, mail_type)
    return {"message": "Check your email for confirmation."}
