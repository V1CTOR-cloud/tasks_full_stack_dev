from app.database import Base
from sqlalchemy import DateTime, String, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from datetime import datetime
from app.models.project_teams import ProjectTeams

if TYPE_CHECKING:
    from app.models.color import Color
    from app.models.project import Project
    from app.models.user import User


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    hex_color: Mapped[str | None] = mapped_column(
        ForeignKey("colors.color"), unique=True
    )

    color: Mapped["Color | None"] = relationship(back_populates="teams")

    users: Mapped[list["User"]] = relationship(back_populates="team")

    projects: Mapped[list["Project"]] = relationship(
        secondary=ProjectTeams.__table__, back_populates="teams"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
