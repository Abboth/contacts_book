from datetime import date

from sqlalchemy import String, func, Date, Integer, ForeignKey, Boolean, Table, Column, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from theregram_proj.src.core.base import Base

followers = Table(
    "followers",
    Base.metadata,
    Column("follower_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("followed_id", Integer, ForeignKey("users.id"), primary_key=True),
)

class Role(Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(primary_key=True)
    role_name: Mapped[str] = mapped_column(String(10), unique=True)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    username: Mapped[str] = mapped_column(String(40))
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    hashed_pwd: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar: Mapped[str] = mapped_column(String(255))
    last_activity: Mapped[date] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), default=3)

    created_at: Mapped[date] = mapped_column(Date, default=func.now())
    updated_at: Mapped[date] = mapped_column(Date, nullable=True, onupdate=func.now())

    role = relationship("Role", backref="user", lazy="selectin")

    received_emails = relationship("Email", backref="user", cascade="all, delete", lazy="selectin")
    auth_session = relationship("AuthSession", backref="user", cascade="all, delete", lazy="selectin")

    followed = relationship(
        "User",
        secondary=followers,
        primaryjoin=id == followers.c.follower_id,
        secondaryjoin=id == followers.c.followed_id,
        backref="followers"
    )