from datetime import datetime
import enum
from sqlalchemy import DateTime, ForeignKey, String, Text, text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User


class TaskStatus(enum.Enum):
    todo = "todo"
    current = "current"
    done = "done"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, name="task_status"), nullable=False, default=TaskStatus.todo
    )
    due_date: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP + INTERVAL '14 days'")
    )

    user: Mapped["User"] = relationship(back_populates="tasks")
