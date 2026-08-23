from app.models.team import Team
from app.models.user import User

def is_user_in_team(user: User, team: Team) -> bool:
    return user.team_id == team.id