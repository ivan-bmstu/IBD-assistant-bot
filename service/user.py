from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from database.repository.user import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_user_by_telegram_id(self, session: AsyncSession, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID"""
        return await self.user_repository.get_user_by_telegram_id(session, telegram_id)

    async def create_user(
            self,
            session: AsyncSession,
            telegram_id: int,
            language_code: str = 'ru',
            timezone_offset: int | None = None
    ) -> User:
        """Create new user without storing personal info"""
        if timezone_offset is None:
            timezone_offset = 0
        return await self.user_repository.create_user(session, telegram_id, language_code, timezone_offset)

    async def get_or_create_user(
            self,
            session: AsyncSession,
            telegram_id: int,
            language_code: str = 'ru',
            timezone_offset: int | None = None
    ) -> User:
        """Get existing user or create new one"""
        user_opt: Optional[User] = await self.get_user_by_telegram_id(session, telegram_id)
        if user_opt is None:
            return await self.create_user(session, telegram_id, language_code, timezone_offset)
        return user_opt

    async def set_user_hour_timezone(self, session: AsyncSession, telegram_id: int, timezone_offset: int) -> User | None:
        user = await self.get_user_by_telegram_id(session, telegram_id)
        if user is None:
            return None
        timezone_offset = timezone_offset * 60
        user.timezone_offset = timezone_offset
        return await self.user_repository.update_user(session, user)

    async def set_user_minute_timezone(self, session: AsyncSession, telegram_id: int,
                                       timezone_minutes: int) -> User | None:
        user = await self.get_user_by_telegram_id(session, telegram_id)
        if user is None:
            return None
        timezone_hours: int = user.timezone_offset
        offset = timezone_hours + (timezone_minutes if timezone_hours >= 0 else -timezone_minutes)
        if timezone_hours != offset:
            user.timezone_offset = offset
            return await self.user_repository.update_user(session, user)
        return user
