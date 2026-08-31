from pydantic import BaseModel
from datetime import datetime
from app.models.project import ProjectStatus


class ProjectCreate(BaseModel):
    title: str
    description: str | None = None
    status: ProjectStatus
    owner_id: int


class ProjectUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: ProjectStatus | None = None
    owner_id: int | None = None


class ProjectResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    status: ProjectStatus
    created_at: datetime
    owner_id: int

    model_config = {"from_attributes": True}
