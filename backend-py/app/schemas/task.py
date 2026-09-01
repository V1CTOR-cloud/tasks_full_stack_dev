from datetime import datetime
from pydantic import BaseModel
from app.models.task import TaskStatus,TaskPriority


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_date: datetime | None = None
    project_id: int


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_date: datetime | None = None
    user_id: int | None = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    status: TaskStatus
    priority: TaskPriority
    due_date: datetime | None = None
    user_id: int | None
    project_id: int

    model_config = {"from_attributes": True}
