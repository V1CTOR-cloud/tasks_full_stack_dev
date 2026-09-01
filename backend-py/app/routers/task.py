from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.crud.task import user_has_task_access, get_task, user_can_be_assigned_to_task
from app.crud.project import get_project, user_has_project_access
from app.crud.comment import get_comments_by_task, is_owner

from app.models.task import Task
from app.models.user import User
from app.models.project import Project
from app.models.comment import Comment
from app.models.team import Team

from app.schemas.task import TaskResponse, TaskCreate, TaskUpdate
from app.schemas.comment import CommentCreate, CommentResponse
from app.schemas.user import UserResponse

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get(
    "/user/{user_id}", response_model=list[TaskResponse], status_code=status.HTTP_200_OK
)
def get_by_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(Task).filter(Task.user_id == user_id).all()


@router.get("/", response_model=list[TaskResponse], status_code=status.HTTP_200_OK)
def get_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tasks = (
        db.query(Task)
        .join(Task.project)
        .filter(
            Task.project.has(Project.teams.any(id=current_user.team_id))
            | Task.project.has(Project.owner_id == current_user.id)
        )
        .all()
    )

    return tasks


@router.get(
    "/{task_id}/assignees",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
)
def get_assignees(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = get_task(db, task_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    if not user_has_task_access(db, current_user, task):
        raise HTTPException(
            status_code=403,
            detail="You don't have access to this task",
        )

    return (
        db.query(User)
        .join(User.team)
        .join(Team.projects)
        .filter(Project.id == task.project_id)
        .distinct()
        .all()
    )


@router.get("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
def get_task_by_id(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = get_task(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if not user_has_task_access(db, current_user, task):
        raise HTTPException(
            status_code=403, detail="You don't have access to this task"
        )

    return task


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
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

    return new_task


@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = get_task(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if not user_has_task_access(db, current_user, task):
        raise HTTPException(
            status_code=403, detail="You don't have access to this task"
        )

    db.delete(task)
    db.commit()

    return {"message": "Task deleted successfully"}


@router.patch("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = get_task(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if not user_has_task_access(db, current_user, task):
        raise HTTPException(
            status_code=403, detail="You don't have access to this task"
        )

    update_data = task_update.model_dump(exclude_unset=True)

    if "user_id" in update_data:
        user_id = update_data["user_id"]

        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not user_can_be_assigned_to_task(db, user, task):
            raise HTTPException(
                status_code=403, detail="This user cannot be assigned to this task"
            )

    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    return task


# Task - Comments


@router.get("/{task_id}/comments")
def get_task_comments(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = get_task(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if not user_has_task_access(db, current_user, task):
        raise HTTPException(
            status_code=403, detail="You don't have access to this task"
        )

    return get_comments_by_task(db, task_id)


@router.post(
    "/{task_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    task_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = get_task(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if not user_has_task_access(db, current_user, task):
        raise HTTPException(
            status_code=403, detail="You don't have access to this task"
        )

    new_comment = Comment(
        comment=comment.comment, author_id=current_user.id, task_id=task.id
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment


@router.patch(
    "/{task_id}/comments/{comment_id}",
    response_model=CommentResponse,
    status_code=status.HTTP_200_OK,
)
def update_comment(
    task_id: int,
    comment_id: int,
    comment_update: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = get_task(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if not user_has_task_access(db, current_user, task):
        raise HTTPException(
            status_code=403, detail="You don't have access to this task"
        )

    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id, Comment.task_id == task_id)
        .first()
    )

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if not is_owner(current_user, comment):
        raise HTTPException(
            status_code=403, detail="You can only delete your own comments"
        )

    comment.comment = comment_update.comment

    db.commit()
    db.refresh(comment)

    return comment


@router.delete("/{task_id}/comments/{comment_id}", status_code=status.HTTP_200_OK)
def delete_comment(
    task_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = get_task(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if not user_has_task_access(db, current_user, task):
        raise HTTPException(
            status_code=403, detail="You don't have access to this task"
        )

    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id, Comment.task_id == task_id)
        .first()
    )

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if not is_owner(current_user, comment):
        raise HTTPException(
            status_code=403, detail="You can only delete your own comments"
        )

    db.delete(comment)
    db.commit()

    return {"message": "Comment deleted successfully", "comment": comment}
