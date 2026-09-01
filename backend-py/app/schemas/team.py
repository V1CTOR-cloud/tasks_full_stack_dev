from pydantic import BaseModel
from app.schemas.color import ColorResponse


class TeamCreate(BaseModel):
    name: str
    hex_color: str | None = None


class TeamUpdate(BaseModel):
    name: str | None = None
    hex_color: str | None = None


class TeamResponse(BaseModel):
    id: int
    name: str
    hex_color: str | None = None
    color: ColorResponse | None = None

    model_config = {"from_attributes": True}


class AddTeamToProject(BaseModel):
    team_id: int

class AddUserToTeam(BaseModel):
    user_id: int