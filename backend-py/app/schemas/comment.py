from pydantic import BaseModel
from datetime import datetime


class CommentCreate(BaseModel):
    comment: str


class CommentResponse(BaseModel):
    id: int
    comment: str
    author_id: int
    task_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
