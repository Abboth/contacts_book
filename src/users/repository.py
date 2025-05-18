import logging
from fastapi import HTTPException, status

from libgravatar import Gravatar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload

from src.core import message
from src.users.models import User, Follower
from src.users.schemas import UserSchema, UserProfileResponseSchema, EditeUserSchema

logging.basicConfig(level=logging.INFO)


async def get_user_by_email_or_none(email: str, db: AsyncSession) -> User | None:
    """
    Retrieve user by mail

    :param email: users email
    :type email: str
    :param db: The database session.
    :type db: AsyncSession
    :return: user or none
    :rtype: User | None
    """
    stmt = select(User).where(User.email == email).options(selectinload(User.role))
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_email(email: str, db: AsyncSession) -> User:
    """
    Retrieve user by mail

    :param email: users email
    :type email: str
    :param db: The database session.
    :type db: AsyncSession
    :return: user or raise exception
    :rtype: User | None
    """
    user = await get_user_by_email_or_none(email, db)
    if not user:
        raise HTTPException(status_code=404, detail=message.USER_NOT_FOUNDED_BY_EMAIL)
    return user


def get_user_by_email_sync(email: str, db: Session) -> User | None:
    """
    sync func for celery worker to retrieve user by mail

    :param email: users email
    :type email: str
    :param db: The database session.
    :type db: Session
    :return: finded user by email or none
    :rtype: User | None
    """
    stmt = select(User).where(User.email == email)
    result = db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=message.USER_NOT_FOUNDED_BY_EMAIL)
    return user


async def get_user_by_profile_slug(profile_slug: str, db: AsyncSession) -> User:
    """
    Retrieve user by username

    :param profile_slug: users profile_slug
    :type profile_slug: str
    :param db: The database session.
    :type db: AsyncSession
    :return: user or raise exception
    :rtype: User | None
    """
    stmt = select(User).where(User.profile_slug == profile_slug).options(selectinload(User.following),
                                                                 selectinload(User.followers),
                                                                 selectinload(User.posts))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail=message.USER_NOT_FOUNDED_BY_USERNAME)

    return user


async def get_user_data(profile_slug: str, db: AsyncSession) -> UserProfileResponseSchema:
    """
    Retrieve user data by username

    :param profile_slug: users profile_slug
    :type profile_slug: str
    :param db: The database session.
    :type db: AsyncSession
    :return: user or raise exception
    :rtype: User | None
    """

    user = await get_user_by_profile_slug(profile_slug, db)

    return UserProfileResponseSchema(count_posts=len(user.posts),
                                     count_followers=len(user.followers),
                                     count_following=len(user.following),
                                     display_name=user.display_name,
                                     posts=user.posts,
                                     created_at=user.created_at
                                     )


async def create_new_user(body: UserSchema, db: AsyncSession) -> User:
    """
    Create new user with avatar getter from gravatar if avalable

    :param body: data to create new user
    :type body: UserSchema
    :param db: The database session.
    :type db: AsyncSession
    :return: created new user
    :rtype: User
    """
    avatar = None
    try:
        gravatar = Gravatar(body.email)
        avatar = gravatar.get_image()
    except Exception as err:
        logging.info(err)

    new_user = User(profile_slug=body.profile_slug,
                    display_name=body.display_name,
                    email=body.email,
                    hashed_pwd=body.password,
                    avatar=avatar)
    if not db.scalar(select(User).limit(1)):
        new_user.role_id = 1

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


async def confirmed_email(email: str, db: AsyncSession) -> None:
    """
    Confirm verification for user by email

    :param email: users email to confirm verification
    :type email: str
    :param db: The database session.
    :type db: AsyncSession
    """
    user = await get_user_by_email(email, db)
    user.is_verified = True
    await db.commit()


async def change_password(email: str, new_hashed_pwd: str, db: AsyncSession) -> None:
    """
    Change current password of user for new one

    :param email: users email
    :type email: str
    :param new_hashed_pwd: new hashed users password to change
    :type new_hashed_pwd: str
    :param db: The database session.
    :type db: AsyncSession
    :return: refreshed user data
    """
    user = await get_user_by_email(email, db)
    user.hashed_pwd = new_hashed_pwd

    await db.commit()
    await db.refresh(user)


