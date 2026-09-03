from sqlalchemy.orm import Session
from app.models.color import Color


def get_color(db: Session, color: str) -> Color | None:
    return db.query(Color).filter(Color.color == color).first()
