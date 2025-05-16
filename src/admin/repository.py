from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status, HTTPException
from sqlalchemy.orm import selectinload

from src.core import message
from src.posts.models import Post, Tag
from src.posts.shcemas import PostSchema
from src.services.cloudinary_service import cloudinary_services
from src.users.models import User


async def get_post(post_id: int, db: AsyncSession) -> Post:
    stmt = (select(Post).where(Post.id == post_id)
            .options(selectinload(Post.content), selectinload(Post.tags)))
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message.POST_NOT_FOUND)

    return post

async def tags_validation(tags_list: list[str], db: AsyncSession) -> list[Tag]:
    tag_obj_list = []
    for tags in tags_list:
        if not tags.strip():
            continue

        raw_tags = [t.strip() for t in tags.split(",") if t.strip()]
        unique_tags = set(raw_tags)
        for tag_name in unique_tags:
            stmt = select(Tag).where(Tag.name == tag_name)
            result = await db.execute(stmt)
            tag_obj = result.scalar_one_or_none()
            if not tag_obj:
                tag_obj = Tag(name=tag_name)
                db.add(tag_obj)
                await db.flush()
            tag_obj_list.append(tag_obj)

    return tag_obj_list

async def edite_post(body: PostSchema, post_id: int, db: AsyncSession) -> Post:
    post = await get_post(post_id, db)
    tag_list = await tags_validation(body.tag, db)

    post.content.description = body.description
    post.tags = tag_list

    await db.commit()
    await db.refresh(post)

    return post


async def delete_post(post_id: int, db: AsyncSession) -> None:
    post = await get_post(post_id, db)

    await db.delete(post)
    await db.commit()

    await cloudinary_services.delete_file(post.content.image)
    if post.content.qr_code:
        await cloudinary_services.delete_file(post.content.qr_code)


async def delete_user(user_id: int, db: AsyncSession) -> None:
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    await db.delete(user)
    await db.commit()

    await cloudinary_services.delete_user_files(user.email)

