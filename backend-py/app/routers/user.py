from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate

from app.dependencies.auth import get_current_user
from app.crud.user import get_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", status_code=status.HTTP_202_ACCEPTED)
def patch_me(
    user: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    existing_user = get_user(db, current_user.id)

    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(existing_user, key, value)

    db.commit()
    db.refresh(existing_user)

    return {"message": "User updated successfully", "User": existing_user}


@router.delete("/me", status_code=status.HTTP_202_ACCEPTED)
def del_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing_user = get_user(db, current_user.id)

    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(existing_user)
    db.commit()

    return {"message": "User deleted successfully"}