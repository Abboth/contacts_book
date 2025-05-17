from fastapi import APIRouter, UploadFile, Depends, File, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.security import auth_security
from src.core.config import configuration
from src.core.connection import get_db
from src.posts.models import Post
from src.posts.repositories import post_repository
from src.posts.shcemas import PostResponseSchema
from src.services.cloudinary_service import cloudinary_services
from src.services.redis_service import redis_manager
from src.users.models import User
from src.users.schemas import UserResponseSchema, SubsListResponseSchema, UserProfileResponseSchema
from src.users import repository as user_repository

router = APIRouter(tags=["Users"])


@router.get("/{username}", response_model=UserProfileResponseSchema)
async def get_user(username: str, db: AsyncSession = Depends(get_db)):
    """
    Retrieve user data by username

    :param username: users username
    :type username: str
    :param db: The database session.
    :type db: AsyncSession
    :return: user or raise exception
    :rtype: User | None
    """

    return await user_repository.get_user_data(username, db)


@router.get("/feed", response_model=list[PostResponseSchema])
async def get_feed(user: User = Depends(auth_security.get_current_user),
                   db: AsyncSession = Depends(get_db)) -> list[Post]:
    """
    Get all posts of subscribed users

    :param user: Currently authenticated user.
    :type user: User
    :param db: Database session.
    :type db: AsyncSession
    """

    return await post_repository.get_feed_posts(user, db)


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
    folder = f"{user.email}/user_avatar"
    public_id = f"avatar_{user.email}"
    transformation = {"width": 250, "height": 250, "crop": "fill"}
    avatar_url = await cloudinary_services.upload_file(avatar_img.file, folder, public_id, transformation)

    updated_user = await user_repository.update_avatar(user.email, avatar_url, db)
    await redis_manager.set_obj(f"user:{user.email}", user, ex=300)
    return updated_user


@router.post("/{user_id}/subscribe", status_code=status.HTTP_201_CREATED)
async def subscribe_user(email: str, user: User = Depends(auth_security.get_current_user),
                         db: AsyncSession = Depends(get_db)):
    await user_repository.subscribe_user(email, user, db)


@router.delete("/{user_id}/unsubscribe", status_code=status.HTTP_204_NO_CONTENT)
async def unsubscribe_user(email: str, user: User = Depends(auth_security.get_current_user),
                           db: AsyncSession = Depends(get_db)) -> None:
    await user_repository.unsubscribe_user(email, user, db)


@router.delete("/{user_id}/delete_subscriber", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subscriber(email: str, user: User = Depends(auth_security.get_current_user),
                            db: AsyncSession = Depends(get_db)) -> None:
    await user_repository.delete_subscriber(email, user, db)


@router.get("/{user_id}/subscribers", response_model=list[SubsListResponseSchema])
async def get_subscribers(user: User = Depends(auth_security.get_current_user),
                          db: AsyncSession = Depends(get_db)) -> list[User]:
    return await user_repository.get_all_subscribers(user, db)


@router.get("/{user_id}/subscriptions", response_model=list[SubsListResponseSchema])
async def get_subscriptions(user: User = Depends(auth_security.get_current_user),
                            db: AsyncSession = Depends(get_db)) -> list[User]:
    return await user_repository.get_all_subscriptions(user, db)
