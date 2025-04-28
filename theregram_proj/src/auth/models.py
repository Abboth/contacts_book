from datetime import date

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Date, Integer, ForeignKey, func

from theregram_proj.src.core.base import Base


class AuthSession(Base):
    __tablename__ = "auth_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    refresh_token: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    device_type: Mapped[str] = mapped_column(String)

    created_at: Mapped[date] = mapped_column(Date, default=func.now())
    expires_at: Mapped[date] = mapped_column(Date, default=None, onupdate=func.now())

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

