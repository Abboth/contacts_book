from datetime import datetime, timedelta

from fastapi import HTTPException, status

from sqlalchemy import exists, extract, cast, Date, Integer
from sqlalchemy.sql import func, literal
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from contacts_book.src.models.models import Person, Email, Phone
from contacts_book.src.schemas.request_schema import AddContactSchema, ContactUpdateSchema, PhoneUpdateSchema, \
    EmailUpdateSchema, AddPhoneSchema, AddEmailSchema


async def show_all_contacts(limit: int, db: AsyncSession):
    stmt = select(Person).limit(limit).options(
        selectinload(Person.email),
        selectinload(Person.phones)
    )
    contacts = await db.execute(stmt)

    return contacts.scalars().all()


async def get_contact_by_id(contact_id: int, db: AsyncSession):
    stmt = select(Person).where(Person.id == contact_id).options(
        selectinload(Person.email),
        selectinload(Person.phones)
    )
    contact = await db.execute(stmt)

    return contact.scalar_one_or_none()


async def get_contact_by_name(name: str, db: AsyncSession):
    stmt = select(Person).where(Person.first_name.ilike("%" + name + "%")).options(
        selectinload(Person.email),
        selectinload(Person.phones)
    )
    contact = await db.execute(stmt)

    return contact.scalars().all()


async def add_contact(body: AddContactSchema, db: AsyncSession):
    contact = Person(
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

    stmt = (select(Person).where(Person.id == contact.id).options(
        selectinload(Person.email),
        selectinload(Person.phones)
    ))
    result = await db.execute(stmt)

    return result.scalar_one()


async def update_contact(body: ContactUpdateSchema, contact_id: id, db: AsyncSession):
    stmt = select(Person).where(Person.id == contact_id)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()

    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.description = body.description
        if not contact.birthday:
            contact.birthday = body.birthday

        await db.commit()
        await db.refresh(contact)
        updated_contact = await db.execute(
            stmt.options(selectinload(Person.email), selectinload(Person.phones)
                         )
        )
        return updated_contact.scalar_one_or_none()


async def add_phone(body: AddPhoneSchema, contact_id: id, db: AsyncSession):
    stmt = select(Person).where(Person.id == contact_id)
    result = await db.execute(stmt)
    person = result.scalar_one_or_none()

    if not person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Contact not found")

    tag_exists = await db.scalar(
        select(exists()
               .where(Phone.tag == body.phone_tag)
               .where(Phone.person_id == contact_id)
               )
    )

    if tag_exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="This tag already used for this contact")

    phone = Phone(phone=body.phone_number,
                  tag=body.phone_tag,
                  person_id=contact_id)
    db.add(phone)
    await db.commit()
    await db.refresh(phone)

    return phone


async def update_phone(body: PhoneUpdateSchema, contact_id: id, tag: str, db: AsyncSession):
    stmt = select(Phone).where(Phone.person_id == contact_id).filter(Phone.tag == tag)
    result = await db.execute(stmt)
    contact_phone = result.scalar_one_or_none()

    if not contact_phone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email with given tag not found")

    contact_phone.phone = str(body.phone_number)

    await db.commit()
    await db.refresh(contact_phone)

    return contact_phone


async def add_email(body: AddEmailSchema, contact_id: id, db: AsyncSession):
    stmt = select(Person).where(Person.id == contact_id)
    result = await db.execute(stmt)
    person = result.scalar_one_or_none()

    if not person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")

    tag_exists = await db.scalar(
        select(exists()
               .where(Phone.tag == body.phone_tag)
               .where(Phone.person_id == contact_id)
               )
    )

    if tag_exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This tag already used for this contact")

    email = Email(email=body.email,
                  tag=body.mail_tag,
                  person_id=contact_id)
    db.add(email)
    await db.commit()
    await db.refresh(email)

    return email


async def update_email(body: EmailUpdateSchema, contact_id: id, tag: str, db: AsyncSession):
    stmt = select(Email).where(Email.person_id == contact_id).filter(Email.tag == tag)
    result = await db.execute(stmt)
    contact_email = result.scalar_one_or_none()

    if not contact_email:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email with given tag not found")

    contact_email.email = str(body.email)

    await db.commit()
    await db.refresh(contact_email)

    return contact_email


async def get_contacts_birthday(db: AsyncSession):
    today = datetime.now().date()
    days_range_check = today + timedelta(days=7)

    birthday_this_year = func.make_date(
        literal(today.year),
        cast(extract("month", Person.birthday), Integer),
        cast(extract("day", Person.birthday), Integer)
    )

    stmt = (select(Person).where(cast(birthday_this_year, Date).
                                 between(today, days_range_check)).
            options(selectinload(Person.email),
                    selectinload(Person.phones)
                    )
            )

    birthdays = await db.execute(stmt)

    return birthdays.scalars().all()


async def delete_contact(person_id: id, db: AsyncSession):
    stmt = select(Person).where(Person.id == person_id)
    result = await db.execute(stmt)
    person = result.scalar_one_or_none()

    if person:
        await db.delete(person)
        await db.commit()

    return person
