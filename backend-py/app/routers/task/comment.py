from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user

from app.crud.task import get_task, user_has_task_access
from app.crud.comment import get_comments_by_task, is_owner

from app.models.user import User
from app.models.comment import Comment

from app.schemas.comment import CommentCreate, CommentResponse

router = APIRouter(prefix="/tasks", tags=["Task Comments"])


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
            status_code=403, detail="You can only update your own comments"
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

    return {"message": "Comment deleted successfully"}
