from datetime import datetime, timedelta
from typing import List

from fastapi import HTTPException, status

from sqlalchemy import exists, extract, cast, Date, Integer
from sqlalchemy.sql import func, literal
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.contacts.models import ContactsEmail, ContactsPhone, Contact
from src.contacts.schemas.request_schema import AddContactSchema, ContactUpdateSchema, PhoneUpdateSchema, \
    EmailUpdateSchema, AddPhoneSchema, AddEmailSchema
from src.users.models import User


async def show_all_contacts(limit: int, user: User, db: AsyncSession) -> List[Contact]:
    """
    Retrieves list with limited count of contacts for a specific user.

    :param limit: limit of users to retrieve from database
    :type limit: int
    :param user: The user to retrieve list of contacts for.
    :type user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: list of contacts
    :rtype: list[Contact]
    """
    stmt = select(Contact).where(Contact.user_id == user.id).limit(limit).options(selectinload(Contact.email),
                                                                                  selectinload(Contact.phones))
    result = await db.execute(stmt)
    contacts = result.scalars().all()

    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="You dont have any contacts yet")

    return contacts


async def get_contact_by_id(contact_id: int, user: User, db: AsyncSession) -> Contact:
    """
    Retrieves list with limited count of contacts for a specific user.

    :param contact_id: contact to find
    :type contact_id: int
    :param user: The user to retrieve contact for.
    :type user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: list of contacts
    :rtype: Contact
    """
    stmt = select(Contact).where(Contact.id == contact_id,
                                 Contact.user_id == user.id).options(selectinload(Contact.email),
                                                                     selectinload(Contact.phones))
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()

    if contact is None:
        raise HTTPException(status_code=404, detail="Contact with this ID not found in your's contact book")

    return contact


async def get_contact_by_name(name: str, user: User, db: AsyncSession) -> List[Contact]:
    """
    Retrieves list of contacts with matches by name for a specific user.

    :param name: name of contact to find
    :type name: str
    :param user: The user to retrieve contact for.
    :type user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: list of contacts with name like looking for
    :rtype: list[Contact]
    """
    stmt = select(Contact).where(Contact.first_name.ilike("%" + name + "%"),
                                 Contact.user_id == user.id).options(selectinload(Contact.email),
                                                                     selectinload(Contact.phones))
    result = await db.execute(stmt)
    contacts = result.scalars().all()

    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not found any contacts with name like {name}")

    return contacts


async def add_contact(body: AddContactSchema, user: User, db: AsyncSession) -> Contact:
    """
    Create new contact for a specific user.

    :param body: data to create new contact.
    :type body: AddContactSchema
    :param user: The user to retrieve contact for.
    :type user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: new contact.
    :rtype: Contact
    """
    contact = Contact(
        first_name=body.first_name,
        last_name=body.last_name,
        birthday=body.birthday,
        description=body.description,
        user_id=user.id
    )

    if body.email:
        contact.email.append(ContactsEmail(email=body.email, tag=body.mail_tag))
    if body.phone_number:
        contact.phones.append(ContactsPhone(phone=body.phone_number, tag=body.phone_tag))

    db.add(contact)
    await db.commit()
    await db.refresh(contact)

    return contact


async def update_contact(body: ContactUpdateSchema, contact_id: int, user: User, db: AsyncSession) -> Contact:
    """
    Update existing contact for a specific user.

    :param body: data to update existing contact.
    :type body: ContactUpdateSchema
    :param contact_id: contact to find
    :type contact_id: int
    :param user: The user to retrieve contact for.
    :type user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: Updated contact.
    :rtype: Contact
    """
    contact = await get_contact_by_id(contact_id, user, db)

    contact.first_name = body.first_name
    contact.last_name = body.last_name
    contact.description = body.description
    if not contact.birthday:
        contact.birthday = body.birthday

    await db.commit()
    await db.refresh(contact)

    return contact


async def add_phone(body: AddPhoneSchema, contact_id: int, user: User, db: AsyncSession) -> ContactsPhone:
    """
    Add new phone number for existing contact with checking phone tag to not repeat.

    :param body: Data to create contact new phone
    :type body: AddPhoneSchema
    :param contact_id: ID of contact to add phone
    :type contact_id: int
    :param user: The user to add contact phone.
    :type user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: new phone for existing contact
    :rtype: ContactsPhone
    """
    await get_contact_by_id(contact_id, user, db)

    tag_exists = await db.scalar(
        select(exists()
               .where(ContactsPhone.tag == body.phone_tag,
                      ContactsPhone.contact_id == contact_id)
               )
    )

    if tag_exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="This tag already used for this contact")

    phone = ContactsPhone(phone=body.phone_number,
                          tag=body.phone_tag,
                          contact_id=contact_id)
    db.add(phone)
    await db.commit()
    await db.refresh(phone)

    return phone


