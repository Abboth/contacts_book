from datetime import date
from typing import Optional

from pydantic import BaseModel


class EmailResponseSchema(BaseModel):
    email: str
    tag: str | None


class PhoneResponseSchema(BaseModel):
    phone: str
    tag: str | None

class ContactResponseSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    birthday: Optional[date] = None
    description: Optional[str] = None

    email: Optional[list[EmailResponseSchema]] = None

    phones: Optional[list[PhoneResponseSchema]] = None

    class Config:
        from_attributes = True
