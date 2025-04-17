from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from bdaybot.src.models.models import Person, Email, Phone, Hobby
from bdaybot.src.schemas.bday_bot import AddContactSchema, ContactUpdateSchema


async def show_all_contacts(limit: int, offset: int, db: AsyncSession):
    stmt = select(Person).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()

async def get_contact_by_id(contact_id: int, db: AsyncSession):
    stmt = select(Person).filter_by(id=contact_id)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def add_contact(body: AddContactSchema, db: AsyncSession):
    print(body.model_dump(exclude_unset=True))
    try:
        contact = Person(
            first_name=body.first_name,
            last_name=body.last_name,
            birthday=body.birthday,
        )
        if body.email:
            contact.email.append(Email(email=body.email, tag=body.mail_tag))
        if body.phone_number:
            contact.phones.append(Phone(phone_number=body.phone_number, tag=body.phone_tag))
        if body.hobby:
            contact.hobby.append(Hobby(hobby_name=body.hobby))

        db.add(contact)
        await db.commit()
        await db.refresh(contact)
        return contact
    except Exception as e:
        print("ERROR IN add_contact:", e)
        raise


async def update_contact(contact_id: id, body: ContactUpdateSchema, db: AsyncSession):
    pass


async def delete_contact(person_id: id, db: AsyncSession):
    pass