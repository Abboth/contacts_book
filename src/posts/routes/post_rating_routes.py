import uuid
from pathlib import Path
from typing import Optional, List

from fastapi import APIRouter, UploadFile, Depends, File, status, Form
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.security import check_active_user
from src.core.connection import get_db
from src.services.cloudinary_service import cloudinary_services
from src.posts.schemas import PostSchema, PostResponseSchema, QRResponseSchema, PostRatingSchema
from src.posts.repositories import post_rating_repository
from src.users.models import User
from src.posts.models import Post
from src.posts.repositories import post_repository as post_repository

router = APIRouter(tags=["Ratings"])


@router.post("/{post_id}/rate_post", response_model=PostResponseSchema, status_code=status.HTTP_201_CREATED)
async def rate_post(body: PostRatingSchema, post_id: int = Path(ge=1),
                    user: User = Depends(check_active_user), db: AsyncSession = Depends(get_db)):
    return await post_rating_repository.rate_post(body.rating, post_id, user, db)