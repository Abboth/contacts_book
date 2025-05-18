from pydantic import BaseModel, ConfigDict

from src.posts.schemas import PostResponseSchema
from src.users.schemas import UserResponseSchema


class UserRatesResponseSchema(BaseModel):
    user: UserResponseSchema
    rating: int

    model_config = ConfigDict(from_attributes=True)

class PostRatesResponseSchema(BaseModel):
    post: PostResponseSchema
    user: list[UserRatesResponseSchema]

    model_config = ConfigDict(from_attributes=True)