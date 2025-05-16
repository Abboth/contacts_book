from datetime import datetime
from typing import Optional, Literal

from pydantic import Field, BaseModel, ConfigDict


class PostSchema(BaseModel):
    description: Optional[str] = Field(max_length=500)
    tag: Optional[list] = Field(max_length=30)


class ContentResponseSchema(BaseModel):
    image: str
    description: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class TagResponseSchema(BaseModel):
    name: str

    model_config = ConfigDict(from_attributes=True)


class PostResponseSchema(BaseModel):
    id: int
    content: ContentResponseSchema
    tags: list[TagResponseSchema]
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class QRResponseSchema(BaseModel):
    qr_code: str

    model_config = ConfigDict(from_attributes=True)


class CommentResponseSchema(BaseModel):
    id: int
    comment: str
    user_id: int
    post_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

class CommentCreateSchema(BaseModel):
    comment: str

class CommentRepliesResponseSchema(CommentResponseSchema):
    replies: list[CommentResponseSchema]