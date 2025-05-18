from datetime import date

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, ForeignKey, func, DateTime

from src.core.base import Base
from src.users.models import User


class AuthSession(Base):
    __tablename__ = "auth_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    refresh_token: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    device_type: Mapped[str] = mapped_column(String)

    created_at: Mapped[date] = mapped_column(DateTime, default=func.now())
    expires_at: Mapped[date] = mapped_column(DateTime, default=None, onupdate=func.now())

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

