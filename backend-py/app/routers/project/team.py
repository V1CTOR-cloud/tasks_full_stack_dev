from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.crud.project import get_project, user_has_project_access
from app.crud.team import is_user_in_team, get_team

from app.models.user import User
from app.models.project import Project
from app.models.team import Team

from app.schemas.team import AddTeamToProject, TeamCreate, TeamResponse

router = APIRouter(prefix="/projects", tags=["Project Teams"])


@router.get("/{project_id}/teams", status_code=status.HTTP_202_ACCEPTED)
def get_project_teams(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing_project = get_project(db, project_id)

    if not existing_project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not user_has_project_access(db, current_user, existing_project):
        raise HTTPException(
            status_code=403, detail="You don't have access to this project"
        )

    return existing_project.teams


@router.post("/{project_id}/teams/{team_id}", status_code=status.HTTP_202_ACCEPTED)
def add_team_to_project(
    project_id: int,
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing_project = get_project(db, project_id)

    if not existing_project:
        raise HTTPException(status_code=404, detail="Project not found")

    if existing_project.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Only the project owner can manage teams"
        )

    existing_team = db.query(Team).filter(Team.id == team_id).first()

    if not existing_team:
        raise HTTPException(status_code=404, detail="Team not found")

    if existing_team in existing_project.teams:
        raise HTTPException(
            status_code=409, detail="Team is already assigned to this project"
        )

    existing_project.teams.append(existing_team)

    db.commit()
    db.refresh(existing_project)

    return existing_project


@router.delete("/{project_id}/teams/{team_id}", status_code=status.HTTP_202_ACCEPTED)
def del_team_from_project(
    project_id: int,
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing_project = get_project(db, project_id)

    if not existing_project:
        raise HTTPException(status_code=404, detail="Project not found")

    if existing_project.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Only the project owner can manage teams"
        )

    existing_team = db.query(Team).filter(Team.id == team_id).first()

    if not existing_team:
        raise HTTPException(status_code=404, detail="Team not found")

    if not existing_team in existing_project.teams:
        raise HTTPException(
            status_code=409, detail="This Team is not assigned to this project"
        )

    existing_project.teams.remove(existing_team)

    db.commit()
    db.refresh(existing_project)

    return existing_project
