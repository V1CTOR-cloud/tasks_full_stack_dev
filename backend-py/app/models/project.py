import enum
from app.database import Base
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, Text, text, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.team import Team
    from app.models.task import Task


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
        secondary="project_teams", back_populates="projects"
    )

    tasks: Mapped[list["Task"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
