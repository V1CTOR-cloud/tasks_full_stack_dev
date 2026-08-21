from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import os
from datetime import datetime, timedelta, timezone

from jose import jwt # type: ignore
from dotenv import load_dotenv

from app.database import get_db
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES")) # type: ignore


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES  # type: ignore
    )

    payload = {"sub": str(user_id), "exp": expire}

    return jwt.encode(
        payload,
        SECRET_KEY,  # type: ignore
        algorithm=ALGORITHM,  # type: ignore
    )


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


@router.post("/register")
def register(user: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = (
        db.query(User)
        .filter((User.username == user.username) | (User.email == user.email))
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400, detail="Username or email already registered"
        )

    hashed_password = hash_password(user.password)

    new_user = User(username=user.username, email=user.email, password=hashed_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}


@router.post("/login", response_model=TokenResponse)
def login(user: LoginRequest, db: Session = Depends(get_db)):
    
    if not user.username and not user.email:
        raise HTTPException(status_code=401, detail="Username or email is required")

    if user.username:
        db_user = db.query(User).filter(User.username == user.username).first()
    else:
        db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token(db_user.id)

    return {"access_token": access_token, "token_type": "bearer"}
