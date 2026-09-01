from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.crud.project import get_project, user_has_project_access

from app.models.user import User
from app.models.task import Task

from app.schemas.task import TaskCreate, TaskResponse

router = APIRouter(prefix="/projects", tags=["Project Tasks"])


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
