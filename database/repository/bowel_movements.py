from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.bowel_movement import BowelMovement


class BowelMovementRepository:
    # Bowel Movement operations
    async def get_bowel_movements_by_user(
            self,
            session: AsyncSession,
            user_id: int,
            start_date: Optional[date] = None,
            end_date: Optional[date] = None,
            limit: int = 100
    ) -> List[BowelMovement]:
        """Get bowel movements for user within date range"""
        query = select(BowelMovement).where(BowelMovement.user_id == user_id)

        if start_date:
            query = query.where(BowelMovement.date >= start_date)
        if end_date:
            query = query.where(BowelMovement.date <= end_date)

        query = query.order_by(BowelMovement.date.desc(), BowelMovement.time.desc()).limit(limit)

        result = await session.execute(query)
        return list(result.scalars().all())


    async def create_bowel_movement(
            self,
            session: AsyncSession,
            user_id: int,
            movement_date: Optional[date] = None,
            movement_time: Optional[datetime] = None,
            notes: Optional[str] = None,
            stool_consistency: Optional[int] = None
    ) -> BowelMovement:
        """Create a new bowel movement record (fact of going to the toilet)"""

        bowel_movement = BowelMovement(
            user_id=user_id,
            date=movement_date,
            time=movement_time,
            notes=notes,
            stool_consistency=stool_consistency,

        )
        session.add(bowel_movement)
        await session.commit()
        await session.refresh(bowel_movement)
        return bowel_movement


    async def update_bowel_movement(
            self,
            session: AsyncSession,
            movement_id: int,
            notes: Optional[str] = None,
            stool_consistency: Optional[int] = None,
            blood_lvl: Optional[int] = None,
            mucus: Optional[int] = None,
            is_false_urge: Optional[bool] = None,
    ) -> Optional[BowelMovement]:
        """Update bowel movement fields if provided."""
        result = await session.execute(
            select(BowelMovement).where(BowelMovement.id == movement_id)
        )
        bowel_movement = result.scalar_one_or_none()
        if bowel_movement is None:
            return None

        if notes is not None:
            bowel_movement.notes = notes
        if stool_consistency is not None:
            bowel_movement.stool_consistency = stool_consistency
        if blood_lvl is not None:
            bowel_movement.blood_lvl = blood_lvl
        if mucus is not None:
            bowel_movement.mucus = mucus
        if is_false_urge is not None:
            bowel_movement.is_false_urge = is_false_urge

        await session.commit()
        await session.refresh(bowel_movement)
        return bowel_movement


    async def delete_bowel_movement(self, session: AsyncSession, bowel_movement_id: int) -> bool:
        """Delete bowel movement by ID"""
        result = await session.execute(
            delete(BowelMovement).where(BowelMovement.id == bowel_movement_id)
        )
        await session.commit()
        return result.rowcount == 1


    async def get_bowel_movement_by_id(
            self,
            session: AsyncSession,
            id: int,
    ) -> BowelMovement:
        """Get bowel movement by ID"""
        query = select(BowelMovement).where(BowelMovement.id == id)

        result: BowelMovement = await session.scalar(query)
        return result
