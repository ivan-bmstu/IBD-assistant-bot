from sqlalchemy import (
    BigInteger, Column, DateTime, Integer, String
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.models import Base


class User(Base):
    """Bot user model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)
    language_code = Column(String(10), default="ru")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    timezone_offset = Column(Integer, nullable=True, server_default="0")

    # Relationships
    bowel_movements = relationship("BowelMovement", back_populates="user", cascade="all, delete-orphan")
