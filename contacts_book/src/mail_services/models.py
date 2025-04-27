from datetime import date

from sqlalchemy import ForeignKey, String, Text, DateTime, func, JSON, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from contacts_book.src.core.base import Base


class EmailTemplates(Base):
    __tablename__ = "mail_letter_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    subject: Mapped[str] = mapped_column(String(100))
    params: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[date] = mapped_column(DateTime, default=func.now())

    emails = relationship("Email", back_populates="template", lazy="selectin")


class Email(Base):
    __tablename__ = "sent_mail_letters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status: Mapped[str] = mapped_column(String, default="pending")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    template_id: Mapped[int] = mapped_column(ForeignKey("mail_letter_templates.id"))
    send_at: Mapped[date] = mapped_column(DateTime, default=func.now())
    opened: Mapped[bool] = mapped_column(Boolean, default=False)

    template = relationship("EmailTemplates", back_populates="emails")
