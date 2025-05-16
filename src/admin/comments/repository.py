from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import message
from src.posts.models import Comment
from src.posts.shcemas import CommentCreateSchema


async def get_comment_by_id(comment_id: int, user_id: int, db: AsyncSession) -> Comment:
    stmt = select(Comment).where(Comment.id == comment_id, Comment.user_id == user_id)
    result = await db.execute(stmt)
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message.COMMENT_NOT_FOUND)

    return comment


async def edit_comment(body: CommentCreateSchema, user_id: int, comment_id: int, db: AsyncSession) -> Comment:
    comment = await get_comment_by_id(comment_id, user_id, db)

    comment.comment = body.comment

    await db.commit()
    await db.refresh(comment)

    return comment


async def delete_comment(comment_id: int, user_id: int, db: AsyncSession) -> Comment:
    comment = await get_comment_by_id(comment_id, user_id, db)

    await db.delete(comment)
    await db.commit()

    return comment


