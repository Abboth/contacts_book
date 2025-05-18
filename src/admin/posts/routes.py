from pathlib import Path
from typing import Optional, List

from fastapi import APIRouter, Depends, status, Form
from sqlalchemy.ext.asyncio import AsyncSession

from src.admin.posts import repository as admin_posts_repository
from src.admin.posts.schemas import PostRatesResponseSchema
from src.auth.security import access, AccessLevel
from src.core.connection import get_db
from src.posts.schemas import PostSchema, PostResponseSchema
from src.posts.models import Post, PostRating

router = APIRouter(tags=["Staff manage panel"])


@router.patch("/{post_id}/edite_post",
              response_model=PostResponseSchema,
              dependencies=[Depends(access[AccessLevel.moderator])])
async def edite_post(description: Optional[str] = Form(default=None),
                     tag: Optional[List[str]] = Form(default=None),
                     post_id: int = Path(ge=1),
                     db: AsyncSession = Depends(get_db)) -> Post:
    """

    :param description: new description for post
    :type description: str
    :param tag: new tag for post
    :type tag: List[str]
    :param post_id: id of post to update
    :type post_id: int
    :param db: Database session.
    :type db: AsyncSession
    :return: Updated post description
    :rtype: Post
    """

    tags = await admin_posts_repository.tags_validation(tag, db)
    body = PostSchema(description=description or None, tag=tags or [])
    edited_post = await admin_posts_repository.edite_post(body, post_id, db)

    return edited_post


@router.delete("/{post_id}/delete_post",
               status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(access[AccessLevel.moderator])])
async def delete_post(post_id: int = Path(ge=1), db: AsyncSession = Depends(get_db)) -> None:
    """

    :param post_id: post id to delete
    :type post_id: int
    :param db: Database session.
    :type db: AsyncSession
    :return: None
    :rtype: status.HTTP_204_NO_CONTENT | status.HTTP_404_NOT_FOUND
    """
    await admin_posts_repository.delete_post(post_id, db)


@router.get("/{post_id}/get_rates", response_model=PostRatesResponseSchema,
            dependencies=[Depends(access[AccessLevel.moderator])])
async def get_rates(post_id: int = Path(ge=1), db: AsyncSession = Depends(get_db)) -> PostRatesResponseSchema:
    return await admin_posts_repository.get_rates(post_id, db)


@router.delete("/{post_id}/{rate_id}/delete_rate", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(access[AccessLevel.moderator])])
async def delete_rate(user_id: int = Path(ge=1), post_id: int = Path(ge=1), db: AsyncSession = Depends(get_db)) -> None:
    await admin_posts_repository.delete_rate(user_id, post_id, db)
