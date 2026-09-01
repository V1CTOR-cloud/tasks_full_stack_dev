from app.database import Base
from datetime import datetime
import enum
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, String, Text, text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.project import Project


class TaskPriority(enum.Enum):
    Low = "Low"
    Medium = "Medium"
    High = "High"


class TaskStatus(enum.Enum):
    todo = "todo"
    current = "current"
    done = "done"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, name="task_status"), nullable=False, default=TaskStatus.todo
    )
    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority, name="task_priority"),
        nullable=False,
        default=TaskPriority.Low,
    )
    due_date: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP + INTERVAL '14 days'")
    )

    user: Mapped["User | None"] = relationship(back_populates="tasks")

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )

    project: Mapped["Project"] = relationship(back_populates="tasks")
