from app.database import Base

from sqlalchemy import DateTime, String, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.task import Task
    from app.models.team import Team
    from app.models.project import Project


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    password: Mapped[str] = mapped_column(String(255), nullable=False)

    team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"))

    tasks: Mapped[list["Task"]] = relationship(back_populates="user")

    team: Mapped["Team | None"] = relationship(back_populates="users")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    projects: Mapped[list["Project"]] = relationship(back_populates="owner")
