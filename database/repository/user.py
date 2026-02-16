from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.user import User


class UserRepository:

    @staticmethod
    async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID"""
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(
            session: AsyncSession,
            telegram_id: int,
            language_code: str = "ru",
            timezone_offset: int = 0,
    ) -> User:
        """Create new user without storing personal info"""
        user = User(
            telegram_id=telegram_id,
            language_code=language_code,
            timezone_offset=timezone_offset
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def update_user(session: AsyncSession, user: User) -> User:
        session.add(user)
        await session.commit()
        return user