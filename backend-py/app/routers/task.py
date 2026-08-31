from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.crud.task import user_has_task_access
from app.crud.project import get_project, user_has_project_access

from app.models.task import Task
from app.models.user import User
from app.models.project import Project
from app.schemas.task import TaskResponse, TaskCreate, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/", response_model=list[TaskResponse], status_code=status.HTTP_200_OK)
def get_all(db: Session = Depends(get_db)):
    return db.query(Task).all()


@router.get(
    "/user/{user_id}", response_model=list[TaskResponse], status_code=status.HTTP_200_OK
)
def get_by_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(Task).filter(Task.user_id == user_id).all()


@router.get("/", response_model=list[TaskResponse])
def get_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tasks = (
        db.query(Task)
        .join(Task.project)
        .filter(
            Task.project.has(Project.teams.any(id=current_user.team_id))
            | (Task.project.has(Project.owner_id == current_user.id))
        )
        .all()
    )

    return tasks


@router.get("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
def get_task_by_id(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing_task = (
        db.query(Task)
        .filter(Task.id == task_id, Task.user_id == current_user.id)
        .first()
    )

    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")

    if not user_has_task_access(db, current_user, existing_task):
        raise HTTPException(
            status_code=404, detail="You don't have access to this task"
        )

    return existing_task


@router.post("/", status_code=status.HTTP_201_CREATED)
def add_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = get_project(db, task.project_id)

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

    return {"message": "Task registered successfully", "task": task}


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    project = get_project(db, task.project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not user_has_project_access(db, current_user, project):
        raise HTTPException(
            status_code=403, detail="You don't have access to this task"
        )

    db.delete(task)
    db.commit()
    
    return {"message": "Task deleted successfully"}


@router.patch(
    "/{task_id}", response_model=TaskResponse, status_code=status.HTTP_202_ACCEPTED
)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    project = get_project(db, task.project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not user_has_project_access(db, current_user, project):
        raise HTTPException(
            status_code=403, detail="You don't have access to this task"
        )

    update_data = task_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    return task
