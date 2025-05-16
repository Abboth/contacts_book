from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.cloudinary_service import cloudinary_services
from src.users.models import User


async def delete_user(user_id: int, db: AsyncSession) -> None:
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    await db.delete(user)
    await db.commit()

    await cloudinary_services.delete_user_files(user.email)
