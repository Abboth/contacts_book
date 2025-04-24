from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from contacts_book.src.auth.security import auth_security, AccessLevel, access
from contacts_book.src.core.connection import get_db
from contacts_book.src.contacts import repository as repositories
from contacts_book.src.contacts.schemas.request_schema import AddPhoneSchema, PhoneUpdateSchema
from contacts_book.src.contacts.schemas.response_schema import PhoneResponseSchema
from contacts_book.src.users.models import User

router = APIRouter(tags=["Phones"])


@router.post("/{contact_id}", response_model=PhoneResponseSchema, status_code=status.HTTP_201_CREATED,
             dependencies=Depends(access[AccessLevel.public]))
async def add_phone(body: AddPhoneSchema, contact_id: int = Path(ge=1),
                    db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(auth_security.get_current_user)):
    person_phone = await repositories.add_phone(body, contact_id, current_user, db)
    return person_phone


@router.put("/{contact_id}/tag/{tag}", response_model=PhoneResponseSchema,
             dependencies=Depends(access[AccessLevel.public]))
async def update_phone(body: PhoneUpdateSchema, contact_id: int = Path(ge=1),
                       tag: str = Path(min_length=4),
                       db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(auth_security.get_current_user)):

    contact = await repositories.update_phone(body, contact_id, tag, current_user, db)

    return contact
