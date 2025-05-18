from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status, HTTPException
from sqlalchemy.orm import selectinload

from src.core import message
from src.posts.filter_enums import OrderByEnum, filter_funcs
from src.posts.models import Post, Content, Tag
from src.posts.schemas import PostSchema
from src.services.cloudinary_service import cloudinary_services
from src.users.models import User, Follower


async def get_feed_posts(user: User, db: AsyncSession) -> list[Post]:
    subquery = select(Follower.followed_id).where(Follower.follower_id == user.id).subquery()
    stmt = (
        select(Post)
        .where(Post.user_id.in_(select(subquery.c.followed_id)))
        .options(
            selectinload(Post.content),
            selectinload(Post.tags),
        )
        .order_by(Post.created_at.desc())
    )
    result = await db.execute(stmt)
    posts = result.scalars().all()

    return posts


async def get_post_by_id(post_id: int, db: AsyncSession) -> Post:
    stmt = (select(Post).where(Post.id == post_id)
            .options(selectinload(Post.content), selectinload(Post.tags)))
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message.POST_NOT_FOUND)

    return post


async def get_user_post(post_id: int, user_id: int, db: AsyncSession) -> Post:
    stmt = (select(Post).where(Post.id == post_id, Post.user_id == user_id)
            .options(selectinload(Post.content), selectinload(Post.tags)))
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message.POST_NOT_FOUND)

    return post


async def get_all_user_posts(user_id: int, db: AsyncSession) -> list[Post] | None:
    stmt = (select(Post).where(Post.user_id == user_id)
            .options(selectinload(Post.content), selectinload(Post.tags)))
    result = await db.execute(stmt)
    posts = result.scalars().all()

    return posts


async def search_posts(tag: str, filter_values, order_by: list[OrderByEnum],
                       db: AsyncSession) -> list[Post]:
    stmt = select(Post).where(Post.tags.any(Tag.name == tag))
    if filter_values:
        for value in filter_values:
            func = filter_funcs.get(value)
            stmt = func(stmt, filter_values)
    if order_by:
        for order in order_by:
            stmt = stmt.order_by(getattr(Post, order.value).desc())

    result = await db.execute(stmt)
    posts = result.scalars().all()

    return posts


async def tags_validation(tags_list: list[str], db: AsyncSession) -> list[Tag]:
    tag_obj_list = []
    for tags in tags_list:
        if not tags.strip():
            continue

        raw_tags = [t.strip() for t in tags.split(",") if t.strip()]
        unique_tags = set(raw_tags)
        if len(unique_tags) > 5:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You can add maximum 5 tags")
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


async def create_post(body: PostSchema, image_url: str, user: User, db: AsyncSession) -> Post:
    post_content = Content(description=body.description, image=image_url)
    post = Post(user_id=user.id, content=post_content, tags=body.tag)

    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


async def edite_post(body: PostSchema, post_id: int, user: User, db: AsyncSession) -> Post:
    post = await get_user_post(post_id, user.id, db)
    tag_list = await tags_validation(body.tag, db)

    post.content.description = body.description
    post.tags = tag_list

    await db.commit()
    await db.refresh(post)

    return post


async def delete_post(post_id: int, user: User, db: AsyncSession) -> None:
    post = await get_user_post(post_id, user.id, db)

    await db.delete(post)
    await db.commit()
    await cloudinary_services.delete_file(post.content.image)
    if post.content.qr_code:
        await cloudinary_services.delete_file(post.content.qr_code)


async def update_qr_code(post: Post, qr_code: str, db: AsyncSession) -> None:
    post.content.qr_code = qr_code
    await db.commit()
