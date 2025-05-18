from fastapi import APIRouter, Depends, status

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.security import check_active_user
from src.core.connection import get_db
from src.posts.shcemas import CommentResponseSchema, CommentCreateSchema, CommentRepliesResponseSchema
from src.users.models import User
from src.posts.models import Comment
from src.posts.repositories import comment_repository

router = APIRouter(tags=["Comments"])


@router.get("/{post_id}/comments", response_model=list[CommentResponseSchema])
async def get_comments(post_id: int, db: AsyncSession = Depends(get_db)) -> list[Comment]:
    return await comment_repository.get_comments_by_post_id(post_id, db)


@router.post("/{post_id}/comments", response_model=CommentResponseSchema)
async def create_comment(body: CommentCreateSchema, post_id: int,
                         db: AsyncSession = Depends(get_db),
                         user: User = Depends(check_active_user)) -> Comment:
    new_comment = await comment_repository.create_comment(body, post_id, user, db)
    return new_comment


@router.get("/{post_id}/comments/{comment_id}", response_model=CommentResponseSchema)
async def get_comment(comment_id: int, user: User = Depends(check_active_user),
                      db: AsyncSession = Depends(get_db)) -> Comment:
    return await comment_repository.get_comment_by_id(comment_id, user, db)


@router.post("/{post_id}/comments/{comment_id}/reply", response_model=CommentResponseSchema)
async def reply_comment(body: CommentCreateSchema, comment_id: int,
                        db: AsyncSession = Depends(get_db),
                        user: User = Depends(check_active_user)) -> Comment:
    return await comment_repository.reply_comment(body, comment_id, user, db)


@router.patch("/{post_id}/comments/{comment_id}", response_model=CommentResponseSchema)
async def edite_comment(body: CommentCreateSchema, comment_id: int,
                        db: AsyncSession = Depends(get_db),
                        user: User = Depends(check_active_user)) -> Comment:
    updated_comment = await comment_repository.edit_comment(body, user, comment_id, db)
    return updated_comment


@router.delete("/{post_id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(comment_id: int, user: User = Depends(check_active_user),
                         db: AsyncSession = Depends(get_db)) -> None:
    await comment_repository.delete_comment(comment_id, user, db)


@router.get("/{post_id}/comments/{comment_id}/replies", response_model=list[CommentRepliesResponseSchema])
async def get_comment_replies(comment_id: int, db: AsyncSession = Depends(get_db)) -> list[Comment]:
    return await comment_repository.get_all_comment_replies(comment_id, db)
