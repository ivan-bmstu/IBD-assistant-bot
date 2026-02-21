from aiogram.fsm.storage.base import StorageKey
from aiogram.types import Message, CallbackQuery


def format_timezone(offset_minutes: int | None) -> str:
    if offset_minutes is None:
        return "не задана"

    sign = "+" if offset_minutes >= 0 else "-"
    total = abs(offset_minutes)
    hours = total // 60
    minutes = total % 60
    return f"UTC{sign}{hours:02d}:{minutes:02d}"


def build_fsm_key_from_message(message: Message, destiny: str = "default") -> StorageKey:
    return StorageKey(
        bot_id=message.bot.id,
        chat_id=message.chat.id,
        user_id=message.from_user.id,
        destiny=destiny,
    )


def build_fsm_key_from_callback(callback: CallbackQuery, destiny: str = "default") -> StorageKey:
    return StorageKey(
        bot_id=callback.bot.id,
        chat_id=callback.message.chat.id,
        user_id=callback.from_user.id,
        destiny=destiny,
    )
