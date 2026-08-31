from sqlalchemy.orm import Session
from app.models.user import User
from app.models.task import Task
from app.crud.project import user_has_project_access





def user_has_task_access(db: Session, user: User, task: Task) -> bool:
    return user_has_project_access(db, user, task.project)
