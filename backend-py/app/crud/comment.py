from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.models.user import User


def get_comments_by_task(db: Session, task_id: int) -> list[Comment]:
    return db.query(Comment).filter(Comment.task_id == task_id).all()


def is_owner(user: User, comment: Comment) -> bool:
    return user == comment.author