from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskResponse, TaskCreate, TaskUpdate
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/", response_model=list[TaskResponse], status_code=status.HTTP_200_OK)
def get_all(db: Session = Depends(get_db)):
    return db.query(Task).all()


@router.get(
    "/user/{user_id}", response_model=list[TaskResponse], status_code=status.HTTP_200_OK
)
def get_by_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(Task).filter(Task.user_id == user_id).all()


@router.get("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
def get_one(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@router.post("/", status_code=status.HTTP_201_CREATED)
def add_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_task = Task(
        user_id=current_user.id,
        title=task.title,
        description=task.description,
        status=task.status,
        due_date=task.due_date
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return {"message": "Task registered successfully"}


@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
def del_task(
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

    db.delete(existing_task)
    db.commit()

    return {"message": "Task deleted successfully"}


@router.patch("/{task_id}", status_code=status.HTTP_202_ACCEPTED)
def patch_task(
    task_id: int,
    task: TaskUpdate,
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

    update_data = task.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(existing_task, key, value)

    db.commit()
    db.refresh(existing_task)

    return {"message": "Task updated successfully", "Task": existing_task}
