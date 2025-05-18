from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from src.core import message
from src.core.connection import celery_app, sync_sessionmanager
from src.posts.models import Post
from src.posts.models import PostRating
from src.posts.repositories import post_repository
from src.services.redis_service import redis_manager
from src.users.models import User


async def check_already_rated(post_id: int, user_id: int, db: AsyncSession) -> None:
    stmt = select(PostRating).where(PostRating.post_id == post_id, PostRating.user_id == user_id)
    result = await db.execute(stmt)
    already_rated = result.one_or_none()
    if already_rated:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message.ALREADY_RATED)


async def rate_post(rate: int, post_id: int, user: User, db: AsyncSession) -> Post:
    post = await post_repository.get_post_by_id(post_id, db)
    if post.user_id == user.id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message.CANT_RATE_YOUR_POST)
    await check_already_rated(post_id, user.id, db)

    new_rate = PostRating(post_id=post_id, user_id=user.id, rating=rate)
    db.add(new_rate)
    await db.commit()
    await db.refresh(post)

    key = f"rating_update:{post_id}"
    if not await redis_manager.get_obj(key):
        await redis_manager.set_obj(key, True, ex=5)
        recalculate_post_rating.delay(post_id)

    return post


@celery_app.task
def recalculate_post_rating(post_id: int):
    with sync_sessionmanager.session() as db:
        stmt = (
            select(func.avg(PostRating.rating))
            .where(PostRating.post_id == post_id)
        )
        result = db.execute(stmt).scalar()
        avg_rating = round(result, 2)

        post = db.get(Post, post_id)
        if post:
            post.average_rating = avg_rating
            db.commit()
