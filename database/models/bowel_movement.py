from datetime import date

from sqlalchemy import (
    Column, Date, DateTime, ForeignKey,
    Integer, Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.models import Base


class BowelMovement(Base):
    """Record of bowel movement"""
    __tablename__ = "bowel_movements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.telegram_id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, default=date.today, nullable=False, index=True)
    time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Additional notes
    notes = Column(Text, nullable=True)
    stool_consistency = Column(Integer, nullable=True)
    blood_lvl = Column(Integer, nullable=True)
    mucus = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="bowel_movements")


from enum import IntEnum


class StoolConsistency(IntEnum):
    LIQUID = 1
    MUSHY = 2
    NORMAL = 3
    HARD = 4

    @property
    def label(self) -> str:
        return {
            StoolConsistency.LIQUID:    "Жидкий",
            StoolConsistency.MUSHY:     "Кашицеобразный",
            StoolConsistency.NORMAL:    "Нормальный",
            StoolConsistency.HARD:      "Твёрдый",
        }[self]


class StoolBlood(IntEnum):
    NOT_PRESENT = 0
    TRACE = 1
    MILD = 2
    MODERATE = 3
    SEVERE = 4

    @property
    def label(self) -> str:
        return {
            StoolBlood.NOT_PRESENT:     "❎ Отсутствует",
            StoolBlood.TRACE:           "🩸 Следы",
            StoolBlood.MILD:            "🩸🩸 Умеренно",
            StoolBlood.MODERATE:        "🩸🩸🩸 Выражено",
            StoolBlood.SEVERE:          "🩸🩸🩸🩸 Резко выражено",
        }[self]


class Mucus(IntEnum):
    NOT_PRESENT = 0
    PRESENT = 1

    @property
    def label(self) -> str:
        return {
            Mucus.NOT_PRESENT:  "❎ Отсутствует",
            Mucus.PRESENT:      "🟢 Присутствует",
        }[self]

