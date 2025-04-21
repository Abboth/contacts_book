from typing import Optional
from pydantic import BaseModel, EmailStr, Field

from contacts_book.src.schemas.custom_validators import ValidatorPhone, DateValidator


class AddContactSchema(BaseModel):
    first_name: str = Field(min_length=2, max_length=25)
    last_name: str = Field(min_length=2, max_length=25)

    birthday: Optional[DateValidator] = Field(default=None)

    email: Optional[EmailStr] = Field(default=None)
    mail_tag: Optional[str] = Field(default=None, max_length=20)
    phone_number: Optional[ValidatorPhone] = Field(default=None)
    phone_tag: Optional[str] = Field(default=None, max_length=20)

    description: Optional[str] = Field(default=None, min_length=3, max_length=500)

class ContactUpdateSchema(BaseModel):
    first_name: str = Field(min_length=2, max_length=25)
    last_name: str = Field(min_length=2, max_length=25)

    birthday: Optional[DateValidator] = Field(default=None)

    description: Optional[str] = Field(default=None, min_length=3, max_length=500)

class AddPhoneSchema(BaseModel):
    phone_number: ValidatorPhone = Field(default=None)
    phone_tag: str = Field(default=None, max_length=20)

class PhoneUpdateSchema(BaseModel):
    phone_number: ValidatorPhone

class AddEmailSchema(BaseModel):
    email: EmailStr = Field(default=None)
    mail_tag: str = Field(default=None, max_length=20)

class EmailUpdateSchema(BaseModel):
    email: EmailStr



