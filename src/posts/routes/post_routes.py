import uuid
from pathlib import Path
from typing import Optional, List

from fastapi import APIRouter, UploadFile, Depends, File, status, Form
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.security import auth_security
from src.core.connection import get_db
from src.services.cloudinary_service import cloudinary_services
from src.posts.shcemas import PostSchema, PostResponseSchema, QRResponseSchema
from src.users.models import User
from src.posts.models import Post
from src.posts.repositories import post_repository as post_repository

router = APIRouter(tags=["Posts"])


@router.get("/{user_id}", response_model=PostResponseSchema)
async def get_posts(user_id: int = Path(ge=1), db: AsyncSession = Depends(get_db)) -> list[Post]:
    """
    Get all posts of user

    :param user_id: id of user
    :type user_id: int
    :param db: Database session.
    :type db: AsyncSession
    """

    return await post_repository.get_all_user_posts(user_id, db)


@router.get("/{user_id}/{post_id}", response_model=PostResponseSchema)
async def get_posts(user_id: int = Path(ge=1), post_id: int = Path(ge=1), db: AsyncSession = Depends(get_db)) -> Post:
    """
    Get posts of user

    :param user_id: user id
    :type user_id: int
    :param post_id: id of post to get
    :type post_id: int
    :param db: Database session.
    :type db: AsyncSession
    """

    return await post_repository.get_user_post(post_id, user_id, db)

@router.post("/create_post", response_model=PostResponseSchema,
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(RateLimiter(times=4, seconds=60))])
async def create_post(description: Optional[str] = Form(default=None),
                      tag: Optional[List[str]] = Form(default=None),
                      image: UploadFile = File, db: AsyncSession = Depends(get_db),
                      image_filter: Optional[cloudinary_services.ImageTransformation] = Form(default=None),
                      current_user: User = Depends(auth_security.get_current_user)) -> Post:
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
    :param current_user: Currently authenticated user.
    :type current_user: User
    :return: Created post.
    :rtype: Post
    """
    tags = await post_repository.tags_validation(tag, db)
    body = PostSchema(description=description or None, tag=tags or [])

    transformation = [{"width": 500, "height": 500, "crop": "fill"}]
    if image_filter:
        transformation.insert(0, {"effect": image_filter.value})

    folder = f"{current_user.email}/user_shots"
    public_id = f"{uuid.uuid4()}"
    cloud_storage_url = await cloudinary_services.upload_file(image.file, folder, public_id, transformation)

    new_post = await post_repository.create_post(body, cloud_storage_url, current_user, db)

    return new_post

@router.post("/create_qr", response_model=QRResponseSchema,
             status_code=status.HTTP_201_CREATED)
async def create_qr(post_id: int, db: AsyncSession = Depends(get_db),
                    current_user: User = Depends(auth_security.get_current_user)) -> QRResponseSchema:
    post = await post_repository.get_user_post(post_id, current_user, db)
    if post.content.qr_code:
        return QRResponseSchema(qr_code=post.content.qr_code)
    folder = f"{current_user.email}/user_QR_codes"
    public_id = f"{uuid.uuid4()}"

    qr_code_link = await cloudinary_services.create_qr_code(post.content.image, folder, public_id)
    await post_repository.update_qr_code(post, qr_code_link, db)
    return QRResponseSchema(qr_code=qr_code_link)


@router.patch("/edite_post/{post_id}",
              response_model=PostResponseSchema,
              dependencies=[Depends(RateLimiter(times=4, seconds=60))])
async def edite_post(description: Optional[str] = Form(default=None),
                     tag: Optional[List[str]] = Form(default=None),
                     post_id: int = Path(ge=1),
                     db: AsyncSession = Depends(get_db),
                     current_user: User = Depends(auth_security.get_current_user)) -> Post:
    """

    :param description: new description for post
    :type description: str
    :param tag: new tag for post
    :type tag: List[str]
    :param post_id: id of post to update
    :type post_id: int
    :param db: Database session.
    :type db: AsyncSession
    :param current_user: Currently authenticated user.
    :type current_user: User
    :return: Updated post description
    :rtype: Post
    """
    tags = await post_repository.tags_validation(tag, db)
    body = PostSchema(description=description or None, tag=tags or [])
    edited_post = await post_repository.edite_post(body, post_id, current_user, db)

    return edited_post


@router.delete("/delete_post/{post_id}",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(auth_security.get_current_user)) -> None:
    """

    :param post_id: post id to delete
    :type post_id: int
    :param db: Database session.
    :type db: AsyncSession
    :param current_user: Currently authenticated user.
    :type current_user: User
    :return: None
    :rtype: status.HTTP_204_NO_CONTENT | status.HTTP_404_NOT_FOUND
    """
    await post_repository.delete_post(post_id, current_user, db)




