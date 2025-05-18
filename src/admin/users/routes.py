from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.admin.users import repository as admin_user_repository
from src.core.connection import get_db

router = APIRouter(tags=["Staff manage panel"])


@router.delete("/{user_id}/delete")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)) -> None:
    await admin_user_repository.delete_user(user_id, db)


@router.patch("/{user_id}/edite")
async def edite_user(user_id: int, db: AsyncSession = Depends(get_db)) -> None:
    await admin_user_repository.edite_user(user_id, db)


@router.patch("/{user_id}/ban")
async def ban_user(user_id: int, db: AsyncSession = Depends(get_db)) -> None:
    await admin_user_repository.ban_user(user_id, db)