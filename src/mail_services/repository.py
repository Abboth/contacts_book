from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.core.connection import sync_sessionmanager
from src.core import message
from src.users.models import User
from src.mail_services.models import Email, EmailTemplates

async def draft_letter(user: User, db: AsyncSession) -> int:
    """
    Create a draft email letter for the given user.

    :param user: Authenticated user.
    :type user: User
    :param db: Database session.
    :type db: Session
    :return: ID of the created draft letter.
    :rtype: int
    """

    new_letter = Email(
        user_id=user.id,
        template_id=1,
    )
    db.add(new_letter)
    await db.flush()
    mail_id = new_letter.id
    return mail_id

def get_letter_by_id_sync(mail_id: int, db: Session) -> Email:
    """
    Retrieve a letter by its ID (synchronous version for celery).

    :param mail_id: ID of the letter.
    :type mail_id: int
    :param db: Database session.
    :type db: Session
    :return: Email object if found, else None.
    :rtype: Email | None
    """

    stmt = select(Email).where(Email.id == mail_id)
    result = db.execute(stmt)
    letter = result.scalar_one_or_none()

    return letter

async def get_letter_by_id_async(mail_id: int, db: AsyncSession) -> Email:
    """
    Retrieve a letter by its ID (asynchronous version).

    :param mail_id: ID of the letter.
    :type mail_id: int
    :param db: Asynchronous database session.
    :type db: AsyncSession
    :return: Email object if found, else None.
    :rtype: Email | None
    """

    stmt = select(Email).where(Email.id == mail_id)
    result = await db.execute(stmt)
    letter = result.scalar_one_or_none()

    return letter

def get_or_create_template(template_data: dict, db: Session) -> EmailTemplates:
    """
    Retrieve an existing template by name or create a new one.

    :param template_data: dict with template name, subject, and params.
    :type template_data: dict
    :param db: Database session.
    :type db: Session
    :return: Existing or newly created template.
    :rtype: EmailTemplates
    """

    name = template_data["template_name"]
    stmt = select(EmailTemplates).where(EmailTemplates.name == name)
    result = db.execute(stmt)
    template = result.scalar_one_or_none()
    if template:
        return template

    template = EmailTemplates(name=template_data["template_name"],
                              subject=template_data["subject"],
                              params=template_data["params"])
    db.add(template)
    db.commit()
    db.refresh(template)

    return template


async def mark_letter_as_opened(mail_id: int, db: AsyncSession) -> None:
    """
    Mark a letter as opened by updating its status.

    :param mail_id: ID of the letter.
    :type mail_id: int
    :param db: Asynchronous database session.
    :type db: AsyncSession
    :return: None
    :rtype: None
    """

    letter = await get_letter_by_id_async(mail_id, db)
    if not letter.opened:
        letter.opened = True
        await db.commit()


async def letter_register(letter_id: int, template_data: dict) -> None:
    """
    Assign a template to a letter and mark it as sent.

    :param letter_id: ID of the letter to register.
    :type letter_id: int
    :param template_data: dict of data to use.
    :type template_data: dict
    :param db: Database session.
    :type db: Session
    :return: None
    :rtype: None
    :raises Exception: If the draft letter is not found.
    """
    with sync_sessionmanager.session() as db:
        template = get_or_create_template(template_data, db)

        letter = get_letter_by_id_sync(letter_id, db)
        if letter:
            letter.template_id = template.id
            letter.status = "sent"
            db.commit()

        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message.DRAFT_LETTER_NOT_FOUND)