from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.cloudinary_service import cloudinary_services
from src.users.models import User
from src.users.schemas import EditeUserSchema

async def get_user_by_id(user_id: int, db: AsyncSession) -> User:
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message.USER_NOT_FOUND)

    return user

async def delete_user(user_id: int, db: AsyncSession) -> None:
    user = await get_user_by_id(user_id, db)

    await db.delete(user)
    await db.commit()

    await cloudinary_services.delete_user_files(user.email)


async def edite_user(body: EditeUserSchema, user_id: int, db: AsyncSession, password=None) -> User:
    """
    update existing user data

    :param body: data to edite
    :type body: UserSchema
    :param user_id: if of user to edite
    :type user_id: User
    :param db: The database session.
    :type db: AsyncSession
    :param password: optional parameter to change new password
    :type password: str
    :return: updated user data
    :rtype: User
    """
    user = await get_user_by_id(user_id, db)

    if body.birthday:
        user.birthday = body.birthday

    if body.profile_slug:
        user.display_name = body.display_name

    if password:
        user.hashed_pwd = password

    await db.commit()
    await db.refresh(user)

    return user


async def ban_user(user_id: int, db: AsyncSession) -> None:
    user = await get_user_by_id(user_id, db)

    user.is_active = False

    await db.commit()
    await db.refresh(user)
