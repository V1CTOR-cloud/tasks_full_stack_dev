from pydantic import BaseModel
from app.models.color import Color


class TeamCreate(BaseModel):
    name: str


class TeamUpdate(BaseModel):
    name: str | None = None
    color: Color | None = None
