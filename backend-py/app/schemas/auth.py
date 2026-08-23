from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str