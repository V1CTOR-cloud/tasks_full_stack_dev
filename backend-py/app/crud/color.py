from sqlalchemy.orm import Session
from app.models.color import Color


def find_color(db: Session, color: str | None) -> Color | None:
    return db.query(Color).filter(Color.color == color).first()

