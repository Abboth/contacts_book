import logging

from fastapi import Depends
from libgravatar import Gravatar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from contacts_book.src.core.connection import get_db
from contacts_book.src.users.models import User
from contacts_book.src.users.schemas import UserSchema

logging.basicConfig(level=logging.INFO)

async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    stmt = select(User).filter(User.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    return user


async def create_new_user(body: UserSchema, db: AsyncSession = Depends(get_db)):
    avatar = None
    try:
        gravatar = Gravatar(body.email)
        avatar = gravatar.get_image()
    except Exception as err:
        logging.info(err)

    new_user = User(username=body.username,
                    email=body.email,
                    hashed_pwd=body.password,
                    avatar=avatar)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user