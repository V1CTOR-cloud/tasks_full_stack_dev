from sqlalchemy.orm import Session

from app.models.team import Team
from app.models.user import User


def get_team(db: Session, team_id: int) -> Team | None:
    return db.query(Team).filter(Team.id == team_id).first()


def is_user_in_team(db: Session, user: User, team: Team) -> bool:
    return (
        db.query(User).filter(User.id == user.id, User.team_id == team.id).first()
        is not None
    )
