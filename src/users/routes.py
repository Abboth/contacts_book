from fastapi import APIRouter, UploadFile, Depends, File, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.security import auth_security, check_active_user
from src.core.config import configuration
from src.core.connection import get_db
from src.posts.models import Post
from src.posts.repositories import post_repository
from src.posts.shcemas import PostResponseSchema
from src.services.cloudinary_service import cloudinary_services
from src.services.redis_service import redis_manager
from src.users.models import User
from src.users.schemas import UserResponseSchema, SubsListResponseSchema, UserProfileResponseSchema, EditeUserSchema
from src.users import repository as user_repository

router = APIRouter(tags=["Users"])


@router.get("/{profile_slug}", response_model=UserProfileResponseSchema)
async def get_user(profile_slug: str, db: AsyncSession = Depends(get_db)):
    """
    Retrieve user data by username

    :param profile_slug: users profile_slug
    :type profile_slug: str
    :param db: The database session.
    :type db: AsyncSession
    :return: user or raise exception
    :rtype: User | None
    """

    return await user_repository.get_user_data(profile_slug, db)


@router.get("/feed", response_model=list[PostResponseSchema])
async def get_feed(user: User = Depends(check_active_user),
                   db: AsyncSession = Depends(get_db)) -> list[Post]:
    """
    Get all posts of subscribed users

    :param user: Currently authenticated user.
    :type user: User
    :param db: Database session.
    :type db: AsyncSession
    """

    return await post_repository.get_feed_posts(user, db)


@router.patch("/me/edite", response_model=UserResponseSchema)
async def edite_user(body: EditeUserSchema, user: User = Depends(check_active_user),
                     db: AsyncSession = Depends(get_db)):
    """
    Edite user data

    :param body: user data
    :type body: EditeUserSchema
    :param user: Currently authenticated user.
    :type user: User
    :param db: Database session.
    :type db: AsyncSession
    :return: user data
    :rtype: UserResponseSchema
    """
    if body.new_password \
            and body.new_password == body.repeat_new_password \
            and auth_security.verify_password(body.old_password, user.hashed_pwd):

        password = auth_security.get_password_hash(body.old_password)

        return await user_repository.edite_user(body, user, db, password=password)

    return await user_repository.edite_user(body, user, db)


@router.patch("/me/change_avatar",
              response_model=UserResponseSchema,
              dependencies=[Depends(RateLimiter(times=2, minutes=1))])
async def change_avatar(avatar_img: UploadFile = File, user: User = Depends(check_active_user),
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
    return updated_user


@router.post("/{profile_slug}/subscribe", status_code=status.HTTP_201_CREATED)
async def subscribe_user(profile_slug: str, user: User = Depends(check_active_user),
                         db: AsyncSession = Depends(get_db)):
    await user_repository.subscribe_user(profile_slug, user, db)


@router.delete("/{profile_slug}/unsubscribe", status_code=status.HTTP_204_NO_CONTENT)
async def unsubscribe_user(profile_slug: str, user: User = Depends(check_active_user),
                           db: AsyncSession = Depends(get_db)) -> None:
    await user_repository.unsubscribe_user(profile_slug, user, db)


@router.delete("/{profile_slug}/delete_subscriber", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subscriber(profile_slug: str, user: User = Depends(check_active_user),
                            db: AsyncSession = Depends(get_db)) -> None:
    await user_repository.delete_subscriber(profile_slug, user, db)


@router.get("/{profile_slug}/subscribers", response_model=list[SubsListResponseSchema])
async def get_subscribers(profile_slug: str, user: User = Depends(check_active_user),
                          db: AsyncSession = Depends(get_db)) -> list[User]:
    return await user_repository.get_all_subscribers(profile_slug, db)


@router.get("/{profile_slug}/subscriptions", response_model=list[SubsListResponseSchema])
async def get_subscriptions(profile_slug: str, user: User = Depends(check_active_user),
                            db: AsyncSession = Depends(get_db)) -> list[User]:
    return await user_repository.get_all_subscriptions(profile_slug, db)
