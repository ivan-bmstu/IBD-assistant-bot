from sqlalchemy.orm import declarative_base

Base = declarative_base()

from .user import User  # noqa: E402,F401
from .bowel_movement import BowelMovement  # noqa: E402,F401
