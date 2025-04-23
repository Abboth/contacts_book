from datetime import datetime, timedelta

from fastapi import HTTPException, status

from sqlalchemy import exists, extract, cast, Date, Integer
from sqlalchemy.sql import func, literal
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from contacts_book.src.contacts.models import Email, Phone, Contact
from contacts_book.src.contacts.schemas.request_schema import AddContactSchema, ContactUpdateSchema, PhoneUpdateSchema, \
    EmailUpdateSchema, AddPhoneSchema, AddEmailSchema
from contacts_book.src.users.models import User


async def show_all_contacts(limit: int, user: User, db: AsyncSession):
    stmt = select(Contact).where(Contact.user_id == user.id).limit(limit)
    result = await db.execute(stmt)
    contacts = result.scalars().all()

    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="You dont have any contacts yet")

    return contacts


async def get_contact_by_id(contact_id: int, user: User, db: AsyncSession):
    stmt = select(Contact).where(Contact.id == contact_id, Contact.user_id == user.id)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()

    if contact is None:
        raise HTTPException(status_code=404, detail="Contact with this ID not found in your's contact book")

    return contact


async def get_contact_by_name(name: str, user: User, db: AsyncSession):
    stmt = select(Contact).where(Contact.first_name.ilike("%" + name + "%"), Contact.user_id == user.id)
    result = await db.execute(stmt)
    contact = result.scalars().all()

    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not found any contacts with name like {name}")

    return contact


async def add_contact(body: AddContactSchema, user: User, db: AsyncSession):
    contact = Contact(
        first_name=body.first_name,
        last_name=body.last_name,
        birthday=body.birthday,
        description=body.description,
        user_id=user.id
    )

    if body.email:
        contact.email.append(Email(email=body.email, tag=body.mail_tag))
    if body.phone_number:
        contact.phones.append(Phone(phone=body.phone_number, tag=body.phone_tag))

    db.add(contact)
    await db.commit()
    await db.refresh(contact)

    new_contact = get_contact_by_id(contact.id, user, db)

    return new_contact


async def update_contact(body: ContactUpdateSchema, contact_id: int, user: User, db: AsyncSession):
    contact = get_contact_by_id(contact_id, user, db)

    contact.first_name = body.first_name
    contact.last_name = body.last_name
    contact.description = body.description
    if not contact.birthday:
        contact.birthday = body.birthday

    await db.commit()
    await db.refresh(contact)

    return contact


async def add_phone(body: AddPhoneSchema, contact_id: int, user: User, db: AsyncSession):
    contact = get_contact_by_id(contact_id, user, db)

    tag_exists = await db.scalar(
        select(exists()
               .where(Phone.tag == body.phone_tag,
                      Phone.contact_id == contact_id)
               )
    )

    if tag_exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="This tag already used for this contact")

    phone = Phone(phone=body.phone_number,
                  tag=body.phone_tag,
                  contact_id=contact_id)
    db.add(phone)
    await db.commit()
    await db.refresh(contact)

    return contact


async def update_phone(body: PhoneUpdateSchema, contact_id: int, tag: str, user: User, db: AsyncSession):
    contact = get_contact_by_id(contact_id, user, db)

    stmt = select(Phone).where(Phone.contact_id == contact_id).filter(Phone.tag == tag)
    result = await db.execute(stmt)
    contact_phone = result.scalar_one_or_none()

    if not contact_phone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Phone with given tag not found for this contact")

    contact_phone.phone = str(body.phone_number)

    await db.commit()
    await db.refresh(contact)

    return contact


async def add_email(body: AddEmailSchema, contact_id: int, user: User, db: AsyncSession):
    contact = get_contact_by_id(contact_id, user, db)

    tag_exists = await db.scalar(
        select(exists()
               .where(Email.tag == body.mail_tag)
               .where(Email.contact_id == contact_id)
               )
    )

    if tag_exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="This tag already used for this contact")

    email = Email(email=body.email,
                  tag=body.mail_tag,
                  contact_id=contact_id)
    db.add(email)
    await db.commit()
    await db.refresh(contact)

    return contact


async def update_email(body: EmailUpdateSchema, contact_id: int, tag: str, user: User, db: AsyncSession):
    contact = get_contact_by_id(contact_id, user, db)

    stmt = select(Email).where(Email.contact_id == contact_id).filter(Email.tag == tag)
    result = await db.execute(stmt)
    contact_email = result.scalar_one_or_none()

    if not contact_email:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Email with given tag not found for this contact")

    contact_email.email = str(body.email)

    await db.commit()
    await db.refresh(contact)

    return contact


async def get_contacts_birthday(user: User, db: AsyncSession):
    today = datetime.now().date()
    days_range_check = today + timedelta(days=7)

    birthday_this_year = func.make_date(
        literal(today.year),
        cast(extract("month", Contact.birthday), Integer),
        cast(extract("day", Contact.birthday), Integer)
    )

    stmt = select(Contact).where(cast(birthday_this_year, Date).
                                 between(today, days_range_check), Contact.user_id == user.id)

    birthdays = await db.execute(stmt)

    return birthdays.scalars().all()


async def delete_contact(contact_id: int, user: User, db: AsyncSession):
    contact = get_contact_by_id(contact_id, user, db)

    if contact:
        await db.delete(contact)
        await db.commit()

    return contact
