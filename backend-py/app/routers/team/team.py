from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user

from app.crud.color import find_color
from app.crud.team import is_user_in_team

from app.models.team import Team
from app.models.user import User

from app.schemas.team import TeamCreate, TeamUpdate, TeamResponse

router = APIRouter(prefix="/teams", tags=["Teams"])


@router.get(
    "/",
    response_model=list[TeamResponse],
    status_code=status.HTTP_200_OK,
)
def get_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Team).filter(Team.id == current_user.team_id).all()


@router.get(
    "/my-team",
    response_model=TeamResponse,
    status_code=status.HTTP_200_OK,
)
def get_my_team(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.team_id is None:
        raise HTTPException(
            status_code=404,
            detail="User does not belong to any team",
        )

    team = db.query(Team).filter(Team.id == current_user.team_id).first()

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    return team


@router.post("/", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def add_team(
    team: TeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    color = find_color(db, team.hex_color)

    if not color:
        raise HTTPException(status_code=404, detail="Color not found")

    existing_team = db.query(Team).filter(Team.name == team.name).first()

    if existing_team:
        raise HTTPException(status_code=409, detail=f"{team.name} already exists")

    existing_color_team = (
        db.query(Team).filter(Team.hex_color == team.hex_color).first()
    )

    if existing_color_team:
        raise HTTPException(
            status_code=409,
            detail=f"The color #{team.hex_color} is already being used by another team",
        )

    new_team = Team(name=team.name, color=color)

    db.add(new_team)
    db.flush()

    current_user.team_id = new_team.id

    db.commit()
    db.refresh(new_team)

    return new_team


@router.patch("/{team_id}", response_model=TeamResponse, status_code=status.HTTP_200_OK)
def patch_team(
    team_id: int,
    team: TeamUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    color = find_color(db, team.hex_color)

    if not color:
        raise HTTPException(status_code=404, detail="Color not found")

    existing_team = db.query(Team).filter(Team.id == team_id).first()

    if not existing_team:
        raise HTTPException(status_code=404, detail="Team not found")

    if not is_user_in_team(db, current_user, existing_team):
        raise HTTPException(
            status_code=404,
            detail=f"the user {current_user.username} does not belong to {existing_team.name}",
        )

    existing_color_team = (
        db.query(Team)
        .filter(Team.hex_color == team.hex_color, Team.id != team_id)
        .first()
    )
    if existing_color_team:
        raise HTTPException(
            status_code=409,
            detail=f"The color #{team.hex_color} is already being used by another team",
        )

    update_data = team.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(existing_team, key, value)

    db.commit()
    db.refresh(existing_team)

    return existing_team


@router.delete("/{team_id}", status_code=status.HTTP_202_ACCEPTED)
def del_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing_team = db.query(Team).filter(Team.id == team_id).first()

    if not existing_team:
        raise HTTPException(status_code=404, detail="Team not found")

    if not is_user_in_team(db, current_user, existing_team):
        raise HTTPException(
            status_code=404,
            detail=f"the user {current_user.username} does not belong to {existing_team.name}",
        )

    db.delete(existing_team)
    db.commit()

    return {"message": "Team deleted successfully"}
