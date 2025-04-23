
from sqlalchemy.ext.asyncio import AsyncSession

from contacts_book.src.users.models import User


async def update_token(user: User, device_type, token: str, db: AsyncSession):
    user.auth_session.refresh_token = token
    user.auth_session.device_type = device_type
    await db.commit()


