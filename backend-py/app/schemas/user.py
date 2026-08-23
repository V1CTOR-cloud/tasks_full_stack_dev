from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    team_id: int | None = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    model_config = {"from_attributes": True}
