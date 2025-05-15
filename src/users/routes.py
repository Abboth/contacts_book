from fastapi import APIRouter, UploadFile, Depends, File
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.security import auth_security
from src.core.config import configuration
from src.core.connection import get_db
from src.services.cloudinary_service import cloudinary_services
from src.services.redis_service import redis_manager
from src.users.models import User
from src.users.schemas import UserResponseSchema
from src.users import repository as user_repository

router = APIRouter(tags=["Users"])

@router.patch("/change_avatar",
              response_model=UserResponseSchema,
              dependencies=[Depends(RateLimiter(times=2, minutes=1))])
async def change_avatar(avatar_img: UploadFile = File, user: User = Depends(auth_security.get_current_user),
                        db: AsyncSession = Depends(get_db)) -> User:
    """
    Upload a new avatar to Cloudinary and update user profile.

    :param avatar_img: Avatar image file.
    :type avatar_img: UploadFile
    :param user: Currently authenticated user.
    :type user: User
    :param db: Async SQLAlchemy session.
    :type db: AsyncSession
    :return: Updated user with new avatar URL.
    :rtype: User
    """
    folder = f"user_avatars/{user.email}"
    public_id = f"avatar_{user.email}"
    transformation = {"width": 250, "height": 250, "crop": "fill"}
    avatar_url =await cloudinary_services.upload_file(avatar_img.file, folder, public_id, transformation)

    updated_user = await user_repository.update_avatar(user.email, avatar_url, db)
    await redis_manager.set_obj(f"user:{user.email}", user, ex=300)
    return updated_user
