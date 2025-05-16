from typing import Optional

from pydantic import EmailStr, Field, BaseModel, ConfigDict, field_serializer


class UserSchema(BaseModel):
    username: str = Field(min_length=2, max_length=25)
    email: EmailStr
    password: str = Field(min_length=6, max_length=10)


class UserResponseSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    avatar: str

    model_config = ConfigDict(from_attributes=True)


