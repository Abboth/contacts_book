from datetime import datetime
from typing import Optional, Literal, Annotated

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
    average_rating: float = 0

    model_config = ConfigDict(from_attributes=True)

class PostRatingSchema(BaseModel):
    rating: Literal[1, 2, 3, 4, 5]

class PostRatingResponseSchema(BaseModel):
    post: PostResponseSchema
    user_id: int
    rating: int

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


class PostFilterParamsSchema(BaseModel):
    rating_gt: Annotated[Optional[float], Field(ge=1, le=5)] = None
    rating_lt: Annotated[Optional[float], Field(ge=1, le=5)] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
