from datetime import date

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Date, Integer, ForeignKey, func

from contacts_book.src.core.base import Base

class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(25), index=True)
    last_name: Mapped[str] = mapped_column(String(25))
    birthday: Mapped[date] = mapped_column(Date, nullable=True)
    description: Mapped[str] = mapped_column(String(500), nullable=True)

    created_at: Mapped[date] = mapped_column(Date, default=func.now())
    updated_at: Mapped[date] = mapped_column(Date, nullable=True, onupdate=func.now())

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))  # корректно

    user = relationship("User", back_populates="contacts")  # правильно
    phones = relationship("Phone", backref="contact", cascade="all, delete")
    email = relationship("Email", backref="contact", cascade="all, delete")

# class Contact(Base):
#     __tablename__ = "contacts"
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     first_name: Mapped[str] = mapped_column(String(25), index=True)
#     last_name: Mapped[str] = mapped_column(String(25))
#     birthday: Mapped[date] = mapped_column(Date, nullable=True)
#     description: Mapped[str] = mapped_column(String(500), nullable=True)
#
#     created_at: Mapped[date] = mapped_column(Date, default=func.now())
#     updated_at: Mapped[date] = mapped_column(Date, nullable=True, onupdate=func.now())
#
#     user_id = relationship("User", backref="contacts", cascade="all, delete")
#     phones = relationship("Phone", backref="contacts", cascade="all, delete", lazy="selectin")
#     email = relationship("Email", backref="contacts", cascade="all, delete", lazy="selectin")


class Email(Base):
    __tablename__ = "emails"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(60))
    tag: Mapped[str] = mapped_column(String(20), nullable=True)

    created_at: Mapped[date] = mapped_column(Date, default=func.now())
    updated_at: Mapped[date] = mapped_column(Date, nullable=True, onupdate=func.now())

    contact_id: Mapped[int] = mapped_column(Integer, ForeignKey("contacts.id"))


class Phone(Base):
    __tablename__ = "phones"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    phone: Mapped[str] = mapped_column(String(16))
    tag: Mapped[str] = mapped_column(String(20), nullable=True)

    created_at: Mapped[date] = mapped_column(Date, default=func.now())
    updated_at: Mapped[date] = mapped_column(Date, nullable=True, onupdate=func.now())

    contact_id: Mapped[int] = mapped_column(Integer, ForeignKey("contacts.id"))
