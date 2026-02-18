from datetime import date, datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from bot.handlers.constants import BowelMovementCallbackKey
from database.models.bowel_movement import BowelMovement
from database.repository.bowel_movements import BowelMovementRepository


class BowelMovementService:

    @staticmethod
    async def create_bowel_movement(
            session: AsyncSession,
            user_id: int,
            movement_date: Optional[date] = None,
            movement_time: Optional[datetime] = None,
            notes: Optional[str] = None,
            stool_consistency: Optional[int] = None
    ) -> BowelMovement:
        """Create new bowel movement for user"""
        return await BowelMovementRepository.create_bowel_movement(
            session=session,
            user_id=user_id,
            movement_date=movement_date,
            movement_time=movement_time,
            notes=notes,
            stool_consistency=stool_consistency
        )


    @staticmethod
    async def update_bowel_movement(
            session: AsyncSession,
            bowel_movement_id: int,
            notes: Optional[str] = None,
            stool_consistency: Optional[int] = None,
            blood_lvl: Optional[int] = None,
    ) -> Optional[BowelMovement]:
        return await BowelMovementRepository.update_bowel_movement(
            session=session,
            movement_id=bowel_movement_id,
            notes=notes,
            stool_consistency=stool_consistency,
            blood_lvl=blood_lvl,
        )


    @staticmethod
    async def get_bowel_movement_by_id(
            session: AsyncSession,
            bowel_movement_id: int
    ) -> Optional[BowelMovement]:
        return await BowelMovementRepository.get_bowel_movement_by_id(
            session=session,
            id=bowel_movement_id,
        )

    @staticmethod
    def get_stool_consistency_data(callback_data: str) -> int | None:
        """Parse stool consistency callback data"""
        stool_consistency_str = callback_data.split(':')[1]
        if stool_consistency_str == BowelMovementCallbackKey.SKIP:
            stool_consistency_val = None
        else:
            stool_consistency_val = int(stool_consistency_str)
        return stool_consistency_val

    @staticmethod
    def get_stool_blood_data(callback_data: str) -> int | None:
        """Parse stool blood callback data"""
        val: str = callback_data.split(':')[1]
        if val == BowelMovementCallbackKey.SKIP:
            return None
        return int(val)
