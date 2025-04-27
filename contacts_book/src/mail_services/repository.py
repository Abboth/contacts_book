from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from contacts_book.src.mail_services.schemas import EmailTemplateSchema
from contacts_book.src.users.models import User
from contacts_book.src.mail_services.models import Email, EmailTemplates

async def draft_letter(user: User, db: Session):
    new_letter = Email(
        user_id=user.id,
        template_id=1,
    )
    db.add(new_letter)
    db.flush()
    mail_id = new_letter.id
    return mail_id

def get_letter_by_id_sync(mail_id: int, db: Session):
    stmt = select(Email).where(Email.id == mail_id)
    result = db.execute(stmt)
    letter = result.scalar_one_or_none()

    return letter

async def get_letter_by_id_async(mail_id: int, db: AsyncSession):
    stmt = select(Email).where(Email.id == mail_id)
    result = await db.execute(stmt)
    letter = result.scalar_one_or_none()

    return letter

async def get_or_create_template(template_data: EmailTemplateSchema, db: Session):
    name = template_data.template_name
    stmt = select(EmailTemplates).where(EmailTemplates.name == name)
    result = db.execute(stmt)
    template = result.scalar_one_or_none()
    if template:
        return template

    template = EmailTemplates(name=template_data.template_name,
                              subject=template_data.subject,
                              params=template_data.params)
    db.add(template)
    db.commit()
    db.refresh(template)

    return template


async def mark_letter_as_opened(mail_id: int, db: AsyncSession):
    letter: Email = await get_letter_by_id_async(mail_id, db)
    if letter:
        letter.opened = True
        await db.commit()


async def letter_register(letter_id: int, template_data: EmailTemplateSchema, db: Session):
    template = await get_or_create_template(template_data, db)

    letter = get_letter_by_id_sync(letter_id, db)
    if letter:
        letter.template_id = template.id
        letter.status = "sent"
        db.commit()

    else:
        raise Exception("Letter draft not found")