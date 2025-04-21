from fastapi import APIRouter, HTTPException, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from contacts_book.src.bd_connect.database.connection import get_db
from contacts_book.src.repository import book as repositories
from contacts_book.src.schemas.request_schema import AddPhoneSchema, PhoneUpdateSchema
from contacts_book.src.schemas.response_schema import PhoneResponseSchema

router = APIRouter(tags=["Phones"])


@router.post("/{contact_id}", response_model=PhoneResponseSchema, status_code=status.HTTP_201_CREATED)
async def add_phone(body: AddPhoneSchema, contact_id: int = Path(ge=1),
                    db: AsyncSession = Depends(get_db)):
    person_phone = await repositories.add_phone(body, contact_id, db)
    return person_phone


@router.put("/{contact_id}/tag/{tag}", response_model=PhoneResponseSchema)
async def update_phone(body: PhoneUpdateSchema, contact_id: int = Path(ge=1),
                       tag: str = Path(min_length=4),
                       db: AsyncSession = Depends(get_db)):

    contact = await repositories.update_phone(body, contact_id, tag, db)

    return contact
