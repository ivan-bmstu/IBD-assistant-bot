from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from bot.handlers.constants import BowelMovementMessageCommand, MainMessageCommand, MainCallbackKey


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Get main menu keyboard"""
    builder = ReplyKeyboardBuilder()

    # Recording button
    builder.add(KeyboardButton(text=BowelMovementMessageCommand.START_BOWEL_MOVEMENT.value))

    # User settings button
    builder.add(KeyboardButton(text=MainMessageCommand.USER_SETTINGS.value))

    # Help button
    builder.add(KeyboardButton(text=MainMessageCommand.HELP.value))

    builder.adjust(1, 1)
    return builder.as_markup(resize_keyboard=True)


def get_timezone_hour_keyboard() -> InlineKeyboardMarkup:
    """Timezone selection keyboard: UTC-12..UTC+12"""
    builder = InlineKeyboardBuilder()

    for offset in range(-12, 13):
        sign = "+" if offset >= 0 else "-"
        label = f"UTC{sign}{abs(offset):02d}:00"
        builder.add(InlineKeyboardButton(text=label, callback_data=f"{MainCallbackKey.SET_HOUR_TIMEZONE}:{offset}"))

    builder.add(InlineKeyboardButton(
        text="Пропустить (оставить текущую)",
        callback_data=f"{MainCallbackKey.SET_HOUR_TIMEZONE}:{MainCallbackKey.SKIP}"
    ))
    builder.adjust(3, 3, 3, 3, 3, 3, 3, 1)
    return builder.as_markup()


def get_timezone_minutes_keyboard() -> InlineKeyboardMarkup:
    """Timezone minutes selection keyboard"""
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text=":00", callback_data=f"{MainCallbackKey.SET_MINUTE_TIMEZONE}:0"))
    builder.add(InlineKeyboardButton(text=":15", callback_data=f"{MainCallbackKey.SET_MINUTE_TIMEZONE}:15"))
    builder.add(InlineKeyboardButton(text=":30", callback_data=f"{MainCallbackKey.SET_MINUTE_TIMEZONE}:30"))
    builder.add(InlineKeyboardButton(text=":45", callback_data=f"{MainCallbackKey.SET_MINUTE_TIMEZONE}:45"))
    builder.add(InlineKeyboardButton(
        text="Пропустить (оставить текущую)",
        callback_data=f"{MainCallbackKey.SET_MINUTE_TIMEZONE}:{MainCallbackKey.SKIP}")
    )

    builder.adjust(3, 1)
    return builder.as_markup()

def get_settings_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🕒 Часовой пояс", callback_data=MainCallbackKey.SETTINGS_TIMEZONE)]
        ]
    )