async def update_avatar(email: str, avatar_url: str | None, db: AsyncSession) -> User:
    """

    :param email: users mail
    :type email: str
    :param avatar_url: url for new avatar at cloudinary
    :type avatar_url: str
    :param db:
    :type db: AsyncSession
    :return: updated user data
    :rtype: User
    """
    user = await get_user_by_email(email, db)
    user.avatar = avatar_url

    await db.commit()
    await db.refresh(user)

    return user


async def edite_user(body: EditeUserSchema, user: User, db: AsyncSession, password=None) -> User:
    """
    update existing user data

    :param body: data to edite
    :type body: UserSchema
    :param user: user to edite
    :type user: User
    :param db: The database session.
    :type db: AsyncSession
    :param password: optional parameter to change new password
    :type password: str
    :return: updated user data
    :rtype: User
    """
    if body.birthday and user.birthday:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message.YOU_ALREADY_HAVE_BIRTHDAY)

    if body.birthday:
        user.birthday = body.birthday

    if body.profile_slug:
        user.display_name = body.display_name

    if password:
        user.hashed_pwd = password

    await db.commit()
    await db.refresh(user)

    return user


async def subscribe_user(profile_slug: str, user: User, db: AsyncSession) -> None:
    """
    Subscribe user to newsletter

    :param user: current user
    :type user: User
    :param profile_slug: users profile_slug
    :type profile_slug: str
    :param db: The database session.
    :type db: AsyncSession
    """
    user_to_follow = await get_user_by_profile_slug(profile_slug, db)
    if user.id == user_to_follow.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=message.YOU_CANT_FOLLOW_YOURSELF)
    stmt = select(Follower).where(
        Follower.follower_id == user.id,
        Follower.followed_id == user_to_follow.id,
    )
    result = await db.execute(stmt)
    subscribed = result.scalar_one_or_none()

    if subscribed:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message.YOU_ALREADY_FOLLOW_THIS_USER)

    new_follow = Follower(follower_id=user.id, followed_id=user_to_follow.id)

    db.add(new_follow)
    await db.commit()


async def unsubscribe_user(profile_slug: str, user: User, db: AsyncSession) -> None:
    """
    Unsubscribe user to newsletter

    :param user: current user
    :type user: User
    :param profile_slug: users profile_slug to unfollow
    :type profile_slug: str
    :param db: The database session.
    :type db: AsyncSession
    """
    user_to_unfollow = await get_user_by_profile_slug(profile_slug, db)
    stmt = select(Follower).where(Follower.follower_id == user.id,
                                  Follower.followed_id == user_to_unfollow.id)
    result = await db.execute(stmt)
    follower = result.scalar_one_or_none()
    if not follower:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=message.THIS_USER_NOT_FOLLOWED)

    await db.delete(follower)
    await db.commit()


async def delete_subscriber(profile_slug: str, user: User, db: AsyncSession) -> None:
    """
    Delete user subscription

    :param user: current user
    :type user: User
    :param profile_slug: users email to delete from subscribers
    :type profile_slug: str
    :param db: The database session.
    :type db: AsyncSession
    """
    subscriber = await get_user_by_profile_slug(profile_slug, db)
    stmt = select(Follower).where(Follower.follower_id == subscriber.id,
                                  Follower.followed_id == user.id)
    result = await db.execute(stmt)
    follower = result.scalar_one_or_none()
    if not follower:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=message.THIS_USER_NOT_FOLLOWED_YOU)

    await db.delete(follower)
    await db.commit()


async def get_all_subscribers(profile_slug: str, db: AsyncSession) -> list[User]:
    """
    Get all subscribers of current user

    :param profile_slug: users profile_slug
    :type profile_slug: str
    :param db: The database session.
    :type db: AsyncSession
    :return: list of subscribers
    :rtype: list[User]
    """
    user = await get_user_by_profile_slug(profile_slug, db)
    stmt = select(Follower).where(Follower.follower_id == user.id)
    result = await db.execute(stmt)
    followers = result.scalars().all()
    return followers


async def get_all_subscriptions(profile_slug: str, db: AsyncSession) -> list[User]:
    """
    Get all subscriptions of current user

    :param user: current user
    :type user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: list of subscriptions
    :rtype: list[User]
    """
    user = await get_user_by_profile_slug(profile_slug, db)
    stmt = select(Follower).where(Follower.followed_id == user.id)
    result = await db.execute(stmt)
    followers = result.scalars().all()
    return followers
