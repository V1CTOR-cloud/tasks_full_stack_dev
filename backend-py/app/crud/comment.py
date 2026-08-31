from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.models.user import User


def get_comment(db: Session, comment_id: int) -> Comment | None:
    return db.query(Comment).filter(Comment.id == comment_id).first()


def get_comments_by_task(db: Session, task_id: int) -> list[Comment]:
    return db.query(Comment).filter(Comment.task_id == task_id).all()


def is_owner(user: User, comment: Comment) -> bool:
    return user == comment.author