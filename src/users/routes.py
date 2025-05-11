import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, UploadFile, Depends, File
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.security import auth_security
from src.core.config import configuration
from src.core.connection import get_db
from src.services.redis_service import redis_manager
from src.users.models import User
from src.users.schemas import UserResponseSchema
from src.users import repository as user_repository

router = APIRouter(tags=["Users"])
cloudinary.config(
    cloud_name=configuration.CLOUDINARY_CLOUD,
    api_key=configuration.CLOUDINARY_API_KEY,
    api_secret=configuration.CLOUDINARY_SECRET_KEY,
    secure=True,
)


@router.patch("/change_avatar",
              response_model=UserResponseSchema,
              dependencies=[Depends(RateLimiter(times=2, minutes=1))])
async def change_avatar(file: UploadFile = File, user: User = Depends(auth_security.get_current_user),
                        db: AsyncSession = Depends(get_db)) -> User:
    """
    Upload a new avatar to Cloudinary and update user profile.

    :param file: Avatar image file.
    :type file: UploadFile
    :param user: Currently authenticated user.
    :type user: User
    :param db: Async SQLAlchemy session.
    :type db: AsyncSession
    :return: Updated user with new avatar URL.
    :rtype: User
    """

    public_id = f"user_avatars/{user.email}"
    cloud_storage = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
    cloud_storage_url = cloudinary.CloudinaryImage(public_id).build_url(width=250, heigth=250, crop="fill",
                                                                        version=cloud_storage.get("version"))

    updated_user = await user_repository.update_avatar(user.email, cloud_storage_url, db)
    await redis_manager.set_obj(f"user:{user.email}", user, ex=300)
    return updated_user
