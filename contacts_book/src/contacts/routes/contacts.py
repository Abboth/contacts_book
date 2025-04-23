from fastapi import APIRouter, Query, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from contacts_book.src.core.connection import get_db
from contacts_book.src.contacts import repository as repositories
from contacts_book.src.contacts.schemas.request_schema import AddContactSchema, ContactUpdateSchema
from contacts_book.src.contacts.schemas.response_schema import ContactResponseSchema
from contacts_book.src.auth.security import auth_security
from contacts_book.src.users.models import User

router = APIRouter(tags=["Contacts"])


@router.get("/", response_model=list[ContactResponseSchema])
async def show_all_persons(limit: int = Query(10, ge=10, le=50),
                           db: AsyncSession = Depends(get_db),
                           current_user: User = Depends(auth_security.get_current_user)):
    contacts = await repositories.show_all_contacts(limit, current_user, db)

    return contacts


@router.post("/create", response_model=ContactResponseSchema, status_code=status.HTTP_201_CREATED)
async def add_person(body: AddContactSchema, db: AsyncSession = Depends(get_db),
                           current_user: User = Depends(auth_security.get_current_user)):
    contact = await repositories.add_contact(body, current_user, db)

    return contact


@router.get("/birthdays", response_model=list[ContactResponseSchema])
async def get_contacts_upcoming_birthday(db: AsyncSession = Depends(get_db),
                           current_user: User = Depends(auth_security.get_current_user)):
    contacts = await repositories.get_contacts_birthday(current_user, db)

    return contacts


@router.put("/{contact_id}", response_model=ContactResponseSchema)
async def update_person(body: ContactUpdateSchema, contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                           current_user: User = Depends(auth_security.get_current_user)):
    contact = await repositories.update_contact(body, contact_id, current_user, db)

    return contact


@router.get("/{contact_id}", response_model=ContactResponseSchema)
async def get_person(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                           current_user: User = Depends(auth_security.get_current_user)):
    contact = await repositories.get_contact_by_id(contact_id, current_user, db)

    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_person(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                           current_user: User = Depends(auth_security.get_current_user)):
    contact = await repositories.delete_contact(contact_id, current_user, db)

    return contact


@router.get("/name/{name}", response_model=list[ContactResponseSchema])
async def get_persons_by_name(name: str = Path(min_length=2), db: AsyncSession = Depends(get_db),
                           current_user: User = Depends(auth_security.get_current_user)):
    contact = await repositories.get_contact_by_name(name, current_user, db)

    return contact
