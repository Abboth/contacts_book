from fastapi import APIRouter, HTTPException, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from bdaybot.src.bd_connect.database.connection import get_db
from bdaybot.src.repository import bday_bot as repositories
from bdaybot.src.schemas.request_schema import AddPhoneSchema, PhoneUpdateSchema
from bdaybot.src.schemas.response_schema import PhoneResponseSchema

router = APIRouter(tags=["Phones"])


@router.post("/{contact_id}", response_model=PhoneResponseSchema, status_code=status.HTTP_201_CREATED)
async def add_phone(body: AddPhoneSchema, contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db)):
    person_phone = await repositories.add_phone(body, contact_id, db)
    return person_phone


@router.put("/{contact_id}/tag/{tag}", response_model=PhoneResponseSchema)
async def update_phone(body: PhoneUpdateSchema, contact_id: int = Path(ge=1),
                       tag: str = Path(min_length=4),
                       db: AsyncSession = Depends(get_db)):
    contact = await repositories.update_phone(body, contact_id, tag, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Phone for this ID is not exist")

    return contact
