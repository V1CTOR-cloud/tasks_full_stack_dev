from pydantic import BaseModel
from datetime import datetime
from app.models.project import ProjectStatus


class ProjectCreate(BaseModel):
    title: str
    description: str | None = None
    status: ProjectStatus


class ProjectUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: ProjectStatus | None = None


class ProjectResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    status: ProjectStatus
    created_at: datetime

    model_config = {"from_attributes": True}
