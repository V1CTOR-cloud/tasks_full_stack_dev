from sqlalchemy.orm import Session

from app.models.user import User
from app.models.task import Task
from app.models.project import Project

from app.crud.project import user_has_project_access


def get_task(db: Session, task_id: int) -> Task | None:
    return db.query(Task).filter(Task.id == task_id).first()


def user_has_task_access(db: Session, user: User, task: Task) -> bool:
    project = db.query(Project).filter(Project.id == task.project_id).first()

    if not project:
        return False

    return user_has_project_access(db, user, project)
