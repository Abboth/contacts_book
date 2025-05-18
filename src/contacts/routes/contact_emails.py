from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.security import check_active_user, AccessLevel, access
from src.contacts.models import ContactsEmail
from src.core.connection import get_db
from src.contacts import repository as repositories
from src.contacts.schemas.request_schema import AddEmailSchema, EmailUpdateSchema
from src.contacts.schemas.response_schema import EmailResponseSchema
from src.users.models import User

router = APIRouter(tags=["Emails"])


@router.post("/{contact_id}", response_model=EmailResponseSchema,
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(access[AccessLevel.public])])
async def add_email(body: AddEmailSchema, contact_id: int = Path(ge=1),
                    db: AsyncSession = Depends(get_db),
                    current_user: User = Depends(check_active_user)) -> ContactsEmail:
    """
    Add a new email address to the specified contact.

    :param body: Email data to be added.
    :type body: AddEmailSchema
    :param contact_id: ID of the contact.
    :type contact_id: int
    :param db: Database session.
    :type db: AsyncSession
    :param current_user: Authenticated user.
    :type current_user: User
    :return: Added email information.
    :rtype: ContactsEmail
    """
    person_email = await repositories.add_email(body, contact_id, current_user, db)
    return person_email


@router.put("/{contact_id}/tag/{tag}", response_model=EmailResponseSchema,
            dependencies=[Depends(access[AccessLevel.public])])
async def update_email(body: EmailUpdateSchema, contact_id: int = Path(ge=1),
                       tag: str = Path(min_length=4),
                       db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(check_active_user)):
    """
    Update an existing email address by contact ID and tag.

    :param body: Updated email data.
    :type body: EmailUpdateSchema
    :param contact_id: ID of the contact.
    :type contact_id: int
    :param tag: Email tag to identify the address.
    :type tag: str
    :param db: Database session.
    :type db: AsyncSession
    :param current_user: Authenticated user.
    :type current_user: User
    :return: Updated email information.
    :rtype: ContactsEmail
    """
    person_email = await repositories.update_email(body, contact_id, tag, current_user, db)
    return person_email
