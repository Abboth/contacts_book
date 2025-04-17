from typing import Optional
from datetime import date
from pydantic import BaseModel, EmailStr, Field

from bdaybot.src.schemas.custom_validators import ValidatorPhone, DateValidator


class AddContactSchema(BaseModel):
    first_name: str = Field(min_length=2, max_length=25)
    last_name: str = Field(min_length=2, max_length=25)

    birthday: Optional[DateValidator] = Field(default=None)

    email: Optional[EmailStr] = Field(default=None)
    mail_tag: Optional[str] = Field(default=None, max_length=20)
    phone_number: Optional[ValidatorPhone] = Field(default=None)
    phone_tag: Optional[str] = Field(default=None, max_length=20)

    hobby: Optional[str] = Field(default=None, min_length=3, max_length=70)

class ContactUpdateSchema(BaseModel):
    first_name: str = Field(min_length=2, max_length=25)
    last_name: str = Field(min_length=2, max_length=25)

    birthday: Optional[DateValidator] = Field(default=None)

    email: Optional[EmailStr] = Field(default=None)
    mail_tag: Optional[str] = Field(default=None, max_length=20)
    phone_number: Optional[ValidatorPhone] = Field(default=None)
    phone_tag: Optional[str] = Field(default=None, max_length=20)

    hobby: Optional[str] = Field(default=None, min_length=3, max_length=70)

class ContactResponseSchema(BaseModel):
    id: int
    first_name: str
    last_name: str

    birthday: Optional[date] = None

    email: Optional[str] = None
    mail_tag: Optional[str] = None
    phone_number: Optional[str] = None
    phone_tag: Optional[str] = None

    hobby: Optional[str] = None

    class Config:
        from_attributes = True

class RemoveContact(BaseModel):
    msg: str
