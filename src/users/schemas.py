from datetime import date, datetime
from typing import Optional, Annotated

from pydantic import EmailStr, Field, BaseModel, ConfigDict

from src.posts.shcemas import PostResponseSchema


class UserSchema(BaseModel):
    profile_slug: str
    display_name: str = Field(min_length=2, max_length=25)
    email: EmailStr
    password: str = Field(min_length=6, max_length=10)


class UserResponseSchema(BaseModel):
    id: int
    profile_slug: str
    display_name: str
    email: EmailStr
    avatar: str

    model_config = ConfigDict(from_attributes=True)


class EditeUserSchema(BaseModel):
    display_name: Annotated[Optional[str], Field(min_length=2, max_length=25)] = None
    birthday: Optional[date] = None

    old_password: Annotated[Optional[str], Field(min_length=6, max_length=10)] = None

    new_password: Annotated[Optional[str], Field(min_length=6, max_length=10)] = None
    repeat_new_password: Annotated[Optional[str], Field(min_length=6, max_length=10)] = None


class SubsListResponseSchema(BaseModel):
    display_name: str
    avatar: str

    model_config = ConfigDict(from_attributes=True)


class UserProfileResponseSchema(BaseModel):
    count_posts: int
    count_followers: int
    count_following: int
    display_name: str
    posts: Optional[list[PostResponseSchema]]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
