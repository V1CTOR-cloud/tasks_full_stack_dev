from app.database import Base
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.color import Color
    from app.models.user import User

class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True
    )

    hex_color: Mapped[str | None] = mapped_column(
        ForeignKey("colors.color"),
        unique=True
    )

    color: Mapped["Color | None"] = relationship(
        back_populates="teams"
    )
    
    users: Mapped[list["User"]] = relationship(
        back_populates="team"
    )
    
    