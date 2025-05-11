from datetime import date

from pydantic import BaseModel, ConfigDict


class EmailResponseSchema(BaseModel):
    email: str
    tag: str | None

    model_config = ConfigDict(from_attributes=True)


class PhoneResponseSchema(BaseModel):
    phone: str
    tag: str | None

    model_config = ConfigDict(from_attributes=True)


class ContactResponseSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    birthday: date = None
    description: str = None

    email: list[EmailResponseSchema] = None

    phones: list[PhoneResponseSchema] = None

    model_config = ConfigDict(from_attributes=True)
