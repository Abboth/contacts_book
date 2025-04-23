from datetime import date

from sqlalchemy import String, func, Date, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from contacts_book.src.core.base import Base



class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(40))
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    hashed_pwd: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar: Mapped[str] = mapped_column(String(255))

    created_at: Mapped[date] = mapped_column(Date, default=func.now())
    updated_at: Mapped[date] = mapped_column(Date, nullable=True, onupdate=func.now())

    contacts = relationship("Contact", backref="user", cascade="all, delete", lazy="selectin")
    auth_session = relationship("AuthSession", backref="user", cascade="all, delete", lazy="selectin")
