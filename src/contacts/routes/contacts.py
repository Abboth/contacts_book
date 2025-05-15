from typing import List

from fastapi import APIRouter, Query, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.contacts.models import Contact
from src.core.connection import get_db
from src.contacts import repository as repositories
from src.contacts.schemas.request_schema import AddContactSchema, ContactUpdateSchema
from src.contacts.schemas.response_schema import ContactResponseSchema
from src.auth.security import auth_security, access, AccessLevel
from src.users.models import User

router = APIRouter(tags=["Contacts"])


@router.get("/", response_model=list[ContactResponseSchema],
             dependencies=[Depends(access[AccessLevel.public])])
async def show_all_persons(limit: int = Query(10, ge=10, le=50),
                           db: AsyncSession = Depends(get_db),
                           current_user: User = Depends(auth_security.get_current_user)) -> List[Contact]:
    """
    Retrieve all contacts belonging to the current user (limited).

    :param limit: Maximum number of contacts to return (between 10 and 50).
    :type limit: int
    :param db: Database session.
    :type db: AsyncSession
    :param current_user: Currently authenticated user.
    :type current_user: User
    :return: List of contacts.
    :rtype: list[Contact]
    """
    contacts = await repositories.show_all_contacts(limit, current_user, db)

    return contacts


@router.post("/create", response_model=ContactResponseSchema,
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(access[AccessLevel.public])])
async def add_person(body: AddContactSchema, db: AsyncSession = Depends(get_db),
                           current_user: User = Depends(auth_security.get_current_user)) -> Contact:
    """
    Add a new contact for the current user.

    :param body: Contact data to create.
    :type body: AddContactSchema
    :param db: Database session.
    :type db: AsyncSession
    :param current_user: Currently authenticated user.
    :type current_user: User
    :return: Created contact.
    :rtype: Contact
    """
    contact = await repositories.add_contact(body, current_user, db)

    return contact


@router.get("/birthdays", response_model=list[ContactResponseSchema],
             dependencies=[Depends(access[AccessLevel.public])])
async def get_contacts_upcoming_birthday(db: AsyncSession = Depends(get_db),
                           current_user: User = Depends(auth_security.get_current_user)) -> List[Contact]:
    """
    Get contacts with upcoming birthdays for the current user.

    :param db: Database session.
    :type db: AsyncSession
    :param current_user: Currently authenticated user.
    :type current_user: User
    :return: List of contacts with upcoming birthdays.
    :rtype: list[Contact]
    """
    contacts = await repositories.get_contacts_birthday(current_user, db)

    return contacts


@router.put("/{contact_id}", response_model=ContactResponseSchema,
             dependencies=[Depends(access[AccessLevel.public])])
async def update_person(body: ContactUpdateSchema, contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                           current_user: User = Depends(auth_security.get_current_user)) -> Contact:
    """
    Update an existing contact by ID.

    :param body: Updated contact data.
    :type body: ContactUpdateSchema
    :param contact_id: ID of the contact to update.
    :type contact_id: int
    :param db: Database session.
    :type db: AsyncSession
    :param current_user: Currently authenticated user.
    :type current_user: User
    :return: Updated contact.
    :rtype: Contact
    """
    contact = await repositories.update_contact(body, contact_id, current_user, db)

    return contact


@router.get("/{contact_id}", response_model=ContactResponseSchema,
             dependencies=[Depends(access[AccessLevel.public])])
async def get_person(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                           current_user: User = Depends(auth_security.get_current_user)) -> Contact:
    """
    Retrieve a specific contact by ID.

    :param contact_id: ID of the contact to retrieve.
    :type contact_id: int
    :param db: Database session.
    :type db: AsyncSession
    :param current_user: Currently authenticated user.
    :type current_user: User
    :return: Contact object.
    :rtype: Contact
    """
    contact = await repositories.get_contact_by_id(contact_id, current_user, db)

    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(access[AccessLevel.public])])
async def delete_person(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                        current_user: User = Depends(auth_security.get_current_user)) -> None:
    """
    Delete a specific contact by ID.

    :param contact_id: ID of the contact to delete.
    :type contact_id: int
    :param db: Database session.
    :type db: AsyncSession
    :param current_user: Currently authenticated user.
    :type current_user: User
    :return: None.
    :rtype: None
    """
    await repositories.delete_contact(contact_id, current_user, db)



@router.get("/name/{name}", response_model=list[ContactResponseSchema],
            dependencies=[Depends(access[AccessLevel.public])])
async def get_persons_by_name(name: str = Path(min_length=2), db: AsyncSession = Depends(get_db),
                              current_user: User = Depends(auth_security.get_current_user)) -> List[Contact]:
    """
    Retrieve contacts by name (case-insensitive match).

    :param name: Name or part of name to search.
    :type name: str
    :param db: Database session.
    :type db: AsyncSession
    :param current_user: Currently authenticated user.
    :type current_user: User
    :return: List of matching contacts.
    :rtype: list[Contact]
    """
    contact = await repositories.get_contact_by_name(name, current_user, db)

    return contact
