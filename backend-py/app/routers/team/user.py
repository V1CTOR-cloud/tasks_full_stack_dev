from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user

from app.crud.team import get_team, is_user_in_team
from app.crud.user import get_user

from app.models.user import User

from app.schemas.user import UserResponse
from app.schemas.team import AddUserToTeam

router = APIRouter(prefix="/teams", tags=["Teams Users"])


@router.get(
    "/{team_id}/users",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
)
def get_users_from_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    team = get_team(db, team_id)

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    if not is_user_in_team(db, current_user, team):
        raise HTTPException(
            status_code=404,
            detail=f"the user {current_user.username} does not belong to {team.name}",
        )

    return team.users


@router.post(
    "/{team_id}/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_user_to_team(
    team_id: int,
    new_team: AddUserToTeam,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    team = get_team(db, team_id)

    if not team:
        raise HTTPException(
            status_code=404,
            detail="Team not found",
        )

    if not is_user_in_team(db, current_user, team):
        raise HTTPException(
            status_code=403,
            detail=f"You don't have access to team {team.name}",
        )

    user = get_user(db, new_team.user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if is_user_in_team(db, user, team):
        raise HTTPException(
            status_code=409,
            detail=f"User {user.username} already belongs to this team",
        )

    if user.team_id is not None:
        raise HTTPException(
            status_code=409,
            detail=f"User {user.username} already belongs to another team",
        )

    user.team_id = team.id

    db.commit()
    db.refresh(user)

    return user


@router.delete("/{team_id}/users/{user_id}", status_code=status.HTTP_202_ACCEPTED)
def del_user_from_team(
    team_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    team = get_team(db, team_id)

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    if not is_user_in_team(db, current_user, team):
        raise HTTPException(
            status_code=403,
            detail=f"the user {current_user.username} does not belong to {team.name}",
        )

    user = get_user(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not is_user_in_team(db, user, team):
        raise HTTPException(
            status_code=404,
            detail=f"The user {user.username} does not belong to {team.name}",
        )

    user.team_id = None
    db.commit()
    return {"message": "User removed from team successfully"}
