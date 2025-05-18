from enum import Enum
from typing import Callable

from sqlalchemy import Select

from src.posts.models import Post
from src.posts.schemas import PostFilterParamsSchema

filter_funcs: dict[str, Callable[[Select, PostFilterParamsSchema], Select]] = {
    "rating_gt": lambda stmt, v: stmt.where(Post.average_rating > v.rating_gt) if v.rating_gt else stmt,
    "rating_lt": lambda stmt, v: stmt.where(Post.average_rating < v.rating_lt) if v.rating_lt else stmt,
    "created_after": lambda stmt, v: stmt.where(Post.created_at > v.created_after) if v.created_after else stmt,
    "created_before": lambda stmt, v: stmt.where(Post.created_at < v.created_before) if v.created_before else stmt,
}

class OrderByEnum(str, Enum):
    created_at = "created_at"
    average_rating = "average_rating"
    user_id = "user_id"
