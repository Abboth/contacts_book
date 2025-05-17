from datetime import datetime
from typing import Optional

from pydantic import EmailStr, Field, BaseModel, ConfigDict, field_serializer, model_serializer

from src.posts.models import Post
from src.posts.shcemas import PostResponseSchema


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

class SubsListResponseSchema(BaseModel):
    username: str
    avatar: str

    model_config = ConfigDict(from_attributes=True)

class UserProfileResponseSchema(BaseModel):
    count_posts: int
    count_followers: int
    count_following: int
    username: str
    posts: Optional[list[PostResponseSchema]]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
