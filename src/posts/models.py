from typing import Optional

from sqlalchemy import Integer, String, DateTime, ForeignKey, func, Float
from sqlalchemy.orm import Mapped, mapped_column, backref
from sqlalchemy.orm import relationship
from src.core.base import Base
from datetime import datetime


class PostTag(Base):
    __tablename__ = "posts_tags"

    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)


class PostRating(Base):
    __tablename__ = "posts_ratings"

    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)

    post = relationship("Post", back_populates="ratings", lazy="selectin")
    user = relationship("User", back_populates="ratings", lazy="selectin")


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, onupdate=func.now())
    average_rating: Mapped[float] = mapped_column(Float, nullable=True, default=0)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    content = relationship("Content", backref="post", cascade="all, delete", lazy="selectin", uselist=False)
    comments = relationship("Comment", backref="post", cascade="all, delete", lazy="selectin")
    ratings = relationship("PostRating", back_populates="post", cascade="all, delete", lazy="selectin")
    tags = relationship("Tag", secondary="posts_tags", back_populates="posts", lazy="selectin")



class Content(Base):
    __tablename__ = "contents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    image: Mapped[str] = mapped_column(String(255))
    qr_code: Mapped[str] = mapped_column(String(255), nullable=True)

    post_id: Mapped[int] = mapped_column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)

    posts = relationship( "Post", secondary="posts_tags", back_populates="tags", lazy="selectin")


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    comment: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, onupdate=func.now())
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reply_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("comments.id",
                                                                        ondelete="CASCADE"), nullable=True)

    replies: Mapped[list["Comment"]] = relationship(
        backref=backref("parent", remote_side=[id]),
        cascade="all, delete-orphan"
    )

