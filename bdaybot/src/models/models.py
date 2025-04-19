import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship, backref, DeclarativeBase
from sqlalchemy import String, Date, Integer, ForeignKey


class Base(DeclarativeBase):
    pass

class Person(Base):

    __tablename__ = "persons"
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(25), index=True)
    last_name: Mapped[str] = mapped_column(String(25))
    birthday: Mapped[datetime.date] = mapped_column(Date, nullable=True)
    description: Mapped[str] = mapped_column(String(500), nullable=True)

    phones = relationship("Phone", backref="person", cascade="all, delete")
    email = relationship("Email", backref="person", cascade="all, delete")


class Email(Base):

    __tablename__ = "emails"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(60))
    tag: Mapped[str] = mapped_column(String(20), nullable=True)

    person_id: Mapped[int] = mapped_column(Integer, ForeignKey("persons.id"))


class Phone(Base):

    __tablename__ = "phones"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    phone: Mapped[str] = mapped_column(String(16))
    tag: Mapped[str] = mapped_column(String(20), nullable=True)

    person_id: Mapped[int] = mapped_column(Integer, ForeignKey("persons.id"))

