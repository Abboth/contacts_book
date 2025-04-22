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


async def show_all_contacts(limit: int, db: AsyncSession):
    stmt = select(Contact).limit(limit).options(
        selectinload(Contact.email),
        selectinload(Contact.phones)
    )
    result = await db.execute(stmt)
    contacts = result.scalars().all()

    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="You dont have any contacts yet")

    return contacts


async def get_contact_by_id(contact_id: int, db: AsyncSession):
    stmt = select(Contact).where(Contact.id == contact_id).options(
        selectinload(Contact.email),
        selectinload(Contact.phones)
    )
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()

    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    return contact


async def get_contact_by_name(name: str, db: AsyncSession):
    stmt = select(Contact).where(Contact.first_name.ilike("%" + name + "%")).options(
        selectinload(Contact.email),
        selectinload(Contact.phones)
    )
    result = await db.execute(stmt)
    contact = result.scalars().all

    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not found any contacts with name like {name}")

    return contact


async def add_contact(body: AddContactSchema, db: AsyncSession):
    contact = Contact(
        first_name=body.first_name,
        last_name=body.last_name,
        birthday=body.birthday,
        description=body.description
    )

    if body.email:
        contact.email.append(Email(email=body.email, tag=body.mail_tag))
    if body.phone_number:
        contact.phones.append(Phone(phone=body.phone_number, tag=body.phone_tag))

    db.add(contact)
    await db.commit()
    await db.refresh(contact)

    stmt = (select(Contact).where(Contact.id == contact.id).options(
        selectinload(Contact.email),
        selectinload(Contact.phones)
    ))
    result = await db.execute(stmt)

    return result.scalar_one()


async def update_contact(body: ContactUpdateSchema, contact_id: id, db: AsyncSession):
    stmt = select(Contact).where(Contact.id == contact_id)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()

    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Contact with this ID not found")

    contact.first_name = body.first_name
    contact.last_name = body.last_name
    contact.description = body.description
    if not contact.birthday:
        contact.birthday = body.birthday

    await db.commit()
    updated_contact = await db.execute(
        stmt.options(selectinload(Contact.email), selectinload(Contact.phones)
                     )
    )

    return updated_contact.scalar_one_or_none()


async def add_phone(body: AddPhoneSchema, contact_id: id, db: AsyncSession):
    stmt = select(Contact).where(Contact.id == contact_id)
    result = await db.execute(stmt)
    person = result.scalar_one_or_none()

    if not person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Contact with this ID not found")

    tag_exists = await db.scalar(
        select(exists()
               .where(Phone.tag == body.phone_tag)
               .where(Phone.contact_id == contact_id)
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
    await db.refresh(phone)

    return phone


async def update_phone(body: PhoneUpdateSchema, contact_id: id, tag: str, db: AsyncSession):
    stmt = select(Phone).where(Phone.contact_id == contact_id).filter(Phone.tag == tag)
    result = await db.execute(stmt)
    contact_phone = result.scalar_one_or_none()

    if not contact_phone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Phone with given tag not found for this contact")

    contact_phone.phone = str(body.phone_number)

    await db.commit()
    await db.refresh(contact_phone)

    return contact_phone


async def add_email(body: AddEmailSchema, contact_id: id, db: AsyncSession):
    stmt = select(Contact).where(Contact.id == contact_id)
    result = await db.execute(stmt)
    person = result.scalar_one_or_none()

    if not person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Contact with this ID not found")

    tag_exists = await db.scalar(
        select(exists()
               .where(Phone.tag == body.phone_tag)
               .where(Phone.contact_id == contact_id)
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
    await db.refresh(email)

    return email


async def update_email(body: EmailUpdateSchema, contact_id: id, tag: str, db: AsyncSession):
    stmt = select(Email).where(Email.contact_id == contact_id).filter(Email.tag == tag)
    result = await db.execute(stmt)
    contact_email = result.scalar_one_or_none()

    if not contact_email:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Email with given tag not found for this contact")

    contact_email.email = str(body.email)

    await db.commit()
    await db.refresh(contact_email)

    return contact_email


async def get_contacts_birthday(db: AsyncSession):
    today = datetime.now().date()
    days_range_check = today + timedelta(days=7)

    birthday_this_year = func.make_date(
        literal(today.year),
        cast(extract("month", Contact.birthday), Integer),
        cast(extract("day", Contact.birthday), Integer)
    )

    stmt = (select(Contact).where(cast(birthday_this_year, Date).
                                 between(today, days_range_check)).
            options(selectinload(Contact.email),
                    selectinload(Contact.phones)
                    )
            )

    birthdays = await db.execute(stmt)

    return birthdays.scalars().all()


async def delete_contact(person_id: id, db: AsyncSession):
    stmt = select(Contact).where(Contact.id == person_id)
    result = await db.execute(stmt)
    person = result.scalar_one_or_none()

    if person:
        await db.delete(person)
        await db.commit()

    return person
