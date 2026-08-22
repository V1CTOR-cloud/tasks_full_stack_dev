from pydantic import BaseModel


class ColorCreate(BaseModel):
    color: str


class ColorResponse(BaseModel):
    color: str

    model_config = {"from_attributes": True}
