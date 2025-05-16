from fastapi import APIRouter

from src.admin.users import repository as admin_user_repository

router = APIRouter(tags=["Staff manage panel"])


@router.delete("/{user_id}/delete")
async def delete_user(user_id: int) -> None:
    await admin_user_repository.delete_user(user_id)