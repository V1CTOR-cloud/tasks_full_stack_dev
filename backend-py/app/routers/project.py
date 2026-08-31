from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.crud.project import get_project, user_has_project_access

from app.models.project import Project
from app.models.user import User
from app.models.team import Team
from app.models.task import Task

from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.schemas.task import TaskCreate, TaskResponse

router = APIRouter(prefix="/projects", tags=["Projects"])


from sqlalchemy import or_


@router.get("/", response_model=list[ProjectResponse], status_code=status.HTTP_200_OK)
def get_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    projects = (
        db.query(Project)
        .filter(
            or_(
                Project.owner_id == current_user.id,
                Project.teams.any(id=current_user.team_id),
            )
        )
        .all()
    )

    return projects


@router.get(
    "/{project_id}", response_model=ProjectResponse, status_code=status.HTTP_200_OK
)
def get_project_by_id(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = get_project(db, project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not user_has_project_access(db, current_user, project):
        raise HTTPException(
            status_code=403, detail="You don't have access to this project"
        )

    return project


@router.post("/", status_code=status.HTTP_201_CREATED)
def add_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing_project = db.query(Project).filter(Project.title == project.title).first()

    if existing_project:
        raise HTTPException(
            status_code=409,
            detail=f"{project.title} already exists",
        )

    new_project = Project(
        title=project.title,
        description=project.description,
        status=project.status,
        owner_id=current_user.id,
    )

    if current_user.team:
        new_project.teams.append(current_user.team)

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return new_project


@router.patch("/{project_id}", status_code=status.HTTP_202_ACCEPTED)
def patch_project(
    project_id: int,
    project: ProjectUpdate,
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

    update_data = project.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(existing_project, key, value)

    db.commit()
    db.refresh(existing_project)

    return {"message": "Project updated successfully", "Project": existing_project}


@router.delete("/{project_id}", status_code=status.HTTP_202_ACCEPTED)
def del_project(
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

    db.delete(existing_project)
    db.commit()

    return {"message": "Project deleted successfully"}


# Project - Teams
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


# Project - Tasks


@router.get("/{project_id}/tasks", status_code=status.HTTP_202_ACCEPTED)
def get_project_tasks(
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

    return existing_project.tasks


@router.post(
    "/{project_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_task_to_project(
    project_id: int,
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = get_project(db, project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not user_has_project_access(db, current_user, project):
        raise HTTPException(
            status_code=403, detail="You don't have access to this project"
        )

    new_task = Task(
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        due_date=task.due_date,
        project_id=project.id,
        user_id=current_user.id,
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


@router.delete("/{project_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_from_project(
    project_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = get_project(db, project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not user_has_project_access(db, current_user, project):
        raise HTTPException(
            status_code=403, detail="You don't have access to this project"
        )

    task = (
        db.query(Task).filter(Task.id == task_id, Task.project_id == project_id).first()
    )

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()

    return {"message", "Task deleted successfully"}
