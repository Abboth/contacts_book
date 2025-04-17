from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bdaybot.src.models.models import Person, Phone, Email, Hobby
from bdaybot.src.schemas.bday_bot import AddContactSchema, ContactUpdateSchema


async def show_all_contacts(db: AsyncSession) -> List[Person]:
    pass


async def get_contact_by_id(person_id: int, db: AsyncSession) -> Person:
    pass


async def add_contact(person: AddContactSchema, db: AsyncSession) -> Person:
    pass


async def update_contact(person_id: id, person: ContactUpdateSchema, db: AsyncSession):
    pass


async def delete_contact(person_id: id, db: AsyncSession):
    pass