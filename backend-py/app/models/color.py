from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.team import Team


class Color(Base):
    __tablename__ = "colors"

    color: Mapped[str] = mapped_column(primary_key=True)

    teams: Mapped[list["Team"]] = relationship(
        back_populates="color"
    )