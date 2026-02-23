from datetime import date, datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from bot.handlers.constants import BowelMovementCallbackKey
from database.models.bowel_movement import BowelMovement
from database.repository.bowel_movements import BowelMovementRepository


class BowelMovementService:
    def __init__(self, bowel_movement_repository: BowelMovementRepository):
        self.bowel_movement_repository = bowel_movement_repository


    async def create_bowel_movement(
            self,
            session: AsyncSession,
            user_id: int,
            movement_date: Optional[date] = None,
            movement_time: Optional[datetime] = None,
            notes: Optional[str] = None,
            stool_consistency: Optional[int] = None
    ) -> BowelMovement:
        """Create new bowel movement for user"""
        return await self.bowel_movement_repository.create_bowel_movement(
            session=session,
            user_id=user_id,
            movement_date=movement_date,
            movement_time=movement_time,
            notes=notes,
            stool_consistency=stool_consistency
        )


    async def update_bowel_movement(
            self,
            session: AsyncSession,
            bowel_movement_id: int,
            notes: Optional[str] = None,
            stool_consistency: Optional[int] = None,
            blood_lvl: Optional[int] = None,
            mucus: Optional[int] = None
    ) -> Optional[BowelMovement]:
        return await self.bowel_movement_repository.update_bowel_movement(
            session=session,
            movement_id=bowel_movement_id,
            notes=notes,
            stool_consistency=stool_consistency,
            blood_lvl=blood_lvl,
            mucus=mucus,
        )


    async def get_bowel_movement_by_id(
            self,
            session: AsyncSession,
            bowel_movement_id: int
    ) -> Optional[BowelMovement]:
        return await self.bowel_movement_repository.get_bowel_movement_by_id(
            session=session,
            id=bowel_movement_id,
        )


    async def delete_bowel_movement(self, session: AsyncSession, bowel_movement_id: int) -> bool:
        return await self.bowel_movement_repository.delete_bowel_movement(session, bowel_movement_id)

    @staticmethod
    def parse_optional_int(callback_data: str) -> int | None:
        try:
            val = callback_data.split(":", 1)[1]
            return None if val == BowelMovementCallbackKey.SKIP else int(val)
        except (ValueError, IndexError):
            return None
