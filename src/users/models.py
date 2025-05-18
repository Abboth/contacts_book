from datetime import datetime, date

from sqlalchemy import String, func, Integer, ForeignKey, Boolean, DateTime, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.base import Base
from src.core import models

class Follower(Base):
    __tablename__ = "followers"
    follower_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    followed_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)

    follower = relationship("User", foreign_keys=[follower_id], back_populates="following", lazy="selectin")
    followed = relationship("User", foreign_keys=[followed_id], back_populates="followers", lazy="selectin")


class Role(Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role_name: Mapped[str] = mapped_column(String(10), unique=True)



class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    profile_slug: Mapped[str] = mapped_column(String(40), nullable=False, unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(50), nullable=False)
    hashed_pwd: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    birthday: Mapped[date] = mapped_column(Date, nullable=True)
    last_activity: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), default=3)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, onupdate=func.now())

    role = relationship("Role", backref="user", lazy="selectin")

    contacts = relationship("Contact", backref="user", cascade="all, delete", lazy="selectin")
    received_emails = relationship("Email", backref="user", cascade="all, delete", lazy="selectin")
    auth_session = relationship("AuthSession", backref="user", cascade="all, delete", lazy="selectin")
    posts = relationship("Post", backref="user", cascade="all, delete", lazy="selectin")
    comments = relationship("Comment", backref="user", cascade="all, delete", lazy="selectin")

    followers = relationship("Follower", foreign_keys="[Follower.followed_id]",
                             back_populates="followed", lazy="selectin")
    following = relationship("Follower", foreign_keys="[Follower.follower_id]",
                             back_populates="follower", lazy="selectin")
