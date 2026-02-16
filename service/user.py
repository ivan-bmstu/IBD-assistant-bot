from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from database.repository.user import UserRepository


class UserService:

    @staticmethod
    async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID"""
        return await UserRepository.get_user_by_telegram_id(session, telegram_id)

    @staticmethod
    async def create_user(
            session: AsyncSession,
            telegram_id: int,
            language_code: str = 'ru',
            timezone_offset: int | None = None
    ) -> User:
        """Create new user without storing personal info"""
        if timezone_offset is None:
            timezone_offset = 0
        return await UserRepository.create_user(session, telegram_id, language_code, timezone_offset)

    @staticmethod
    async def get_or_create_user(
            session: AsyncSession,
            telegram_id: int,
            language_code: str = 'ru',
            timezone_offset: int | None = None
    ) -> User:
       """Get existing user or create new one"""
       user_opt: Optional[User] = await UserService.get_user_by_telegram_id(session, telegram_id)
       if user_opt is None:
           return await UserService.create_user(session, telegram_id, language_code, timezone_offset)
       return user_opt

    @staticmethod
    async def set_user_hour_timezone(session: AsyncSession, telegram_id: int, timezone_offset: int):
        user = await UserService.get_user_by_telegram_id(session, telegram_id)
        timezone_offset = timezone_offset * 60
        user.timezone_offset = timezone_offset
        return await UserRepository.update_user(session, user)

    @staticmethod
    async def set_user_minute_timezone(session: AsyncSession, telegram_id: int, timezone_minutes: int) -> User:
        user = await UserService.get_user_by_telegram_id(session, telegram_id)
        timezone_hours: int = user.timezone_offset
        offset = timezone_hours + (timezone_minutes if timezone_hours >= 0 else -timezone_minutes)
        if timezone_hours != offset:
            user.timezone_offset = offset
            return await UserRepository.update_user(session, user)
        return user
