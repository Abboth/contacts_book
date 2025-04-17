from fastapi import APIRouter, HTTPException, Query, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from bdaybot.src.bd_connect.database.connection import get_db
from bdaybot.src.repository import bday_bot as repositories
from bdaybot.src.schemas.bday_bot import AddContactSchema, ContactUpdateSchema, ContactResponseSchema

router = APIRouter(prefix="/bot", tags=["bot"])


@router.get("/", response_model=list[ContactResponseSchema])
async def show_all_persons(limit: int = Query(10, ge=10, le=50),
                           offset: int = Query(0, ge=0),
                           db: AsyncSession = Depends(get_db)):
    contacts = await repositories.show_all_contacts(limit, offset, db)

    return contacts


@router.get("/{contact_id}", response_model=ContactResponseSchema)
async def get_person(contact_id, db: AsyncSession = Depends(get_db)):
    contact = await repositories.get_contact_by_id(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact this ID is not exist")

    return contact


@router.post("/", response_model=ContactResponseSchema, status_code=status.HTTP_201_CREATED)
async def add_person(body: AddContactSchema, db: AsyncSession = Depends(get_db)):
    person = await repositories.add_contact(body, db)

    await db.refresh(person, ["email", "phones", "hobby"])

    email = person.email[0].email if person.email else None
    phone = person.phones[0].phone_number if person.phones else None
    hobby = person.hobby[0].hobby_name if person.hobby else None

    return ContactResponseSchema(
        id=person.id,
        first_name=person.first_name,
        last_name=person.last_name,
        birthday=person.birthday,
        email=email,
        phone_number=phone,
        hobby=hobby,
    )

@router.put("/{contact_id}")
async def update_person():
    pass


@router.delete("/{contact_id}")
async def delete_person():
    pass
