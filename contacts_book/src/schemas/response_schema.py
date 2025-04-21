from datetime import date

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
    birthday: date = None
    description: str = None

    email: list[EmailResponseSchema] = None

    phones: list[PhoneResponseSchema] = None

    class Config:
        from_attributes = True
