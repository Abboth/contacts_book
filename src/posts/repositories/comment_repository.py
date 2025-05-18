from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core import message
from src.posts.models import Comment
from src.posts.schemas import CommentCreateSchema
from src.users.models import User


async def get_comment_by_id(comment_id: int, user: User, db: AsyncSession) -> Comment:
    stmt = select(Comment).where(Comment.id == comment_id, Comment.user_id == user.id)
    result = await db.execute(stmt)
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message.COMMENT_NOT_FOUND)

    return comment

async def get_comments_by_post_id(post_id: int, db: AsyncSession) -> list[Comment]:
    stmt = select(Comment).where(Comment.post_id == post_id)
    result = await db.execute(stmt)
    comments = result.scalars().all()

    return comments

async def get_all_comment_replies(comment_id: int, db: AsyncSession) -> list[Comment]:
    stmt = select(Comment).options(selectinload(Comment.replies)).where(Comment.id == comment_id)
    result = await db.execute(stmt)
    comments = result.scalars().all()

    return comments

async def create_comment(body: CommentCreateSchema, post_id: int,
                         user: User, db: AsyncSession, reply_id=None) -> Comment:
    new_comment = Comment(**body.model_dump(exclude_unset=True),
                          post_id=post_id, user_id=user.id, reply_id=reply_id)
    db.add(new_comment)

    await db.commit()
    await db.refresh(new_comment)

    return new_comment

async def edit_comment(body: CommentCreateSchema, user: User, comment_id: int, db: AsyncSession) -> Comment:
    comment = await get_comment_by_id(comment_id, user, db)

    comment.comment = body.comment

    await db.commit()
    await db.refresh(comment)

    return comment

async def delete_comment(comment_id: int, user: User, db: AsyncSession) -> Comment:
    comment = await get_comment_by_id(comment_id, user, db)

    await db.delete(comment)
    await db.commit()

    return comment

async def reply_comment(body: CommentCreateSchema, comment_id: int, user: User, db: AsyncSession) -> Comment:
    stmt = select(Comment).where(Comment.id == comment_id)
    result = await db.execute(stmt)
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message.COMMENT_NOT_FOUND)

    reply = await create_comment(body, comment.post_id, user, db, reply_id=comment.id)

    return reply
