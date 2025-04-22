from datetime import date

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Date, Integer, ForeignKey, func

from contacts_book.src.core.base import Base


class AuthSession(Base):
    __tablename__ = "auth_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    refresh_token: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    device_type: Mapped[str] = mapped_column(String)

    created_at: Mapped[date] = mapped_column(Date, default=func.now())
    expires_at: Mapped[date] = mapped_column(Date, default=None, onupdate=func.now())

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # user = relationship("User", back_populates="auth_session")


# class AuthSession(Base):
#     __tablename__ = "auth_sessions"
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     refresh_token: Mapped[str] = mapped_column(String, unique=True, nullable=False)
#     device_type: Mapped[str] = mapped_column(String)
#
#     created_at: Mapped[date] = mapped_column(Date, default=func.now())
#     expires_at: Mapped[date] = mapped_column(Date, default=None, onupdate=func.now())
#
#
#     user_id =relationship("User", backref="auth_sessions", uselist=False, cascade="all, delete", lazy="selectin")
