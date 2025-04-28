from datetime import date

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from theregram_proj.src.auth.models import AuthSession
from theregram_proj.src.users.models import User


async def update_token(user: User, device_type, token: str, expires_at: date, db: AsyncSession):
    result = await db.execute(
        select(AuthSession).where(AuthSession.user_id == user.id, AuthSession.device_type == device_type)
    )
    session = result.scalar_one_or_none()


    if session is None:
        session = AuthSession(
            refresh_token=token,
            device_type=device_type,
            user_id=user.id,
            expires_at=expires_at
        )
        db.add(session)
    else:
        session.refresh_token = token
        session.expires_at = expires_at

    await db.commit()

