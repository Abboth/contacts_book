import uuid
from pathlib import Path
from typing import Optional, List

from fastapi import APIRouter, UploadFile, Depends, File, status, Form
from sqlalchemy.ext.asyncio import AsyncSession

from src.admin import repository as admin_repository
from src.auth.security import access, AccessLevel
from src.core.connection import get_db
from src.services.cloudinary_service import cloudinary_services
from src.posts.shcemas import PostSchema, PostResponseSchema
from src.posts.models import Post
from src.users import repository as user_repository
from src.posts import repository as post_repository

router = APIRouter(tags=["Staff manage panel"])


@router.post("/create_post", response_model=PostResponseSchema,
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(access[AccessLevel.moderator])])
async def create_post(user_email: str = Form(default=None),
                      description: Optional[str] = Form(default=None),
                      tag: Optional[List[str]] = Form(default=None),
                      image: UploadFile = File, db: AsyncSession = Depends(get_db),
                      image_filter: Optional[cloudinary_services.ImageTransformation] = Form(default=None)) -> Post:
    """
    Add a new post for the current user.

    :param description: description of post.
    :type description: str
    :param tag: dedicated tags for post.
    :type tag: str
    :param image: Image file to upload.
    :type image: UploadFile
    :param image_filter: filter for image
    :type image_filter: str
    :param db: Database session.
    :type db: AsyncSession
    :return: Created post.
    :rtype: Post
    """
    tags = await admin_repository.tags_validation(tag, db)
    body = PostSchema(description=description or None, tag=tags or [], image_filter=image_filter)

    transformation = [{"width": 500, "height": 500, "crop": "fill"}]
    if image_filter:
        transformation.insert(0, {"effect": image_filter.value})

    user = await user_repository.get_user_by_email(user_email, db)
    folder = f"user_shots/{user.email}"
    public_id = f"{uuid.uuid4()}"
    cloud_storage_url = await cloudinary_services.upload_file(image.file, folder, public_id, transformation)

    new_post = await post_repository.create_post(body, cloud_storage_url, user, db)

    return new_post


@router.patch("/edite_post/{post_id}",
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

    tags = await admin_repository.tags_validation(tag, db)
    body = PostSchema(description=description or None, tag=tags or [])
    edited_post = await admin_repository.edite_post(body, post_id, db)

    return edited_post


@router.delete("/delete_post/{post_id}",
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
    await admin_repository.delete_post(post_id, db)


@router.delete("/delete_user/{user_id}",
               status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(access[AccessLevel.admin])])
async def delete_post(user_id: int = Path(ge=1), db: AsyncSession = Depends(get_db)) -> None:
    """

    :param post_id: user id to delete
    :type post_id: int
    :param db: Database session.
    :type db: AsyncSession
    :return: None
    :rtype: status.HTTP_204_NO_CONTENT | status.HTTP_404_NOT_FOUND
    """
    await admin_repository.delete_user(user_id, db)