async def update_phone(body: PhoneUpdateSchema, contact_id: int, tag: str, user: User,
                       db: AsyncSession) -> ContactsPhone:
    """
    Update phone by tag for existing contact.

    :param body: Data to update contacts phone
    :type body: PhoneUpdateSchema
    :param contact_id: ID of contact to update phone
    :type contact_id: int
    :param tag: tag of phone
    :type tag: str
    :param user: The user to update contacts phone.
    :type user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: updated phone for existing contact
    :rtype: ContactsPhone
    """
    await get_contact_by_id(contact_id, user, db)

    stmt = select(ContactsPhone).where(ContactsPhone.contact_id == contact_id).filter(ContactsPhone.tag == tag)
    result = await db.execute(stmt)
    contact_phone = result.scalar_one_or_none()

    if not contact_phone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Phone with given tag not found for this contact")

    contact_phone.phone = str(body.phone_number)

    await db.commit()
    await db.refresh(contact_phone)

    return contact_phone


async def add_email(body: AddEmailSchema, contact_id: int, user: User, db: AsyncSession) -> ContactsEmail:
    """
    Add new email for existing contact with checking email tag to not repeat.

    :param body: Data to create contact email.
    :type body: AddEmailSchema
    :param contact_id: ID of contact to add new email
    :type contact_id: int
    :param user: The user to add contact email.
    :type user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: new email for existing contact
    :rtype: ContactsEmail
    """
    users_contact_exist = await get_contact_by_id(contact_id, user, db)

    tag_exists = await db.scalar(
        select(exists()
               .where(ContactsEmail.tag == body.mail_tag)
               .where(ContactsEmail.contact_id == contact_id)
               )
    )

    if tag_exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="This tag already used for this contact")

    email = ContactsEmail(email=body.email,
                          tag=body.mail_tag,
                          contact_id=contact_id)
    db.add(email)
    await db.commit()
    await db.refresh(email)

    return email


async def update_email(body: EmailUpdateSchema, contact_id: int, tag: str, user: User,
                       db: AsyncSession) -> ContactsEmail:
    """
    Update email by tag for existing contact.

    :param body: Data to update contacts email
    :type body: EmailUpdateSchema
    :param contact_id: ID of contact to update email
    :type contact_id: int
    :param tag: tag of email
    :type tag: str
    :param user: The user to update contacts email.
    :type user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: updated email for existing contact
    :rtype: ContactsEmail
    """
    await get_contact_by_id(contact_id, user, db)

    stmt = select(ContactsEmail).where(ContactsEmail.contact_id == contact_id).filter(ContactsEmail.tag == tag)
    result = await db.execute(stmt)
    contact_email = result.scalar_one_or_none()

    if not contact_email:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Email with given tag not found for this contact")

    contact_email.email = str(body.email)

    await db.commit()
    await db.refresh(contact_email)

    return contact_email


async def get_contacts_birthday(user: User, db: AsyncSession) -> List[Contact]:
    """
    Gather contacts who has birthday in nearest 7 days

    :param user: Current session user
    :type user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: List of contact
    :rtype: list[Contact]
    """
    today = datetime.now().date()
    days_range_check = today + timedelta(days=7)

    birthday_this_year = func.make_date(
        literal(today.year),
        cast(extract("month", Contact.birthday), Integer),
        cast(extract("day", Contact.birthday), Integer)
    )

    stmt = (select(Contact).where(cast(birthday_this_year, Date).
                                  between(today, days_range_check), Contact.user_id == user.id).
            options(selectinload(Contact.email),
                    selectinload(Contact.phones)))

    birthdays = await db.execute(stmt)

    return birthdays.scalars().all()


async def delete_contact(contact_id: int, user: User, db: AsyncSession) -> Contact:
    """
    Delete one contact of user

    :param contact_id: ID of contact to delete
    :type contact_id: int
    :param user: Current session user
    :type user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: Deleted contact
    :rtype: Contact
    """

    contact = await get_contact_by_id(contact_id, user, db)

    if contact:
        await db.delete(contact)
        await db.commit()

    return contact
