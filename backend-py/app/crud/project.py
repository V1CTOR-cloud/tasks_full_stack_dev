from sqlalchemy.orm import Session
from app.models.project import Project
from app.models.user import User
from app.models.team import Team


def get_project(db: Session, project_id: int) -> Project | None:
    return db.query(Project).filter(Project.id == project_id).first()


def user_has_project_access(db: Session, user: User, project: Project) -> bool:

    if project.owner_id == user.id:
        return True

    if user.team_id is None:
        return False

    return any(team.id == user.team_id for team in project.teams)
