import asyncio
import logging

from fastapi_mail import FastMail, MessageSchema, MessageType
from fastapi_mail.errors import ConnectionErrors

from src.core.connection import celery_app, mail_conf
from src.mail_services import repository as mail_repository

logging.basicConfig(level=logging.INFO)


@celery_app.task
def celery_task_email(email: str, letter_id, template_data: dict):
    """
    Celery task that sends an email using asynchronous processing.

    :param email: Recipient's email address.
    :type email: str
    :param letter_id: ID of the drafted letter for tracking and logging.
    :type letter_id: int
    :param template_data: Email content, template name, and params.
    :type template_data: dict
    :return: None
    :rtype: None
    """
    asyncio.run(email_processing(email, letter_id, template_data))



async def email_processing(email: str, letter_id: int, template_data: dict):
    """
    Process the email sending asynchronously using FastMail.

    :param email: Recipient's email address.
    :type email: str
    :param letter_id: ID of the drafted letter for tracking and logging.
    :type letter_id: int
    :param template_data: Email content, subject, template name, and params.
    :type template_data: dict
    :return: None
    :rtype: None
    """

    try:
        message = MessageSchema(
            subject=template_data["subject"],
            recipients=[email],
            template_body=template_data["params"],
                    subtype=MessageType.html
        )
        fm = FastMail(mail_conf)
        await fm.send_message(message, template_name=template_data["template_name"])
        await mail_repository.letter_register(letter_id, template_data)

    except ConnectionErrors as err:
        logging.info(err)


