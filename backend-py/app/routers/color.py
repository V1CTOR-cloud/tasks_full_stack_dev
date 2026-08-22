from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db

from app.models.color import Color
from app.models.user import User
from app.schemas.color import ColorResponse, ColorCreate
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/colors", tags=["Colors"])


@router.get("/", response_model=list[ColorResponse], status_code=status.HTTP_200_OK)
def get_all(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return db.query(Color).all()


@router.post("/", status_code=status.HTTP_201_CREATED)
def add_color(
    color_obj: ColorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_color = Color(color=color_obj.color)

    db.add(new_color)
    db.commit()
    db.refresh(new_color)
    return {"message": "Color registered successfully"}


@router.delete("/{color}", status_code=status.HTTP_200_OK)
def del_color(
    color: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing_color = db.query(Color).filter(Color.color == color).first()

    if not existing_color:
        raise HTTPException(status_code=404, detail="Color not found")

    db.delete(existing_color)
    db.commit()

    return {"message": "Color deleted successfully"}
