from datetime import date

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, Integer, ForeignKey, func

from src.core.base import Base

class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(25), index=True)
    last_name: Mapped[str] = mapped_column(String(25))
    birthday: Mapped[date] = mapped_column(DateTime, nullable=True)
    description: Mapped[str] = mapped_column(String(500), nullable=True)

    created_at: Mapped[date] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column(DateTime, nullable=True, onupdate=func.now())

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    phones = relationship("ContactsPhone", backref="contact", cascade="all, delete", lazy="joined")
    email = relationship("ContactsEmail", backref="contact", cascade="all, delete", lazy="joined")


class ContactsEmail(Base):
    __tablename__ = "emails"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(60))
    tag: Mapped[str] = mapped_column(String(20), nullable=True)

    created_at: Mapped[date] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column(DateTime, nullable=True, onupdate=func.now())

    contact_id: Mapped[int] = mapped_column(Integer, ForeignKey("contacts.id"))


class ContactsPhone(Base):
    __tablename__ = "phones"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    phone: Mapped[str] = mapped_column(String(16))
    tag: Mapped[str] = mapped_column(String(20), nullable=True)

    created_at: Mapped[date] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column(DateTime, nullable=True, onupdate=func.now())

    contact_id: Mapped[int] = mapped_column(Integer, ForeignKey("contacts.id"))
