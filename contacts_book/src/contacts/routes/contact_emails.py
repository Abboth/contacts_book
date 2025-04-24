from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from contacts_book.src.auth.security import auth_security, AccessLevel, access
from contacts_book.src.core.connection import get_db
from contacts_book.src.contacts import repository as repositories
from contacts_book.src.contacts.schemas.request_schema import AddEmailSchema, EmailUpdateSchema
from contacts_book.src.contacts.schemas.response_schema import EmailResponseSchema
from contacts_book.src.users.models import User

router = APIRouter(tags=["Emails"])


@router.post("/{contact_id}", response_model=EmailResponseSchema,
             status_code=status.HTTP_201_CREATED,
             dependencies=Depends(access[AccessLevel.public])
             )
async def add_email(body: AddEmailSchema, contact_id: int = Path(ge=1),
                    db: AsyncSession = Depends(get_db),
                    current_user: User = Depends(auth_security.get_current_user)):

    person_email = await repositories.add_email(body, contact_id, current_user, db)
    return person_email


@router.put("/{contact_id}/tag/{tag}", response_model=EmailResponseSchema,
             dependencies=Depends(access[AccessLevel.public]))
async def update_email(body: EmailUpdateSchema, contact_id: int = Path(ge=1),
                       tag: str = Path(min_length=4),
                       db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(auth_security.get_current_user)):

    person_email = await repositories.update_email(body, contact_id, tag, current_user, db)
    return person_email
