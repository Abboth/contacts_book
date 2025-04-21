from fastapi import APIRouter, HTTPException, Query, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from contacts_book.src.bd_connect.database.connection import get_db
from contacts_book.src.repository import book as repositories
from contacts_book.src.schemas.request_schema import AddContactSchema, ContactUpdateSchema
from contacts_book.src.schemas.response_schema import ContactResponseSchema

router = APIRouter(tags=["Contacts"])


@router.get("/", response_model=list[ContactResponseSchema])
async def show_all_persons(limit: int = Query(10, ge=10, le=50),
                           db: AsyncSession = Depends(get_db)):
    contacts = await repositories.show_all_contacts(limit, db)

    return contacts


@router.post("/create", response_model=ContactResponseSchema, status_code=status.HTTP_201_CREATED)
async def add_person(body: AddContactSchema, db: AsyncSession = Depends(get_db)):
    person = await repositories.add_contact(body, db)
    return person


@router.get("/birthdays", response_model=list[ContactResponseSchema])
async def get_contacts_upcoming_birthday(db: AsyncSession = Depends(get_db)):
    contacts = await repositories.get_contacts_birthday(db)

    return contacts


@router.get("/{name}", response_model=list[ContactResponseSchema])
async def get_persons_by_name(name: str = Path(min_length=2), db: AsyncSession = Depends(get_db)):
    contact = await repositories.get_contact_by_name(name, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact this ID is not exist")

    return contact


@router.put("/{contact_id}", response_model=ContactResponseSchema)
async def update_person(body: ContactUpdateSchema, contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db)):
    contact = await repositories.update_contact(body, contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email this ID is not exist")

    return contact


@router.get("/{contact_id}", response_model=ContactResponseSchema)
async def get_person(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db)):
    contact = await repositories.get_contact_by_id(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact this ID is not exist")

    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_person(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db)):
    contact = await repositories.delete_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email this ID is not exist")

    return None
