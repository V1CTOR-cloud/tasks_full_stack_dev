from app.database import Base
import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.project_teams import ProjectTeams

if TYPE_CHECKING:
    from app.models.team import Team
    from app.models.task import Task
    from app.models.user import User


class ProjectStatus(enum.Enum):
    Planning = "Planning"
    Development = "Development"
    Testing = "Testing"
    Production = "Production"
    Completed = "Completed"


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus, name="project_status"),
        nullable=False,
        default=ProjectStatus.Planning,
    )

    teams: Mapped[list["Team"]] = relationship(
        secondary=ProjectTeams.__table__, back_populates="projects"
    )

    tasks: Mapped[list["Task"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    owner: Mapped["User"] = relationship(back_populates="projects")
