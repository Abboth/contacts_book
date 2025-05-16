from fastapi import APIRouter, Depends, status

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.security import access, AccessLevel
from src.core.connection import get_db
from src.posts.shcemas import CommentResponseSchema, CommentCreateSchema
from src.posts.models import Comment
from src.admin.comments import repository as admin_comment_repository

router = APIRouter(tags=["Staff manage panel"])


@router.patch("/{post_id}/comments/{comment_id}", response_model=CommentResponseSchema,
              dependencies=[Depends(access[AccessLevel.moderator])])
async def edite_comment(body: CommentCreateSchema, comment_id: int,
                        user_id: int,
                        db: AsyncSession = Depends(get_db)) -> Comment:
    updated_comment = await admin_comment_repository.edit_comment(body, user_id, comment_id, db)
    return updated_comment


@router.delete("/{post_id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(access[AccessLevel.moderator])])
async def delete_comment(comment_id: int, user_id: int,
                         db: AsyncSession = Depends(get_db)) -> None:
    await admin_comment_repository.delete_comment(comment_id, user_id, db)

