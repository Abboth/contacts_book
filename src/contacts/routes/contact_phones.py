from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.security import check_active_user, AccessLevel, access
from src.contacts.models import ContactsPhone
from src.core.connection import get_db
from src.contacts import repository as repositories
from src.contacts.schemas.request_schema import AddPhoneSchema, PhoneUpdateSchema
from src.contacts.schemas.response_schema import PhoneResponseSchema
from src.users.models import User

router = APIRouter(tags=["Phones"])


@router.post("/{contact_id}", response_model=PhoneResponseSchema, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(access[AccessLevel.public])])
async def add_phone(body: AddPhoneSchema, contact_id: int = Path(ge=1),
                    db: AsyncSession = Depends(get_db),
                    current_user: User = Depends(check_active_user)) -> ContactsPhone:
    """
    Add a new phone number to the specified contact.

    :param body: Phone data to be added.
    :type body: AddPhoneSchema
    :param contact_id: ID of the contact.
    :type contact_id: int
    :param db: Database session.
    :type db: AsyncSession
    :param current_user: Authenticated user.
    :type current_user: User
    :return: Added phone information.
    :rtype: ContactsPhone
    """
    person_phone = await repositories.add_phone(body, contact_id, current_user, db)
    return person_phone


@router.put("/{contact_id}/tag/{tag}", response_model=PhoneResponseSchema,
             dependencies=[Depends(access[AccessLevel.public])])
async def update_phone(body: PhoneUpdateSchema, contact_id: int = Path(ge=1),
                       tag: str = Path(min_length=4),
                       db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(check_active_user)) -> ContactsPhone:
    """
    Update an existing phone number by contact ID and tag.

    :param body: Updated phone data.
    :type body: PhoneUpdateSchema
    :param contact_id: ID of the contact.
    :type contact_id: int
    :param tag: Phone tag to identify the number.
    :type tag: str
    :param db: Database session.
    :type db: AsyncSession
    :param current_user: Authenticated user.
    :type current_user: User
    :return: Updated phone information.
    :rtype: ContactsPhone
    """

    contact = await repositories.update_phone(body, contact_id, tag, current_user, db)

    return contact
